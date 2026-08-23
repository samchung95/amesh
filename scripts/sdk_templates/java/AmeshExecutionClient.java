package io.amesh.client;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.amesh.client.model.ExecutionArtifact;
import io.amesh.client.model.ExecutionDetail;
import io.amesh.client.model.ExecutionState;
import io.amesh.client.model.TaskLog;
import java.io.IOException;
import java.net.URI;
import java.net.URLEncoder;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.time.Duration;
import java.time.Instant;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import java.util.stream.Stream;
import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;

/** Thread-safe high-level execution client layered over generated AMESH models. */
public final class AmeshExecutionClient {
    private static final Set<ExecutionState> TERMINAL_STATES =
            Set.of(
                    ExecutionState.CANCELLED,
                    ExecutionState.SUCCESS,
                    ExecutionState.FAILED,
                    ExecutionState.WARNING);
    private static final Set<Integer> RETRYABLE_STATUS = Set.of(408, 429, 502, 503, 504);

    private final URI endpoint;
    private final String token;
    private final String tenant;
    private final HttpClient httpClient;
    private final ObjectMapper mapper;
    private final RetryPolicy retryPolicy;
    private final Duration timeout;

    public AmeshExecutionClient(String endpoint, String token) {
        this(
                endpoint,
                token,
                "default",
                HttpClient.newBuilder().version(HttpClient.Version.HTTP_1_1).build(),
                RetryPolicy.defaults(),
                Duration.ofSeconds(30));
    }

    public AmeshExecutionClient(
            String endpoint,
            String token,
            String tenant,
            HttpClient httpClient,
            RetryPolicy retryPolicy,
            Duration timeout) {
        if (endpoint == null || endpoint.isBlank() || token == null || token.isBlank()) {
            throw new IllegalArgumentException("endpoint and token are required");
        }
        this.endpoint = URI.create(endpoint.replaceAll("/+$", ""));
        this.token = token;
        this.tenant = tenant;
        this.httpClient = httpClient;
        this.mapper = ApiClient.createDefaultObjectMapper();
        this.retryPolicy = retryPolicy;
        this.timeout = timeout;
    }

    public ExecutionDetail launch(String namespace, String flowId, Map<String, Object> inputs)
            throws IOException, InterruptedException {
        return launch(namespace, flowId, inputs, "local", UUID.randomUUID().toString());
    }

    public ExecutionDetail launch(
            String namespace,
            String flowId,
            Map<String, Object> inputs,
            String runner,
            String idempotencyKey)
            throws IOException, InterruptedException {
        Map<String, Object> body = new LinkedHashMap<>();
        body.put("namespace", namespace);
        body.put("flowId", flowId);
        body.put("inputs", inputs == null ? Map.of() : inputs);
        body.put("runner", runner);
        body.put("idempotencyKey", idempotencyKey);
        return mapper.readValue(
                request("POST", "/api/v1/executions", body, idempotencyKey, true, "application/json"),
                ExecutionDetail.class);
    }

    public ExecutionDetail get(String executionId) throws IOException, InterruptedException {
        return mapper.readValue(
                request(
                        "GET",
                        "/api/v1/executions/" + segment(executionId),
                        null,
                        null,
                        true,
                        "application/json"),
                ExecutionDetail.class);
    }

    public ExecutionDetail waitForTerminal(String executionId, Duration waitTimeout, Duration poll)
            throws IOException, InterruptedException {
        Instant deadline = Instant.now().plus(waitTimeout);
        while (true) {
            ExecutionDetail detail = get(executionId);
            if (TERMINAL_STATES.contains(detail.getExecution().getState())) {
                return detail;
            }
            Duration remaining = Duration.between(Instant.now(), deadline);
            if (remaining.isZero() || remaining.isNegative()) {
                throw new java.net.http.HttpTimeoutException(
                        "execution " + executionId + " did not reach a terminal state");
            }
            Thread.sleep(Math.min(poll.toMillis(), remaining.toMillis()));
        }
    }

