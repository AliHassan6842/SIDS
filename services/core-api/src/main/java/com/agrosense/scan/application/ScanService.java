package com.agrosense.scan.application;

import static com.agrosense.ai.AiContracts.*;
import static com.agrosense.catalog.api.CatalogDtos.CropResponse;
import static com.agrosense.scan.api.ScanDtos.*;

import com.agrosense.ai.AiClient;
import com.agrosense.ai.AiResponseValidator;
import com.agrosense.catalog.infrastructure.CatalogRepository;
import com.agrosense.scan.infrastructure.ScanRepository;
import com.agrosense.scan.domain.IdentificationMode;
import com.agrosense.shared.error.ApiException;
import com.agrosense.storage.ImageSanitizer;
import com.agrosense.storage.PrivateImageStorage;
import java.util.List;
import java.util.UUID;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.multipart.MultipartFile;

@Service
public class ScanService {
    private final CatalogRepository catalog;
    private final ScanRepository scans;
    private final ImageSanitizer sanitizer;
    private final PrivateImageStorage storage;
    private final AiClient ai;
    private final AiResponseValidator aiResponses;
    public ScanService(CatalogRepository catalog, ScanRepository scans, ImageSanitizer sanitizer, PrivateImageStorage storage,
                       AiClient ai, AiResponseValidator aiResponses) {
        this.catalog = catalog; this.scans = scans; this.sanitizer = sanitizer; this.storage = storage; this.ai = ai;
        this.aiResponses = aiResponses;
    }
    public ValidateResponse validate(UUID cropId, MultipartFile image, String requestId) {
        return validate(IdentificationMode.CROP_PEST, cropId, image, requestId);
    }
    public ValidateResponse validate(IdentificationMode mode, UUID cropId, MultipartFile image, String requestId) {
        Context context = context(mode, cropId);
        return aiResponses.validate(ai.validate(sanitizer.sanitize(image), mode.name(), context.cropSlug(), requestId));
    }
    @Transactional
    public ScanResult create(UUID userId, UUID cropId, MultipartFile image, String requestId) {
        return create(userId, IdentificationMode.CROP_PEST, cropId, false, image, requestId);
    }
    @Transactional
    public ScanResult create(UUID userId, IdentificationMode mode, UUID cropId, boolean trainingConsent,
                             MultipartFile image, String requestId) {
        Context context = context(mode, cropId);
        byte[] sanitized = sanitizer.sanitize(image);
        UUID scanId = UUID.randomUUID();
        String imageKey = storage.save(userId, scanId, sanitized);
        try {
            IdentifyResponse result = aiResponses.validate(ai.identify(sanitized, mode.name(), context.cropSlug(), requestId));
            UUID pestId = null;
            if (mode == IdentificationMode.GENERAL_INSECT) {
                result = "REJECTED_IMAGE".equals(result.status())
                    ? new IdentifyResponse("REJECTED_IMAGE", result.reason(), null, null)
                    : new IdentifyResponse("UNKNOWN", "MODEL_UNAVAILABLE", null, null);
            } else if ("IDENTIFIED".equals(result.status())) {
                if (!catalog.supports(context.crop().id(), result.prediction().pestId())) {
                    result = new IdentifyResponse("UNKNOWN", "CLASS_UNCERTAIN", null, result.model());
                } else pestId = catalog.pestId(result.prediction().pestId());
            }
            scans.insert(scanId, userId, mode, cropId, imageKey, trainingConsent, result, pestId);
            return get(scanId, userId);
        } catch (RuntimeException exception) {
            try { storage.delete(imageKey); }
            catch (RuntimeException cleanupFailure) { exception.addSuppressed(cleanupFailure); }
            throw exception;
        }
    }
    public List<ScanResult> list(UUID userId) { return scans.list(userId).stream().map(this::view).toList(); }
    public ScanResult get(UUID scanId, UUID userId) { return scans.get(scanId, userId).map(this::view).orElseThrow(() -> new ApiException(HttpStatus.NOT_FOUND, "SCAN_NOT_FOUND", "Scan was not found.", false)); }
    public byte[] image(UUID scanId, UUID userId) { return storage.read(scans.get(scanId, userId).orElseThrow(() -> new ApiException(HttpStatus.NOT_FOUND, "SCAN_NOT_FOUND", "Scan was not found.", false)).imageKey()); }
    private CropResponse supportedCrop(UUID id) { return catalog.cropById(id).orElseThrow(() -> new ApiException(HttpStatus.BAD_REQUEST, "UNSUPPORTED_CROP", "Crop is not supported by the current model.", false)); }
    private ScanResult view(ScanRepository.Row row) {
        var crop = row.cropId() == null ? null : new CropResponse(row.cropId(), row.cropSlug(), row.cropName(),
            row.cropImageUrl(), row.cropIdentificationSupported());
        var pest = row.pestSlug() == null ? null : catalog.pestBySlug(row.pestSlug());
        var model = row.modelId() == null ? null : new ModelResponse(row.modelId(), row.modelVersion(), row.datasetVersion());
        return new ScanResult(row.id(), row.mode(), crop, row.status(), row.reason(), row.confidence(), row.bbox(),
            "/api/v1/scans/" + row.id() + "/image", pest, model, row.trainingConsent(), row.consentedAt(),
            row.reviewStatus(), row.createdAt());
    }
    private Context context(IdentificationMode mode, UUID cropId) {
        if (mode == null) mode = IdentificationMode.CROP_PEST;
        if (mode == IdentificationMode.GENERAL_INSECT) {
            if (cropId != null) throw new ApiException(HttpStatus.BAD_REQUEST, "CROP_NOT_ALLOWED",
                "cropId must be omitted for GENERAL_INSECT.", false);
            return new Context(null, null);
        }
        if (cropId == null) throw new ApiException(HttpStatus.BAD_REQUEST, "CROP_REQUIRED",
            "cropId is required for CROP_PEST.", false);
        CropResponse crop = supportedCrop(cropId);
        return new Context(crop, crop.slug());
    }
    private record Context(CropResponse crop, String cropSlug) {}
}
