package io.amesh.plugin;

import java.time.Instant;
import java.util.List;
import java.util.Map;

/** AMESH isolated-plugin wire contracts. The normative schema is schemas/plugin-wire.schema.json. */
public final class Wire {
    public static final String VERSION = "amesh.plugin.wire/v1";
    public static final String HANDSHAKE = "amesh.handshake";
    public static final String DISCOVER = "amesh.discover";
    public static final String VALIDATE = "amesh.validate";
    public static final String INVOKE = "amesh.invoke";
    public static final String CANCEL = "amesh.cancel";
    public static final String SHUTDOWN = "amesh.shutdown";
    public static final List<String> REQUIRED_FEATURES = List.of(
            "schema-discovery", "validation", "execution", "cancellation",
            "heartbeats", "logs", "metrics", "artifacts");

    private Wire() {}

    public record WorkloadIdentity(String sessionId, String workloadToken, Instant expiresAt) {}

    public record CapabilityEnvelope(
            Map<String, String> capabilityTokens,
            Map<String, String> secrets,
            Map<String, String> files,
            List<String> allowedEgress,
            List<String> platformApis) {}

    public record PluginRequest(
            String protocolVersion,
            String plugin,
            String entryPoint,
            String operation,
            Map<String, Object> session,
            Map<String, Object> configuration,
            Map<String, Object> input,
            Map<String, Object> context) {}

    public record InvocationParams(
            String sessionId,
            String workloadToken,
            PluginRequest request,
            CapabilityEnvelope capabilities) {}

    public record EntryPoint(
            String name,
            String type,
            String resourceType,
            Map<String, Object> configurationSchema,
            Map<String, Object> outputSchema) {}

    public record DiscoveryResult(
            String sessionId, String workloadToken, List<EntryPoint> entryPoints) {}

    public record PluginResponse(
            String protocolVersion,
            String invocationId,
            Map<String, Object> output,
            List<Map<String, Object>> logs,
            List<Map<String, Object>> errors,
            Map<String, Object> checkpoint) {}

    @FunctionalInterface
    public interface PluginHandler {
        PluginResponse invoke(PluginRequest request, CapabilityEnvelope capabilities) throws Exception;
    }
}
