package com.agrosense.scan.api;

import static com.agrosense.ai.AiContracts.BoundingBox;
import static com.agrosense.catalog.api.CatalogDtos.*;

import com.agrosense.scan.domain.IdentificationMode;
import java.time.OffsetDateTime;
import java.util.UUID;

public final class ScanDtos {
    private ScanDtos() {}
    public record ModelResponse(String id, String version, String datasetVersion) {}
    public record ScanResult(UUID id, IdentificationMode mode, CropResponse crop, String status, String reason, Double confidence,
                             BoundingBox bbox, String imageUrl, PestResponse pest, ModelResponse model,
                             boolean trainingConsent, OffsetDateTime consentedAt, String reviewStatus,
                             OffsetDateTime createdAt) {}
}
