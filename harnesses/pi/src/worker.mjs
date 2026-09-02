import { pathToFileURL } from "node:url";
import { resolve } from "node:path";
import { createHash } from "node:crypto";

import { Agent } from "@earendil-works/pi-agent-core";
import { createAssistantMessageEventStream } from "@earendil-works/pi-ai";

const TERMINAL_MODEL_EVENTS = new Set(["done", "error"]);
const WORKER_PROTOCOL = "amesh.pi-worker/v2";
const WORKER_VERSION = "0.84.3";
const DEFAULT_MAX_CONTROL_FRAME_BYTES = 1024 * 1024;
const configuredFrameLimit = Number.parseInt(process.env.AMESH_PI_MAX_FRAME_BYTES ?? "", 10);
const MAX_CONTROL_FRAME_BYTES = Number.isSafeInteger(configuredFrameLimit) && configuredFrameLimit > 0
  ? configuredFrameLimit
  : DEFAULT_MAX_CONTROL_FRAME_BYTES;

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
  #started = false;
  #maxFrameBytes;

  constructor({
    input = process.stdin,
    output = process.stdout,
    maxFrameBytes = MAX_CONTROL_FRAME_BYTES,
  } = {}) {
    if (!Number.isSafeInteger(maxFrameBytes) || maxFrameBytes < 1) {
      throw new Error("AMESH control frame limit must be a positive integer");
    }
    this.#input = input;
    this.#output = output;
    this.#maxFrameBytes = maxFrameBytes;
  }

  start() {
    if (this.#started) return;
    this.#started = true;
    void this.#readLines();
  }

  async #readLines() {
    let chunks = [];
    let bufferedBytes = 0;
    try {
      for await (const rawChunk of this.#input) {
        const chunk = Buffer.isBuffer(rawChunk) ? rawChunk : Buffer.from(rawChunk);
        let offset = 0;
        while (offset < chunk.length) {
          const newline = chunk.indexOf(0x0a, offset);
          const end = newline === -1 ? chunk.length : newline;
          const fragment = chunk.subarray(offset, end);
          bufferedBytes += fragment.length;
          if (bufferedBytes + 1 > this.#maxFrameBytes) {
            throw new Error("AMESH control frame exceeded the configured limit");
          }
          if (fragment.length) chunks.push(fragment);
          if (newline === -1) break;
          this.#handleLine(Buffer.concat(chunks, bufferedBytes).toString("utf8"));
          chunks = [];
          bufferedBytes = 0;
          offset = newline + 1;
        }
      }
      if (bufferedBytes) this.#handleLine(Buffer.concat(chunks, bufferedBytes).toString("utf8"));
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

  #handleLine(line) {
    if (!line.trim()) return;
    const message = JSON.parse(line);
    const requestId = message.requestId;
    const pending = requestId ? this.#pending.get(requestId) : undefined;
    if (pending) pending.handle(message);
    else this.#commands.push(message);
  }

  send(message) {
    const encoded = JSON.stringify(message);
    if (Buffer.byteLength(encoded, "utf8") + 1 > this.#maxFrameBytes) {
      throw new Error("AMESH control frame exceeded the configured limit");
    }
    this.#output.write(`${encoded}\n`);
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
    if (!run.contextProjection) {
      throw new Error("Pi transformContext did not produce a context projection");
    }
    const selectedContext = encodeSelectedContext(bridge, run, context.messages);
    bridge.requestModel(
      {
        runId: run.runId,
        sessionId: run.sessionId,
        model: { ...model, api: "amesh", provider: "amesh" },
        ...selectedContext,
        contextProjection: run.contextProjection,
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

function canonicalJson(value) {
  const normalize = (item) => {
    if (Array.isArray(item)) return item.map(normalize);
    if (item && typeof item === "object") {
      return Object.fromEntries(Object.keys(item).sort().map((key) => [key, normalize(item[key])]));
    }
    return item;
  };
  return JSON.stringify(normalize(value));
}

function contextSize(messages) {
  const bytes = Buffer.byteLength(canonicalJson(messages), "utf8");
  return { bytes, estimatedTokens: Math.max(1, Math.ceil(bytes / 4)) };
}

function encodeSelectedContext(bridge, run, messages) {
  const payload = Buffer.from(canonicalJson(messages), "utf8");
  if (payload.byteLength <= MAX_CONTROL_FRAME_BYTES / 2) {
    return { selectedMessages: messages };
  }
  const chunkSize = Math.floor(MAX_CONTROL_FRAME_BYTES / 2);
  const count = Math.ceil(payload.byteLength / chunkSize);
  for (let index = 0; index < count; index += 1) {
    const chunk = payload.subarray(index * chunkSize, (index + 1) * chunkSize);
    bridge.send({
      type: "context.chunk",
      protocol: WORKER_PROTOCOL,
      runId: run.runId,
      index,
      count,
      data: chunk.toString("base64"),
    });
  }
  return {
    selectedTranscript: {
      encoding: "base64-json-chunks",
      count,
      bytes: payload.byteLength,
      sha256: createHash("sha256").update(payload).digest("hex"),
    },
  };
}

function messageGroups(messages) {
  const firstAssistant = messages.findIndex((message) => message?.role === "assistant");
  const boundary = firstAssistant === -1 ? messages.length : firstAssistant;
  const prefix = Array.from({ length: boundary }, (_, index) => index);
  const groups = [];
  for (let index = boundary; index < messages.length; index += 1) {
    if (messages[index]?.role === "assistant" || groups.length === 0) groups.push([index]);
    else groups.at(-1).push(index);
  }
  return { prefix, groups };
}

export function projectContext(messages, budget) {
  if (!Array.isArray(messages) || messages.length === 0) {
    throw new Error("Pi context projection requires canonical messages");
  }
  const { prefix, groups } = messageGroups(messages);
  const retainedGroups = groups.map((group) => [...group]);
  const omitted = [];
  while (true) {
    const retained = [...prefix, ...retainedGroups.flat()];
    const selected = retained.map((index) => messages[index]);
    const size = contextSize(selected);
    const fits = (budget.maxMessages == null || selected.length <= budget.maxMessages)
      && (budget.maxBytes == null || size.bytes <= budget.maxBytes)
      && size.estimatedTokens <= budget.maxInputTokens;
    if (fits) {
      return {
        messages: selected,
        projection: {
          algorithm: "pi.transform-context/recent-complete-turns/v1",
          retainedSourceIndexes: retained,
          omittedSourceIndexes: omitted.toSorted((left, right) => left - right),
        },
      };
    }
    if (retainedGroups.length <= 1) {
      throw new Error("Pi pinned context and newest complete turn exceed the AMESH context budget");
    }
    omitted.push(...retainedGroups.shift());
  }
}

function collectTranscriptChunk(transcripts, command) {
  if (command.protocol !== WORKER_PROTOCOL || typeof command.runId !== "string") {
    throw new Error("Pi transcript chunk protocol mismatch");
  }
  if (!Number.isInteger(command.index) || !Number.isInteger(command.count)
      || command.index < 0 || command.count < 1 || command.index >= command.count
      || typeof command.data !== "string") {
    throw new Error("Pi transcript chunk metadata is invalid");
  }
  const existing = transcripts.get(command.runId) ?? { count: command.count, chunks: new Map() };
  if (existing.count !== command.count || existing.chunks.has(command.index)) {
    throw new Error("Pi transcript chunks are inconsistent or duplicated");
  }
  existing.chunks.set(command.index, command.data);
  transcripts.set(command.runId, existing);
}

function resolveTranscript(transcripts, command) {
  if (Array.isArray(command.messages)) return command.messages;
  const descriptor = command.transcript;
  const stored = transcripts.get(command.runId);
  if (!descriptor || descriptor.encoding !== "base64-json-chunks" || !stored
      || stored.count !== descriptor.count || stored.chunks.size !== descriptor.count) {
    throw new Error("Pi transcript chunks are incomplete");
  }
  const chunks = Array.from({ length: descriptor.count }, (_, index) => stored.chunks.get(index));
  if (chunks.some((chunk) => typeof chunk !== "string")) {
    throw new Error("Pi transcript chunk sequence has a gap");
  }
  const payload = Buffer.concat(chunks.map((chunk) => Buffer.from(chunk, "base64")));
  const digest = createHash("sha256").update(payload).digest("hex");
  if (payload.byteLength !== descriptor.bytes || digest !== descriptor.sha256) {
    throw new Error("Pi transcript chunk digest mismatch");
  }
  transcripts.delete(command.runId);
  const messages = JSON.parse(payload.toString("utf8"));
  if (!Array.isArray(messages) || messages.length === 0) {
    throw new Error("Pi transcript must contain messages");
  }
  return messages;
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

function safeDigest(value) {
  return createHash("sha256").update(String(value)).digest("hex").slice(0, 24);
}

function safeUuid(value) {
  const digest = createHash("sha256").update(String(value)).digest("hex");
  return `${digest.slice(0, 8)}-${digest.slice(8, 12)}-4${digest.slice(13, 16)}-8${digest.slice(17, 20)}-${digest.slice(20, 32)}`;
}

export function progressFrame(run, event) {
  if (!run.progressContext) return null;
  const context = run.progressContext;
  const turn = run.turn;
  const now = new Date().toISOString();
  const eventType = event?.type;
  const thinkingType = event.assistantMessageEvent?.type;
  const mappedEvent = [
    "agent_start",
    "turn_start",
    "message_start",
    "message_end",
    "message_update",
    "tool_execution_start",
    "tool_execution_update",
    "tool_execution_end",
    "turn_end",
    "agent_end",
  ].includes(eventType);
  if (!mappedEvent) return null;
  if (eventType === "message_update" && !["thinking_start", "thinking_delta", "thinking_end"].includes(thinkingType)) {
    return null;
  }
  if (eventType === "message_start" && event.message?.role !== "assistant") return null;
  if (eventType === "message_end" && event.message?.role !== "assistant") return null;
  run.progressSequence += 1;
  const base = {
    schemaVersion: "amesh.agent-progress/v1",
    attemptSessionId: context.attemptSessionId,
    attempt: context.attempt,
    turn,
    sourceId: `pi:${safeDigest(run.runId)}`,
    sourceSequence: run.progressSequence,
    occurredAt: now,
  };
  if (eventType === "agent_start") {
    return { ...base, activity: "MODEL", status: "STARTED", activityId: `agent:${safeDigest(run.runId)}` };
  }
  if (eventType === "turn_start") {
    return { ...base, activity: "MODEL", status: "STARTED", activityId: `turn:${turn}` };
  }
  if (eventType === "message_start" && event.message?.role === "assistant") {
    run.modelSequence += 1;
    return {
      ...base,
      activity: "MODEL",
      status: "STARTED",
      activityId: `model:${safeDigest(run.runId)}:${run.modelSequence}`,
    };
  }
  if (eventType === "message_end" && event.message?.role === "assistant") {
    const failed = event.message.stopReason === "error";
    return {
      ...base,
      activity: "MODEL",
      status: failed ? "FAILED" : "COMPLETED",
      activityId: `model:${safeDigest(run.runId)}:${run.modelSequence}`,
    };
  }
  if (eventType === "message_update") {
    const updateType = event.assistantMessageEvent?.type;
    if (["thinking_start", "thinking_delta", "thinking_end"].includes(updateType)) {
      if (updateType === "thinking_start") {
        run.thinkingSegment += 1;
        run.activeThinkingSegment = run.thinkingSegment;
      }
      const segment = run.activeThinkingSegment ?? run.thinkingSegment;
      const segmentId = safeUuid(`${run.runId}:thinking:${segment}`);
      const status = updateType === "thinking_start" ? "STARTED" : updateType === "thinking_end" ? "COMPLETED" : "DELTA";
      return {
        ...base,
        activity: "THINKING",
        status,
        activityId: `thinking:${segment}`,
        segmentId,
      };
    }
  }
  if (eventType === "tool_execution_start" || eventType === "tool_execution_update" || eventType === "tool_execution_end") {
    const toolKey = safeDigest(event.toolCallId ?? "tool");
    const segmentId = safeUuid(`${run.runId}:tool:${toolKey}`);
    const status = eventType === "tool_execution_start" ? "STARTED" : eventType === "tool_execution_end" ? (event.isError ? "FAILED" : "COMPLETED") : "DELTA";
    return {
      ...base,
      activity: "TOOL",
      status,
      activityId: `tool:${toolKey}`,
      segmentId,
    };
  }
  if (eventType === "turn_end") {
    return { ...base, activity: "MODEL", status: "COMPLETED", activityId: `turn:${turn}` };
  }
  if (eventType === "agent_end") {
    return { ...base, activity: "TERMINAL", status: "COMPLETED", activityId: `agent:${safeDigest(run.runId)}` };
  }
  return null;
}

export async function runWorker({ input = process.stdin, output = process.stdout } = {}) {
  const bridge = new JsonlBridge({ input, output });
  const transcripts = new Map();
  let agent;
  let run;

  for await (const command of bridge) {
    if (command.type === "transcript.chunk") {
      collectTranscriptChunk(transcripts, command);
    } else if (command.type === "run.start") {
      if (command.protocol !== WORKER_PROTOCOL) {
        throw new Error("AMESH worker protocol mismatch");
      }
      if (agent) throw new Error("Only one active Pi run is supported by this minimal worker");
      run = {
        runId: command.runId ?? "run-1",
        sessionId: command.sessionId ?? "session-1",
        turn: command.turn ?? 1,
        progressContext: command.progressContext,
        progressSequence: 0,
        modelSequence: 0,
        thinkingSegment: 0,
      };
      const model = normalizeModel(command.model);
      const tools = (command.tools ?? []).map((definition) => makeTool(bridge, run, definition));
      const canonicalMessages = resolveTranscript(transcripts, command);
      const contextBudget = command.contextBudget;
      if (!contextBudget || contextBudget.schemaVersion !== "amesh.agent-context-budget/v1") {
        throw new Error("AMESH context budget is required");
      }
      agent = new Agent({
        initialState: {
          systemPrompt: "",
          model,
          thinkingLevel: command.thinkingLevel ?? "off",
          tools,
          messages: canonicalMessages,
        },
        transformContext: async (messages) => {
          const projected = projectContext(messages, contextBudget);
          run.contextProjection = projected.projection;
          return projected.messages;
        },
        convertToLlm: (messages) => messages,
        streamFn: createStreamFn(bridge, run),
        sessionId: run.sessionId,
      });
      agent.subscribe((event) => {
        const progress = progressFrame(run, event);
        if (progress) {
          bridge.send({
            type: "progress",
            protocol: WORKER_PROTOCOL,
            runId: run.runId,
            frame: progress,
          });
        }
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
      await agent.continue();
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