    public ExecutionDetail cancel(String executionId, String reason, double graceSeconds)
            throws IOException, InterruptedException {
        ExecutionDetail current = get(executionId);
        Map<String, Object> body = new LinkedHashMap<>();
        body.put("action", "REQUEST_CANCEL");
        body.put("expectedVersion", current.getExecution().getVersion());
        body.put("expectedEpoch", current.getExecution().getEpoch());
        body.put("reason", reason);
        body.put("graceSeconds", graceSeconds);
        return mapper.readValue(
                request(
                        "POST",
                        "/api/v1/executions/" + segment(executionId) + "/interventions",
                        body,
                        null,
                        false,
                        "application/json"),
                ExecutionDetail.class);
    }

    public List<TaskLog> logs(String executionId) throws IOException, InterruptedException {
        return mapper.readValue(
                request(
                        "GET",
                        "/api/v1/executions/" + segment(executionId) + "/logs",
                        null,
                        null,
                        true,
                        "application/json"),
                new TypeReference<List<TaskLog>>() {});
    }

    public List<ExecutionArtifact> artifacts(String executionId)
            throws IOException, InterruptedException {
        return mapper.readValue(
                request(
                        "GET",
                        "/api/v1/executions/" + segment(executionId) + "/files",
                        null,
                        null,
                        true,
                        "application/json"),
                new TypeReference<List<ExecutionArtifact>>() {});
    }

    public byte[] downloadArtifact(String executionId, String artifactId)
            throws IOException, InterruptedException {
        return request(
                "GET",
                "/api/v1/executions/"
                        + segment(executionId)
                        + "/files/"
                        + segment(artifactId),
                null,
                null,
                true,
                "application/octet-stream");
    }

    public Stream<JsonNode> streamLogs(String executionId)
            throws IOException, InterruptedException {
        String document =
                new String(
                        request(
                                "GET",
                                "/api/v1/executions/" + segment(executionId) + "/logs/stream",
                                null,
                                null,
                                true,
                                "application/x-ndjson"),
                        StandardCharsets.UTF_8);
        return document.lines().filter(line -> !line.isBlank()).map(this::readTree);
    }

    private byte[] request(
            String method,
            String path,
            Object body,
            String idempotencyKey,
            boolean retryable,
            String accept)
            throws IOException, InterruptedException {
        byte[] encoded = body == null ? new byte[0] : mapper.writeValueAsBytes(body);
        Duration delay = retryPolicy.initialDelay;
        AmeshException lastError = null;
        for (int attempt = 0; attempt < retryPolicy.maxAttempts; attempt++) {
            HttpRequest.Builder builder =
                    HttpRequest.newBuilder(endpoint.resolve(path))
                            .timeout(timeout)
                            .header("Accept", accept)
                            .header("Authorization", "Bearer " + token)
                            .header("X-Amesh-Tenant", tenant);
            if (idempotencyKey != null) {
                builder.header("Idempotency-Key", idempotencyKey);
            }
            if (body == null) {
                builder.method(method, HttpRequest.BodyPublishers.noBody());
            } else {
                builder.header("Content-Type", "application/json");
                builder.method(method, HttpRequest.BodyPublishers.ofByteArray(encoded));
            }
            try {
                HttpResponse<byte[]> response =
                        httpClient.send(builder.build(), HttpResponse.BodyHandlers.ofByteArray());
                if (response.statusCode() >= 200 && response.statusCode() < 300) {
                    return response.body();
                }
                lastError = responseError(response);
                if (!retryable || !lastError.isRetryable() || attempt + 1 >= retryPolicy.maxAttempts) {
                    throw lastError;
                }
                delay = retryAfter(response, delay);
            } catch (IOException error) {
                lastError = new AmeshException("AMESH transport failed", 0, "transport_error", "", true);
                if (!retryable || attempt + 1 >= retryPolicy.maxAttempts) {
                    throw lastError;
                }
            }
            Thread.sleep(delay.toMillis());
            delay = delay.multipliedBy(2).compareTo(retryPolicy.maximumDelay) > 0
                    ? retryPolicy.maximumDelay
                    : delay.multipliedBy(2);
        }
        throw lastError == null
                ? new AmeshException("AMESH request failed", 0, "request_failed", "", false)
                : lastError;
    }

