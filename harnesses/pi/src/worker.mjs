import { createInterface } from "node:readline";
import { pathToFileURL } from "node:url";
import { resolve } from "node:path";

import { Agent } from "@earendil-works/pi-agent-core";
import { createAssistantMessageEventStream } from "@earendil-works/pi-ai";

const TERMINAL_MODEL_EVENTS = new Set(["done", "error"]);
const WORKER_PROTOCOL = "amesh.pi-worker/v1";
const WORKER_VERSION = "0.84.3";
const MAX_CONTROL_FRAME_BYTES = 1024 * 1024;

class AsyncQueue {
  #items = [];
  #waiters = [];
  #ended = false;

  push(item) {
    if (this.#ended) return;
    const waiter = this.#waiters.shift();
    if (waiter) waiter.resolve({ value: item, done: false });
    else this.#items.push(item);
  }

  end(error) {
    if (this.#ended) return;
    this.#ended = true;
    for (const waiter of this.#waiters.splice(0)) {
      if (error) waiter.reject(error);
      else waiter.resolve({ value: undefined, done: true });
    }
  }

  next() {
    if (this.#items.length) {
      return Promise.resolve({ value: this.#items.shift(), done: false });
    }
    if (this.#ended) return Promise.resolve({ value: undefined, done: true });
    return new Promise((resolve, reject) => this.#waiters.push({ resolve, reject }));
  }

  [Symbol.asyncIterator]() {
    return this;
  }
}

export class JsonlBridge {
  #input;
  #output;
  #commands = new AsyncQueue();
  #pending = new Map();
  #nextRequest = 1;
  #reader;
  #started = false;

  constructor({ input = process.stdin, output = process.stdout } = {}) {
    this.#input = input;
    this.#output = output;
  }

  start() {
    if (this.#started) return;
    this.#started = true;
    this.#reader = createInterface({ input: this.#input, crlfDelay: Infinity });
    void this.#readLines();
  }

  async #readLines() {
    try {
      for await (const line of this.#reader) {
        if (!line.trim()) continue;
        if (Buffer.byteLength(line, "utf8") + 1 > MAX_CONTROL_FRAME_BYTES) {
          throw new Error("AMESH control frame exceeded the configured limit");
        }
        const message = JSON.parse(line);
        const requestId = message.requestId;
        const pending = requestId ? this.#pending.get(requestId) : undefined;
        if (pending) {
          pending.handle(message);
        } else {
          this.#commands.push(message);
        }
      }
      const error = new Error("AMESH parent closed the JSONL bridge");
      for (const pending of this.#pending.values()) pending.fail(error);
      this.#pending.clear();
      this.#commands.end();
    } catch (error) {
      for (const pending of this.#pending.values()) pending.fail(error);
      this.#pending.clear();
      this.#commands.end(error);
    }
  }

  send(message) {
    this.#output.write(`${JSON.stringify(message)}\n`);
  }

  #allocateRequest(kind, payload, handle) {
    const requestId = `${kind}-${this.#nextRequest++}`;
    this.#pending.set(requestId, {
      handle: (message) => {
        handle(message, requestId);
      },
      fail: (error) => {
        handle({ type: "bridge.error", requestId, error: String(error.message ?? error) }, requestId);
      },
    });
    this.send({ ...payload, requestId });
    return requestId;
  }

  requestModel(payload, onEvent) {
    let requestId;
    requestId = this.#allocateRequest("model", {
      type: "model.request",
      protocol: WORKER_PROTOCOL,
      ...payload,
    }, (message) => {
      if (message.type === "bridge.error") {
        onEvent({ type: "error", reason: "error", error: assistantError(payload.model, message.error) });
        this.#pending.delete(requestId);
        return;
      }
      if (message.type !== "model.event" || message.requestId !== requestId) return;
      onEvent(message.event);
      if (TERMINAL_MODEL_EVENTS.has(message.event?.type)) this.#pending.delete(requestId);
    });
    return requestId;
  }

  requestTool(payload) {
    return new Promise((resolve, reject) => {
      let requestId;
      requestId = this.#allocateRequest("tool", {
        type: "tool.request",
        protocol: WORKER_PROTOCOL,
        ...payload,
      }, (message) => {
        if (message.type === "bridge.error") {
          this.#pending.delete(requestId);
          reject(new Error(message.error));
          return;
        }
        if (message.type !== "tool.result" || message.requestId !== requestId) return;
        this.#pending.delete(requestId);
        if (message.error) reject(new Error(String(message.error)));
        else resolve(message.result);
      });
    });
  }

  [Symbol.asyncIterator]() {
    this.start();
    return this.#commands;
  }
}

function assistantError(model, message) {
  return {
    role: "assistant",
    content: [{ type: "text", text: String(message) }],
    api: "amesh",
    provider: "amesh",
    model: model.id,
    usage: emptyUsage(),
    stopReason: "error",
    timestamp: Date.now(),
    errorMessage: String(message),
  };
}

function emptyUsage() {
  return { input: 0, output: 0, cacheRead: 0, cacheWrite: 0, totalTokens: 0 };
}

function normalizeModel(model = {}) {
  return {
    id: model.id ?? "amesh-model",
    name: model.name ?? model.id ?? "AMESH model",
    api: "amesh",
    provider: "amesh",
    baseUrl: model.baseUrl ?? "http://amesh.invalid",
    reasoning: Boolean(model.reasoning),
    input: model.input ?? ["text"],
    cost: model.cost ?? { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
    contextWindow: model.contextWindow ?? 128000,
    maxTokens: model.maxTokens ?? 8192,
  };
}

function jsonOptions(options = {}) {
  const allowed = ["temperature", "maxTokens", "topP", "topK", "reasoningEffort", "cacheRetention"];
  return Object.fromEntries(allowed.filter((key) => options[key] !== undefined).map((key) => [key, options[key]]));
}

function createStreamFn(bridge, run) {
  return async (model, context, options = {}) => {
    const stream = createAssistantMessageEventStream();
    bridge.requestModel(
      {
        runId: run.runId,
        sessionId: run.sessionId,
        model: { ...model, api: "amesh", provider: "amesh" },
        context,
        options: jsonOptions(options),
      },
      (event) => {
        stream.push(event);
        if (TERMINAL_MODEL_EVENTS.has(event.type)) stream.end();
      },
    );
    return stream;
  };
}

function makeTool(bridge, run, definition) {
  return {
    name: definition.name,
    label: definition.label ?? definition.name,
    description: definition.description ?? "",
    parameters: definition.parameters ?? { type: "object", properties: {}, additionalProperties: true },
    execute: async (toolCallId, params) => {
      const result = await bridge.requestTool({
        runId: run.runId,
        sessionId: run.sessionId,
        toolCallId,
        name: definition.name,
        arguments: params,
      });
      return result ?? { content: [{ type: "text", text: "AMESH parent returned no tool result." }], details: {} };
    },
  };
}

export async function runWorker({ input = process.stdin, output = process.stdout } = {}) {
  const bridge = new JsonlBridge({ input, output });
  let agent;
  let run;

  for await (const command of bridge) {
    if (command.type === "run.start") {
      if (command.protocol !== WORKER_PROTOCOL) {
        throw new Error("AMESH worker protocol mismatch");
      }
      if (agent) throw new Error("Only one active Pi run is supported by this minimal worker");
      run = {
        runId: command.runId ?? "run-1",
        sessionId: command.sessionId ?? "session-1",
      };
      const model = normalizeModel(command.model);
      const tools = (command.tools ?? []).map((definition) => makeTool(bridge, run, definition));
      agent = new Agent({
        initialState: {
          systemPrompt: command.systemPrompt,
          model,
          thinkingLevel: command.thinkingLevel ?? "off",
          tools,
          messages: command.messages ?? [],
        },
        streamFn: createStreamFn(bridge, run),
        sessionId: run.sessionId,
      });
      agent.subscribe((event) => {
        bridge.send({
          type: "agent.event",
          protocol: WORKER_PROTOCOL,
          runId: run.runId,
          event: { type: event.type },
        });
        if (event.type === "agent_end") {
          bridge.send({ type: "run.result", protocol: WORKER_PROTOCOL, runId: run.runId });
        }
      });
      bridge.send({
        type: "run.started",
        protocol: WORKER_PROTOCOL,
        adapterVersion: WORKER_VERSION,
        runId: run.runId,
      });
      if (command.prompt !== undefined) await agent.prompt(command.prompt);
    } else if (command.type === "run.prompt") {
      if (!agent) throw new Error("run.prompt received before run.start");
      await agent.prompt(command.message);
    } else if (command.type === "run.abort") {
      agent?.abort();
    } else if (command.type === "run.reset") {
      agent?.reset();
    }
  }
}

if (process.argv[1] && pathToFileURL(resolve(process.argv[1])).href === import.meta.url) {
  runWorker().catch((error) => {
    process.stderr.write(`${error.stack ?? error}\n`);
    process.exitCode = 1;
  });
}
