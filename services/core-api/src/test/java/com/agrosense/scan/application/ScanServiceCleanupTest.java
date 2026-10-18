package com.agrosense.scan.application;

import static com.agrosense.ai.AiContracts.*;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

import com.agrosense.ai.AiClient;
import com.agrosense.ai.AiResponseValidator;
import com.agrosense.catalog.api.CatalogDtos.CropResponse;
import com.agrosense.catalog.infrastructure.CatalogRepository;
import com.agrosense.scan.infrastructure.ScanRepository;
import com.agrosense.scan.domain.IdentificationMode;
import com.agrosense.shared.error.ApiException;
import com.agrosense.storage.ImageSanitizer;
import com.agrosense.storage.PrivateImageStorage;
import java.util.Optional;
import java.time.OffsetDateTime;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.http.HttpStatus;
import org.springframework.mock.web.MockMultipartFile;

@ExtendWith(MockitoExtension.class)
class ScanServiceCleanupTest {
    @Mock CatalogRepository catalog;
    @Mock ScanRepository scans;
    @Mock ImageSanitizer sanitizer;
    @Mock PrivateImageStorage storage;
    @Mock AiClient ai;
    private ScanService service;
    private UUID cropId;
    private UUID userId;
    private MockMultipartFile upload;
    private byte[] sanitized;

    @BeforeEach
    void setUp() {
        service = new ScanService(catalog, scans, sanitizer, storage, ai, new AiResponseValidator());
        cropId = UUID.randomUUID();
        userId = UUID.randomUUID();
        upload = new MockMultipartFile("image", "capture.jpg", "image/jpeg", new byte[] {1});
        sanitized = new byte[] {2};
        lenient().when(catalog.cropById(cropId)).thenReturn(Optional.of(new CropResponse(cropId, "rice", "Rice")));
        lenient().when(sanitizer.sanitize(upload)).thenReturn(sanitized);
        lenient().when(storage.save(eq(userId), any(UUID.class), same(sanitized))).thenReturn("new/image-key.jpg");
    }

    @Test
    void removesNewlySavedImageWhenAiCallFails() {
        when(ai.identify(sanitized, "CROP_PEST", "rice", "request-1"))
            .thenThrow(new ApiException(HttpStatus.SERVICE_UNAVAILABLE, "AI_SERVICE_UNAVAILABLE", "Unavailable", true));

        assertThatThrownBy(() -> service.create(userId, cropId, upload, "request-1"))
            .isInstanceOf(ApiException.class);

        verify(storage).delete("new/image-key.jpg");
        verifyNoInteractions(scans);
    }

    @Test
    void removesNewlySavedImageWhenPersistenceFails() {
        IdentifyResponse response = new IdentifyResponse("UNKNOWN", "LOW_CONFIDENCE", null,
            new Model("sids-rice-pest-detector", "1.0.0", "sids-rice-pest-detection-v1.1"));
        when(ai.identify(sanitized, "CROP_PEST", "rice", "request-1")).thenReturn(response);
        doThrow(new RuntimeException("database unavailable")).when(scans)
            .insert(any(UUID.class), eq(userId), eq(IdentificationMode.CROP_PEST), eq(cropId),
                eq("new/image-key.jpg"), eq(false), same(response), isNull());

        assertThatThrownBy(() -> service.create(userId, cropId, upload, "request-1"))
            .isInstanceOf(RuntimeException.class).hasMessage("database unavailable");

        verify(storage).delete("new/image-key.jpg");
    }

    @Test
    void enforcesModeCropRulesBeforeImageProcessing() {
        assertThatThrownBy(() -> service.validate(IdentificationMode.CROP_PEST, null, upload, "request-1"))
            .isInstanceOf(ApiException.class)
            .satisfies(error -> org.assertj.core.api.Assertions.assertThat(((ApiException) error).code()).isEqualTo("CROP_REQUIRED"));
        assertThatThrownBy(() -> service.validate(IdentificationMode.GENERAL_INSECT, cropId, upload, "request-1"))
            .isInstanceOf(ApiException.class)
            .satisfies(error -> org.assertj.core.api.Assertions.assertThat(((ApiException) error).code()).isEqualTo("CROP_NOT_ALLOWED"));
        verifyNoInteractions(sanitizer);
    }

