package com.agrosense.ai;

import static com.agrosense.ai.AiContracts.*;

import com.agrosense.shared.error.ApiException;
import java.time.Duration;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.ByteArrayResource;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.client.SimpleClientHttpRequestFactory;
import org.springframework.stereotype.Component;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.web.client.RestClient;
import org.springframework.web.client.RestClientException;

@Component
public class AiClient {
    private final RestClient client;
    private final String serviceToken;
    public AiClient(@Value("${sids.ai.base-url}") String baseUrl,
                    @Value("${sids.ai.service-token}") String serviceToken,
                    @Value("${sids.ai.connect-timeout}") Duration connectTimeout,
                    @Value("${sids.ai.read-timeout}") Duration readTimeout) {
        if (invalidSecret(serviceToken))
            throw new IllegalStateException("AI_SERVICE_TOKEN must be a non-placeholder value of at least 24 characters");
        var factory = new SimpleClientHttpRequestFactory();
        factory.setConnectTimeout(connectTimeout);
        factory.setReadTimeout(readTimeout);
        client = RestClient.builder().baseUrl(baseUrl).requestFactory(factory).build();
        this.serviceToken = serviceToken;
    }
    private boolean invalidSecret(String token) {
        if (token == null || token.isBlank() || token.length() < 24) return true;
        String normalized = token.toLowerCase(java.util.Locale.ROOT);
        return normalized.contains("replace-with") || normalized.contains("change-me") || normalized.contains("development-internal");
    }
    public ValidateResponse validate(byte[] image, String cropId, String requestId) {
        return validate(image, "CROP_PEST", cropId, requestId);
    }
    public ValidateResponse validate(byte[] image, String mode, String cropId, String requestId) {
        return post("/internal/v1/validate-frame", image, mode, cropId, requestId, ValidateResponse.class);
    }
    public IdentifyResponse identify(byte[] image, String cropId, String requestId) {
        return identify(image, "CROP_PEST", cropId, requestId);
    }
    public IdentifyResponse identify(byte[] image, String mode, String cropId, String requestId) {
        return post("/internal/v1/identify", image, mode, cropId, requestId, IdentifyResponse.class);
    }
    private <T> T post(String path, byte[] image, String mode, String cropId, String requestId, Class<T> type) {
        var body = new LinkedMultiValueMap<String, Object>();
        body.add("mode", mode);
        if (cropId != null) body.add("crop_id", cropId);
        var imageHeaders = new HttpHeaders();
        imageHeaders.setContentType(MediaType.IMAGE_JPEG);
        var imageResource = new ByteArrayResource(image) {
            @Override public String getFilename() { return "capture.jpg"; }
        };
        body.add("image", new HttpEntity<>(imageResource, imageHeaders));
        try {
            T response = client.post().uri(path).header("X-Request-Id", requestId)
                .header("X-SIDS-Service-Token", serviceToken)
                .contentType(MediaType.MULTIPART_FORM_DATA).body(body).retrieve().body(type);
            if (response == null) throw new RestClientException("Empty AI response");
            return response;
        } catch (RestClientException exception) {
            throw new ApiException(org.springframework.http.HttpStatus.SERVICE_UNAVAILABLE, "AI_SERVICE_UNAVAILABLE",
                "Identification service is temporarily unavailable.", true);
        }
    }
}
