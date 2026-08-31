/** AMESH isolated-plugin wire contracts. The normative schema is schemas/plugin-wire.schema.json. */

export const WIRE_VERSION = "amesh.plugin.wire/v1" as const;
export const METHODS = {
  handshake: "amesh.handshake",
  discover: "amesh.discover",
  validate: "amesh.validate",
  invoke: "amesh.invoke",
  cancel: "amesh.cancel",
  shutdown: "amesh.shutdown",
} as const;
export const REQUIRED_FEATURES = [
  "schema-discovery",
  "validation",
  "execution",
  "cancellation",
  "heartbeats",
  "logs",
  "metrics",
  "artifacts",
] as const;

export type WireFeature = (typeof REQUIRED_FEATURES)[number];
export type JsonValue = null | boolean | number | string | JsonValue[] | { [key: string]: JsonValue };

export interface JsonRpcRequest {
  jsonrpc: "2.0";
  id: string;
  method: string;
  params: Record<string, JsonValue>;
}

export interface JsonRpcNotification {
  jsonrpc: "2.0";
  method: string;
  params: Record<string, JsonValue>;
}

export interface WorkloadIdentity {
  sessionId: string;
  workloadToken: string;
}

export interface CapabilityEnvelope {
  capabilityTokens: Record<string, string>;
  secrets: Record<string, string>;
  files: Record<string, string>;
  allowedEgress: string[];
  platformApis: string[];
}

export interface PluginRequest {
  protocolVersion: "amesh.plugin.rpc/v1";
  plugin: string;
  entryPoint: string;
  operation: string;
  session: Record<string, JsonValue>;
  configuration: Record<string, JsonValue>;
  input: Record<string, JsonValue>;
  context: Record<string, JsonValue>;
}

export interface InvocationParams extends WorkloadIdentity {
  request: PluginRequest;
  capabilities: CapabilityEnvelope;
}

export interface EntryPoint {
  name: string;
  type: string;
  resourceType: string;
  configurationSchema: Record<string, JsonValue>;
  outputSchema?: Record<string, JsonValue>;
  inputModalities?: ("text" | "image")[];
}

export interface DiscoveryResult extends WorkloadIdentity {
  entryPoints: EntryPoint[];
}

export interface PluginResponse {
  protocolVersion: "amesh.plugin.rpc/v1";
  invocationId: string;
  output: Record<string, JsonValue>;
  logs: JsonValue[];
  errors: JsonValue[];
  checkpoint?: Record<string, JsonValue>;
}

export interface PluginHandler {
  (request: PluginRequest, capabilities: CapabilityEnvelope): Promise<PluginResponse>;
}