    private AmeshException responseError(HttpResponse<byte[]> response) {
        String message = "AMESH request failed with HTTP " + response.statusCode();
        String code = "request_failed";
        try {
            JsonNode root = mapper.readTree(response.body());
            if (root.path("detail").isTextual() && root.path("detail").asText().length() <= 512) {
                message = root.path("detail").asText();
            }
            if (root.path("code").isTextual()) {
                code = root.path("code").asText();
            }
        } catch (IOException ignored) {
            // Do not copy an arbitrary response body into an exception.
        }
        return new AmeshException(
                message,
                response.statusCode(),
                code,
                response.headers().firstValue("x-request-id").orElse(""),
                RETRYABLE_STATUS.contains(response.statusCode()));
    }

    private static Duration retryAfter(HttpResponse<?> response, Duration fallback) {
        try {
            return Duration.ofMillis(
                    Math.max(
                            0,
                            Math.round(
                                    Double.parseDouble(
                                                    response.headers()
                                                            .firstValue("retry-after")
                                                            .orElseThrow())
                                            * 1000)));
        } catch (RuntimeException ignored) {
            return fallback;
        }
    }

    private JsonNode readTree(String line) {
        try {
            return mapper.readTree(line);
        } catch (IOException error) {
            throw new AmeshException("AMESH returned invalid NDJSON", 502, "invalid_response", "", false);
        }
    }

    private static String segment(String value) {
        return URLEncoder.encode(value, StandardCharsets.UTF_8).replace("+", "%20");
    }

    public static boolean verifyWebhook(
            String secret,
            long timestamp,
            String deliveryId,
            byte[] body,
            String signature,
            Instant now,
            Duration tolerance) {
        if (tolerance.isNegative()
                || Math.abs(now.getEpochSecond() - timestamp) > tolerance.getSeconds()) {
            return false;
        }
        try {
            Mac mac = Mac.getInstance("HmacSHA256");
            mac.init(new SecretKeySpec(secret.getBytes(StandardCharsets.UTF_8), "HmacSHA256"));
            mac.update((timestamp + "." + deliveryId + ".").getBytes(StandardCharsets.UTF_8));
            byte[] digest = mac.doFinal(body);
            StringBuilder expected = new StringBuilder("v1=");
            for (byte value : digest) {
                expected.append(String.format("%02x", value & 0xff));
            }
            return MessageDigest.isEqual(
                    expected.toString().getBytes(StandardCharsets.US_ASCII),
                    signature.getBytes(StandardCharsets.US_ASCII));
        } catch (java.security.GeneralSecurityException error) {
            throw new IllegalStateException("HMAC-SHA256 is unavailable", error);
        }
    }

    public static final class RetryPolicy {
        private final int maxAttempts;
        private final Duration initialDelay;
        private final Duration maximumDelay;

        public RetryPolicy(int maxAttempts, Duration initialDelay, Duration maximumDelay) {
            if (maxAttempts < 1 || initialDelay.isNegative() || maximumDelay.isNegative()) {
                throw new IllegalArgumentException("invalid retry policy");
            }
            this.maxAttempts = maxAttempts;
            this.initialDelay = initialDelay;
            this.maximumDelay = maximumDelay;
        }

        public static RetryPolicy defaults() {
            return new RetryPolicy(3, Duration.ofMillis(250), Duration.ofSeconds(2));
        }
    }

    public static final class AmeshException extends RuntimeException {
        private final int status;
        private final String code;
        private final String requestId;
        private final boolean retryable;

        public AmeshException(
                String message, int status, String code, String requestId, boolean retryable) {
            super(message);
            this.status = status;
            this.code = code;
            this.requestId = requestId;
            this.retryable = retryable;
        }

        public int getStatus() {
            return status;
        }

        public String getCode() {
            return code;
        }

        public String getRequestId() {
            return requestId;
        }

        public boolean isRetryable() {
            return retryable;
        }
    }
}
