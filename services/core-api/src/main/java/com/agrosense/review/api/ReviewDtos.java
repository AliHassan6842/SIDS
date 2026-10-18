package com.agrosense.review.api;

import com.agrosense.scan.domain.IdentificationMode;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;
import java.time.OffsetDateTime;
import java.util.UUID;

public final class ReviewDtos {
    private static final String SLUG = "^[a-z0-9]+(?:-[a-z0-9]+)*$";
    private ReviewDtos() {}

    public record TrainingConsentRequest(@NotNull Boolean trainingConsent) {}
    public record TrainingConsentResponse(UUID scanId, boolean trainingConsent, OffsetDateTime consentedAt,
                                          String reviewStatus) {}
    public record ReviewSubmissionRequest(
        @Size(max=96) @Pattern(regexp=SLUG) String proposedLabelSlug,
        @Size(max=1000) String notes) {}
    public record ReviewDecisionRequest(
        @NotNull ReviewDecision decision,
        @Size(max=96) @Pattern(regexp=SLUG) String labelSlug,
        @Size(max=1000) String notes) {}
    public enum ReviewDecision { APPROVED, REJECTED }
    public record ReviewResponse(UUID id, UUID scanId, UUID submittedBy, IdentificationMode mode,
                                 String scanStatus, String proposedLabelSlug, String submissionNotes,
                                 String status, UUID assignedReviewerId, String reviewerLabelSlug,
                                 String reviewerNotes, OffsetDateTime claimedAt, OffsetDateTime reviewedAt,
                                 OffsetDateTime createdAt) {}
}
