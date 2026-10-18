package com.agrosense.promotion.api;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;
import java.time.OffsetDateTime;
import java.util.List;
import java.util.UUID;

public final class PromotionDtos {
    private PromotionDtos() {}
    public record PromotionRequest(
        @NotBlank @Size(max=120) String modelId,
        @NotBlank @Size(max=80) String modelVersion,
        @NotBlank @Size(max=120) String datasetVersion,
        @NotBlank @Pattern(regexp="^[0-9a-f]{64}$") String manifestSha256,
        @NotBlank @Pattern(regexp="^[0-9a-f]{64}$") String artifactSha256,
        UUID supersedesPromotionId,
        @NotNull @Size(max=1000) List<UUID> reviewIds) {}
    public record PromotionResponse(UUID id, String modelId, String modelVersion, String datasetVersion,
                                    String manifestSha256, String artifactSha256, UUID supersedesPromotionId,
                                    List<UUID> reviewIds, UUID promotedBy, OffsetDateTime promotedAt) {}
}