    @Test
    void generalInsectCannotBecomeKnownWithoutPromotedGeneralCatalog() {
        IdentifyResponse identified = new IdentifyResponse("IDENTIFIED", null,
            new Prediction("household-beetle", 0.99, null),
            new Model("future-general-model", "0.1.0", "research-only"));
        when(ai.identify(sanitized, "GENERAL_INSECT", null, "request-1")).thenReturn(identified);
        when(scans.get(any(UUID.class), eq(userId))).thenAnswer(invocation -> {
            UUID id = invocation.getArgument(0);
            return Optional.of(new ScanRepository.Row(id, userId, IdentificationMode.GENERAL_INSECT,
                null, null, null, null, false, "new/image-key.jpg", "UNKNOWN", OffsetDateTime.now(),
                null, null, null, null, null, null, "MODEL_UNAVAILABLE",
                true, OffsetDateTime.now(), "NOT_SUBMITTED"));
        });

        var result = service.create(userId, IdentificationMode.GENERAL_INSECT, null, true, upload, "request-1");

        verify(scans).insert(any(UUID.class), eq(userId), eq(IdentificationMode.GENERAL_INSECT), isNull(),
            eq("new/image-key.jpg"), eq(true), argThat(aiResult -> "UNKNOWN".equals(aiResult.status())
                && "MODEL_UNAVAILABLE".equals(aiResult.reason()) && aiResult.prediction() == null
                && aiResult.model() == null), isNull());
        org.assertj.core.api.Assertions.assertThat(result.status()).isEqualTo("UNKNOWN");
        org.assertj.core.api.Assertions.assertThat(result.crop()).isNull();
        org.assertj.core.api.Assertions.assertThat(result.pest()).isNull();
        org.assertj.core.api.Assertions.assertThat(result.model()).isNull();
    }

    @Test
    void generalInsectPreservesImageRejectionWithoutRiceModelMetadata() {
        IdentifyResponse rejected = new IdentifyResponse("REJECTED_IMAGE", "TOO_BLURRY", null,
            new Model("rice-only-model", "1.0.0", "rice-v1"));
        when(ai.identify(sanitized, "GENERAL_INSECT", null, "request-1")).thenReturn(rejected);
        when(scans.get(any(UUID.class), eq(userId))).thenAnswer(invocation -> {
            UUID id = invocation.getArgument(0);
            return Optional.of(new ScanRepository.Row(id, userId, IdentificationMode.GENERAL_INSECT,
                null, null, null, null, false, "new/image-key.jpg", "REJECTED_IMAGE", OffsetDateTime.now(),
                null, null, null, null, null, null, "TOO_BLURRY", false, null, "NOT_SUBMITTED"));
        });

        var result = service.create(userId, IdentificationMode.GENERAL_INSECT, null, false, upload, "request-1");

        verify(scans).insert(any(UUID.class), eq(userId), eq(IdentificationMode.GENERAL_INSECT), isNull(),
            eq("new/image-key.jpg"), eq(false), argThat(aiResult -> "REJECTED_IMAGE".equals(aiResult.status())
                && "TOO_BLURRY".equals(aiResult.reason()) && aiResult.model() == null), isNull());
        org.assertj.core.api.Assertions.assertThat(result.status()).isEqualTo("REJECTED_IMAGE");
        org.assertj.core.api.Assertions.assertThat(result.reason()).isEqualTo("TOO_BLURRY");
        org.assertj.core.api.Assertions.assertThat(result.model()).isNull();
    }
}
