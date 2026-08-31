import { test } from "node:test";
import assert from "node:assert/strict";
import { createInterface } from "node:readline";
import { spawn } from "node:child_process";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import { JsonlBridge, progressFrame } from "../src/worker.mjs";

const here = dirname(fileURLToPath(import.meta.url));
const worker = join(here, "..", "src", "worker.mjs");

function usage() {
  return { input: 1, output: 1, cacheRead: 0, cacheWrite: 0, totalTokens: 2 };
}

function assistant(model, content, stopReason) {
  return {
    role: "assistant",
    content,
    api: "amesh",
    provider: "amesh",
    model,
    usage: usage(),
    stopReason,
    timestamp: Date.now(),
  };
}

function writeJson(child, message) {
  child.stdin.write(`${JSON.stringify(message)}\n`);
}

test("proxies one model/tool round-trip without echoing model content", async () => {
  const child = spawn(process.execPath, [worker], { stdio: ["pipe", "pipe", "pipe"] });
  const lines = createInterface({ input: child.stdout, crlfDelay: Infinity });
  const messages = [];
  const stderr = [];
  child.stderr.on("data", (chunk) => stderr.push(String(chunk)));
  let modelRequests = 0;
  let toolRequests = 0;

  const result = new Promise((resolve, reject) => {
    lines.on("line", (line) => {
      const message = JSON.parse(line);
      messages.push(message);
      if (message.type === "model.request") {
        modelRequests += 1;
        const partial = assistant(message.model.id, [], "stop");
        if (modelRequests === 1) {
          writeJson(child, { type: "model.event", requestId: message.requestId, event: { type: "start", partial } });
          writeJson(child, {
            type: "model.event",
            requestId: message.requestId,
            event: {
              type: "done",
              reason: "toolUse",
              message: assistant(
                message.model.id,
                [{ type: "toolCall", id: "call-1", name: "echo", arguments: { text: "hello" } }],
                "toolUse",
              ),
            },
          });
        } else {
          writeJson(child, { type: "model.event", requestId: message.requestId, event: { type: "start", partial } });
          writeJson(child, {
            type: "model.event",
            requestId: message.requestId,
            event: {
              type: "done",
              reason: "stop",
              message: assistant(message.model.id, [{ type: "text", text: "final answer" }], "stop"),
            },
          });
        }
      } else if (message.type === "tool.request") {
        toolRequests += 1;
        writeJson(child, {
          type: "tool.result",
          requestId: message.requestId,
          result: { content: [{ type: "text", text: `echo:${message.arguments.text}` }], details: {} },
        });
      } else if (message.type === "run.result") {
        resolve(message);
      }
    });
    child.on("error", reject);
    child.on("exit", (code, signal) => {
      if (code !== 0) reject(new Error(`worker exited with ${code ?? signal}: ${stderr.join("")}`));
    });
  });

  writeJson(child, {
    type: "run.start",
    protocol: "amesh.pi-worker/v1",
    runId: "run-test",
    sessionId: "session-test",
    model: { id: "scripted-model" },
    prompt: "Use the echo tool.",
    tools: [{
      name: "echo",
      description: "Echo text through the AMESH parent.",
      parameters: {
        type: "object",
        properties: { text: { type: "string" } },
        required: ["text"],
        additionalProperties: false,
      },
    }],
  });

  const runResult = await result;
  assert.equal(modelRequests, 2);
  assert.equal(toolRequests, 1);
  assert.equal(runResult.runId, "run-test");
  assert.deepEqual(Object.keys(runResult).sort(), ["protocol", "runId", "type"]);
  assert.equal(messages.filter((message) => message.type === "tool.request")[0].name, "echo");

  child.kill();
  lines.close();
});

test("maps Pi thinking and tool events to safe ordered frames", () => {
  const run = {
    runId: "run-unit",
    turn: 1,
    progressContext: {
      attemptSessionId: "00000000-0000-4000-8000-000000000004",
      attempt: 1,
    },
    progressSequence: 0,
    modelSequence: 0,
    thinkingSegment: 0,
  };
  const events = [
    { type: "message_update", assistantMessageEvent: { type: "thinking_start" } },
    { type: "message_update", assistantMessageEvent: { type: "thinking_delta", delta: "hidden" } },
    { type: "message_update", assistantMessageEvent: { type: "thinking_end", content: "hidden" } },
    { type: "tool_execution_start", toolCallId: "private-tool-id" },
    { type: "tool_execution_end", toolCallId: "private-tool-id", isError: false },
  ];

  const frames = events.map((event) => progressFrame(run, event));
  assert.deepEqual(frames.map((frame) => [frame.activity, frame.status]), [
    ["THINKING", "STARTED"],
    ["THINKING", "DELTA"],
    ["THINKING", "COMPLETED"],
    ["TOOL", "STARTED"],
    ["TOOL", "COMPLETED"],
  ]);
  assert.deepEqual(frames.map((frame) => frame.sourceSequence), [1, 2, 3, 4, 5]);
  assert.equal(JSON.stringify(frames).includes("hidden"), false);
  assert.equal(JSON.stringify(frames).includes("private-tool-id"), false);
});

test("bounds worker-to-parent JSONL frames", () => {
  const bridge = new JsonlBridge({ output: { write() {} } });
  assert.throws(
    () => bridge.send({ type: "progress", frame: { text: "x".repeat(1024 * 1024) } }),
    /control frame exceeded the configured limit/,
  );
});

