import { test } from "node:test";
import assert from "node:assert/strict";
import { createInterface } from "node:readline";
import { spawn } from "node:child_process";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

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
