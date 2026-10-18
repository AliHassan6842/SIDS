package com.agrosense.ai;

import static org.assertj.core.api.Assertions.assertThat;

import com.sun.net.httpserver.HttpServer;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.util.ArrayList;
import java.util.List;
import org.junit.jupiter.api.Test;

class AiClientMultipartContractTest {
    @Test
    void sendsExplicitModeAndOmitsFakeCropForGeneralInsect() throws Exception {
        List<String> requests = new ArrayList<>();
        HttpServer server = server(requests);
        try {
            var client = new AiClient("http://127.0.0.1:" + server.getAddress().getPort(),
                "test-service-token-with-32-characters", Duration.ofSeconds(2), Duration.ofSeconds(2));

            client.identify(new byte[]{1, 2}, "GENERAL_INSECT", null, "request-general");
            client.identify(new byte[]{1, 2}, "CROP_PEST", "rice", "request-crop");

            assertThat(requests.get(0)).contains("name=\"mode\"", "GENERAL_INSECT")
                .doesNotContain("name=\"crop_id\"");
            assertThat(requests.get(1)).contains("name=\"mode\"", "CROP_PEST",
                "name=\"crop_id\"", "rice");
        } finally {
            server.stop(0);
        }
    }

    private HttpServer server(List<String> requests) throws Exception {
        HttpServer server = HttpServer.create(new InetSocketAddress("127.0.0.1", 0), 0);
        server.createContext("/internal/v1/identify", exchange -> {
            requests.add(new String(exchange.getRequestBody().readAllBytes(), StandardCharsets.ISO_8859_1));
            byte[] response = "{\"status\":\"UNKNOWN\",\"reason\":\"MODEL_UNAVAILABLE\",\"prediction\":null,\"model\":{\"id\":\"unavailable\",\"version\":\"unavailable\",\"datasetVersion\":\"unavailable\"}}"
                .getBytes(StandardCharsets.UTF_8);
            exchange.getResponseHeaders().add("Content-Type", "application/json");
            exchange.sendResponseHeaders(200, response.length);
            exchange.getResponseBody().write(response);
            exchange.close();
        });
        server.start();
        return server;
    }
}
