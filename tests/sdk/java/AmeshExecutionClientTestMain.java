import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpServer;
import io.amesh.client.AmeshExecutionClient;
import io.amesh.client.model.ExecutionDetail;
import io.amesh.client.model.ExecutionState;
import java.io.IOException;
import java.net.InetSocketAddress;
import java.net.http.HttpClient;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.time.Instant;
import java.util.Map;
import java.util.concurrent.atomic.AtomicInteger;
import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;

public final class AmeshExecutionClientTestMain {
    private static final String DETAIL =
            "{\"execution\":{\"execution_id\":\"0198cafe-0000-7000-8000-000000000001\","
                    + "\"tenant_id\":\"default\",\"state\":\"SUCCESS\",\"epoch\":1,\"version\":2,"
                    + "\"namespace\":\"examples.mvp\",\"flow_id\":\"hello_world\","
                    + "\"created_at\":\"2026-08-23T00:00:00Z\","
                    + "\"updated_at\":\"2026-08-23T00:00:01Z\"},\"taskRuns\":[]}";

    private AmeshExecutionClientTestMain() {}

    public static void main(String[] args) throws Exception {
        AtomicInteger calls = new AtomicInteger();
        HttpServer server = HttpServer.create(new InetSocketAddress("127.0.0.1", 0), 0);
        server.createContext(
                "/api/v1/executions",
                exchange -> {
                    try {
                        if (!"stable-key".equals(exchange.getRequestHeaders().getFirst("Idempotency-Key"))
                                || !"Bearer test-token"
                                        .equals(exchange.getRequestHeaders().getFirst("Authorization"))) {
                            respond(exchange, 400, "{}");
                        } else if (calls.incrementAndGet() == 1) {
                            exchange.getResponseHeaders().set("Retry-After", "0");
                            respond(exchange, 503, "{}");
                        } else {
                            respond(exchange, 200, DETAIL);
                        }
                    } finally {
                        exchange.close();
                    }
                });
        server.start();
        try {
            AmeshExecutionClient client =
                    new AmeshExecutionClient(
                            "http://127.0.0.1:" + server.getAddress().getPort(),
                            "test-token",
                            "default",
                            HttpClient.newHttpClient(),
                            new AmeshExecutionClient.RetryPolicy(
                                    2, Duration.ZERO, Duration.ZERO),
                            Duration.ofSeconds(5));
            ExecutionDetail detail =
                    client.launch(
                            "examples.mvp", "hello_world", Map.of("name", "SDK"), "local", "stable-key");
            if (detail.getExecution().getState() != ExecutionState.SUCCESS || calls.get() != 2) {
                throw new AssertionError("Java execution client did not retry the idempotent launch");
            }
            verifyWebhook();
        } finally {
            server.stop(0);
        }
        liveConformance();
    }

    private static void verifyWebhook() throws Exception {
        String secret = "webhook-secret";
        long timestamp = 1_800_000_000L;
        String deliveryId = "0198cafe-0000-7000-8000-000000000002";
        byte[] body = "{\"event\":\"execution.completed\"}".getBytes(StandardCharsets.UTF_8);
        Mac mac = Mac.getInstance("HmacSHA256");
        mac.init(new SecretKeySpec(secret.getBytes(StandardCharsets.UTF_8), "HmacSHA256"));
        mac.update((timestamp + "." + deliveryId + ".").getBytes(StandardCharsets.UTF_8));
        StringBuilder signature = new StringBuilder("v1=");
        for (byte value : mac.doFinal(body)) signature.append(String.format("%02x", value & 0xff));
        if (!AmeshExecutionClient.verifyWebhook(
                secret,
                timestamp,
                deliveryId,
                body,
                signature.toString(),
                Instant.ofEpochSecond(timestamp + 30),
                Duration.ofMinutes(5))) {
            throw new AssertionError("Java webhook signature verification failed");
        }
    }

    private static void liveConformance() throws Exception {
        String endpoint = System.getenv("AMESH_SDK_LIVE_ENDPOINT");
        if (endpoint == null || endpoint.isBlank()) return;
        AmeshExecutionClient client =
                new AmeshExecutionClient(
                        endpoint,
                        System.getenv("AMESH_SDK_LIVE_TOKEN"),
                        System.getenv().getOrDefault("AMESH_SDK_LIVE_TENANT", "default"),
                        HttpClient.newBuilder().version(HttpClient.Version.HTTP_1_1).build(),
                        new AmeshExecutionClient.RetryPolicy(
                                3, Duration.ofMillis(250), Duration.ofSeconds(2)),
                        Duration.ofSeconds(30));
        ExecutionDetail launched =
                client.launch(
                        System.getenv().getOrDefault(
                                "AMESH_SDK_LIVE_NAMESPACE", "examples.getting_started"),
                        System.getenv().getOrDefault("AMESH_SDK_LIVE_FLOW", "hello_world"),
                        Map.of("name", "Java SDK"));
        String executionId = launched.getExecution().getExecutionId().toString();
        ExecutionDetail completed =
                client.waitForTerminal(executionId, Duration.ofSeconds(90), Duration.ofMillis(250));
        if (completed.getExecution().getState() != ExecutionState.SUCCESS
                || !client.get(executionId).getExecution().getExecutionId().toString().equals(executionId)) {
            throw new AssertionError("Java live execution did not complete successfully");
        }
        client.logs(executionId);
        client.artifacts(executionId);
    }

    private static void respond(HttpExchange exchange, int status, String body) throws IOException {
        byte[] bytes = body.getBytes(StandardCharsets.UTF_8);
        exchange.sendResponseHeaders(status, bytes.length);
        exchange.getResponseBody().write(bytes);
    }
}
