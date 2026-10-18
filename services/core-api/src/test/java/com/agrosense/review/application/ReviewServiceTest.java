package com.agrosense.review.application;

import static com.agrosense.review.api.ReviewDtos.*;
import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.Mockito.*;

import com.agrosense.identity.application.StaffAuthorizationService;
import com.agrosense.review.infrastructure.ReviewRepository;
import com.agrosense.scan.domain.IdentificationMode;
import com.agrosense.shared.error.ApiException;
import com.agrosense.storage.PrivateImageStorage;
import java.time.OffsetDateTime;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class ReviewServiceTest {
    private ReviewRepository repository;
    private StaffAuthorizationService staff;
    private ReviewService service;
    private UUID ownerId;
    private UUID scanId;

    @BeforeEach
    void setUp() {
        repository = mock(ReviewRepository.class);
        staff = mock(StaffAuthorizationService.class);
        service = new ReviewService(repository, staff, mock(PrivateImageStorage.class));
        ownerId = UUID.randomUUID();
        scanId = UUID.randomUUID();
    }

    @Test
    void userCannotChangeAnotherOwnersConsent() {
        when(repository.ownedScan(scanId, ownerId)).thenReturn(Optional.empty());

        assertThatThrownBy(() -> service.setConsent(scanId, ownerId, true))
            .isInstanceOf(ApiException.class)
            .satisfies(error -> assertThat(((ApiException) error).status().value()).isEqualTo(404));
        verify(repository, never()).setConsent(any(), any(), anyBoolean(), any());
    }

    @Test
    void consentDoesNotSubmitButAllowsUnknownScanSubmission() {
        var scan = new ReviewRepository.ScanIntake(scanId, ownerId, IdentificationMode.GENERAL_INSECT,
            "UNKNOWN", true, OffsetDateTime.now(), "private/key.jpg");
        var expected = response("PENDING");
        when(repository.ownedScan(scanId, ownerId)).thenReturn(Optional.of(scan));
        when(repository.submit(scan, ownerId, null, "Please review")).thenReturn(expected);

        ReviewResponse actual = service.submit(scanId, ownerId,
            new ReviewSubmissionRequest(null, "Please review"));

        assertThat(actual.status()).isEqualTo("PENDING");
        verify(repository).submit(scan, ownerId, null, "Please review");
    }

    @Test
    void submissionRequiresExplicitConsent() {
        var scan = new ReviewRepository.ScanIntake(scanId, ownerId, IdentificationMode.CROP_PEST,
            "UNKNOWN", false, null, "private/key.jpg");
        when(repository.ownedScan(scanId, ownerId)).thenReturn(Optional.of(scan));

        assertThatThrownBy(() -> service.submit(scanId, ownerId, new ReviewSubmissionRequest(null, null)))
            .isInstanceOf(ApiException.class)
            .satisfies(error -> assertThat(((ApiException) error).code()).isEqualTo("TRAINING_CONSENT_REQUIRED"));
        verify(repository, never()).submit(any(), any(), any(), any());
    }

    @Test
    void ordinaryUserIsRejectedBeforeAnyReviewerDataIsReadOrChanged() {
        UUID farmerId = UUID.randomUUID();
        UUID reviewId = UUID.randomUUID();
        doThrow(new ApiException(org.springframework.http.HttpStatus.FORBIDDEN, "STAFF_ACCESS_REQUIRED", "Forbidden", false))
            .when(staff).requireReviewer(farmerId);

        assertThatThrownBy(() -> service.queue(farmerId, "PENDING"))
            .isInstanceOf(ApiException.class)
            .satisfies(error -> assertThat(((ApiException) error).status().value()).isEqualTo(403));
        assertThatThrownBy(() -> service.claim(reviewId, farmerId))
            .isInstanceOf(ApiException.class)
            .satisfies(error -> assertThat(((ApiException) error).status().value()).isEqualTo(403));
        assertThatThrownBy(() -> service.decide(reviewId, farmerId,
            new ReviewDecisionRequest(ReviewDecision.REJECTED, null, null)))
            .isInstanceOf(ApiException.class)
            .satisfies(error -> assertThat(((ApiException) error).status().value()).isEqualTo(403));
        verify(repository, never()).queue(anyString());
        verify(repository, never()).get(any());
        verify(repository, never()).claim(any(), any(), any());
        verify(repository, never()).decide(any(), any(), any(), any(), any(), any());
    }

    private ReviewResponse response(String status) {
        return new ReviewResponse(UUID.randomUUID(), scanId, ownerId, IdentificationMode.GENERAL_INSECT,
            "UNKNOWN", null, "Please review", status, null, null, null, null, null, OffsetDateTime.now());
    }
}