test("emits bounded chronological safe progress without reasoning or tool authority", async () => {
  const child = spawn(process.execPath, [worker], { stdio: ["pipe", "pipe", "pipe"] });
  const lines = createInterface({ input: child.stdout, crlfDelay: Infinity });
  const progress = [];
  const stdoutMessages = [];
  const stderr = [];
  child.stderr.on("data", (chunk) => stderr.push(String(chunk)));
  let modelRequests = 0;

  const result = new Promise((resolve, reject) => {
    lines.on("line", (line) => {
      const message = JSON.parse(line);
      stdoutMessages.push(message);
      if (message.type === "progress") {
        progress.push(message);
        return;
      }
      if (message.type === "model.request") {
        modelRequests += 1;
        const thinking = (text) => [
          { type: "model.event", requestId: message.requestId, event: { type: "thinking_start", contentIndex: 0, partial: assistant(message.model.id, [{ type: "thinking", thinking: "" }], "stop") } },
          { type: "model.event", requestId: message.requestId, event: { type: "thinking_delta", contentIndex: 0, delta: text, partial: assistant(message.model.id, [{ type: "thinking", thinking: text }], "stop") } },
          { type: "model.event", requestId: message.requestId, event: { type: "thinking_end", contentIndex: 0, content: text, partial: assistant(message.model.id, [{ type: "thinking", thinking: text }], "stop") } },
        ];
        writeJson(child, {
          type: "model.event",
          requestId: message.requestId,
          event: {
            type: "start",
            partial: assistant(message.model.id, [], "stop"),
          },
        });
        if (modelRequests === 1) {
          for (const event of thinking("private-thought-one")) writeJson(child, event);
          writeJson(child, {
            type: "model.event",
            requestId: message.requestId,
            event: {
              type: "done",
              reason: "toolUse",
              message: assistant(
                message.model.id,
                [{ type: "toolCall", id: "secret-tool-call", name: "echo", arguments: { text: "hello" } }],
                "toolUse",
              ),
            },
          });
        } else {
          for (const event of thinking("private-thought-two")) writeJson(child, event);
          writeJson(child, {
            type: "model.event",
            requestId: message.requestId,
            event: { type: "done", reason: "stop", message: assistant(message.model.id, [{ type: "text", text: "final" }], "stop") },
          });
        }
      } else if (message.type === "tool.request") {
        writeJson(child, {
          type: "tool.result",
          requestId: message.requestId,
          result: { content: [{ type: "text", text: "tool-result" }], details: {} },
        });
      } else if (message.type === "run.result") {
        resolve(message);
      }
    });
    child.on("error", reject);
    child.on("exit", (code, signal) => {
      if (code !== 0) reject(new Error(`worker exited with ${code ?? signal}: ${stderr.join("")}`));
    });
  });

  writeJson(child, {
    type: "run.start",
    protocol: "amesh.pi-worker/v1",
    runId: "run-progress-test",
    sessionId: "session-progress-test",
    turn: 1,
    progressContext: {
      serviceSessionId: "00000000-0000-4000-8000-000000000001",
      executionId: "00000000-0000-4000-8000-000000000002",
      taskRunId: "00000000-0000-4000-8000-000000000003",
      attemptSessionId: "00000000-0000-4000-8000-000000000004",
      attempt: 1,
    },
    model: { id: "scripted-model" },
    thinkingLevel: "high",
    prompt: "Use the echo tool.",
    tools: [{ name: "echo", description: "Echo through AMESH.", parameters: { type: "object" } }],
  });

  await result;
  const frames = progress.map((message) => message.frame);
  assert.deepEqual(frames.map((frame) => frame.status), [
    "STARTED", "STARTED", "STARTED", "STARTED", "DELTA", "COMPLETED",
    "COMPLETED", "STARTED", "COMPLETED", "COMPLETED", "STARTED", "STARTED",
    "STARTED", "DELTA", "COMPLETED", "COMPLETED", "COMPLETED", "COMPLETED",
  ]);
  assert.deepEqual(frames.map((frame) => frame.activity), [
    "MODEL", "MODEL", "MODEL", "THINKING", "THINKING", "THINKING", "MODEL",
    "TOOL", "TOOL", "MODEL", "MODEL", "MODEL", "THINKING", "THINKING",
    "THINKING", "MODEL", "MODEL", "TERMINAL",
  ]);
  assert.deepEqual(frames.map((frame) => frame.sourceSequence), frames.map((_, index) => index + 1));
  const thinkingSegments = frames
    .filter((frame) => frame.activity === "THINKING")
    .map((frame) => frame.segmentId);
  assert.equal(new Set(thinkingSegments.slice(0, 3)).size, 1);
  assert.equal(new Set(thinkingSegments.slice(3)).size, 1);
  assert.notEqual(thinkingSegments[0], thinkingSegments[3]);
  assert.equal(frames.some((frame) => JSON.stringify(frame).includes("private-thought")), false);
  assert.equal(frames.some((frame) => JSON.stringify(frame).includes("secret-tool-call")), false);
  assert.equal(stdoutMessages.some((message) => message.type === "progress" && message.frame.arguments), false);

  child.kill();
  lines.close();
});
