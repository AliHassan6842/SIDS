package com.agrosense.review.application;

import static com.agrosense.review.api.ReviewDtos.*;

import com.agrosense.identity.application.StaffAuthorizationService;
import com.agrosense.identity.domain.SystemRole;
import com.agrosense.review.infrastructure.ReviewRepository;
import com.agrosense.shared.error.ApiException;
import com.agrosense.storage.PrivateImageStorage;
import java.time.OffsetDateTime;
import java.util.List;
import java.util.Set;
import java.util.UUID;
import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class ReviewService {
    private static final Set<String> REVIEW_STATUSES = Set.of("PENDING", "APPROVED", "REJECTED");
    private final ReviewRepository reviews;
    private final StaffAuthorizationService staff;
    private final PrivateImageStorage storage;

    public ReviewService(ReviewRepository reviews, StaffAuthorizationService staff, PrivateImageStorage storage) {
        this.reviews = reviews;
        this.staff = staff;
        this.storage = storage;
    }

    @Transactional
    public TrainingConsentResponse setConsent(UUID scanId, UUID ownerId, boolean consented) {
        var scan = ownedScan(scanId, ownerId);
        OffsetDateTime now = OffsetDateTime.now();
        reviews.setConsent(scanId, ownerId, consented, now);
        var refreshed = ownedScan(scanId, ownerId);
        return new TrainingConsentResponse(scanId, refreshed.trainingConsent(), refreshed.consentedAt(),
            reviews.latestStatus(scanId));
    }

    @Transactional
    public ReviewResponse submit(UUID scanId, UUID ownerId, ReviewSubmissionRequest request) {
        var scan = ownedScan(scanId, ownerId);
        if (!scan.trainingConsent()) throw new ApiException(HttpStatus.CONFLICT, "TRAINING_CONSENT_REQUIRED",
            "Training consent is required before review submission.", false);
        if ("REJECTED_IMAGE".equals(scan.status()) || "FAILED".equals(scan.status()))
            throw new ApiException(HttpStatus.CONFLICT, "SCAN_NOT_REVIEWABLE",
                "Rejected or failed scans cannot enter the review queue.", false);
        try {
            return reviews.submit(scan, ownerId, clean(request.proposedLabelSlug()), clean(request.notes()));
        } catch (DataIntegrityViolationException exception) {
            throw new ApiException(HttpStatus.CONFLICT, "REVIEW_ALREADY_PENDING",
                "This scan already has a pending review.", false);
        }
    }

    public List<ReviewResponse> queue(UUID reviewerId, String status) {
        staff.requireReviewer(reviewerId);
        String normalized = status == null ? "PENDING" : status.toUpperCase(java.util.Locale.ROOT);
        if (!REVIEW_STATUSES.contains(normalized)) throw new ApiException(HttpStatus.BAD_REQUEST,
            "INVALID_REVIEW_STATUS", "Review status is invalid.", false);
        return reviews.queue(normalized);
    }

    @Transactional
    public ReviewResponse claim(UUID reviewId, UUID reviewerId) {
        staff.requireReviewer(reviewerId);
        ReviewResponse existing = review(reviewId);
        if (!"PENDING".equals(existing.status())) throw reviewConflict();
        if (reviewerId.equals(existing.assignedReviewerId())) return existing;
        if (existing.assignedReviewerId() != null || !reviews.claim(reviewId, reviewerId, OffsetDateTime.now()))
            throw reviewConflict();
        return review(reviewId);
    }

    @Transactional
    public ReviewResponse decide(UUID reviewId, UUID reviewerId, ReviewDecisionRequest request) {
        staff.requireReviewer(reviewerId);
        String label = clean(request.labelSlug());
        if (request.decision() == ReviewDecision.APPROVED && label == null)
            throw new ApiException(HttpStatus.BAD_REQUEST, "REVIEW_LABEL_REQUIRED",
                "An approved review requires a reviewer label.", false);
        if (request.decision() == ReviewDecision.REJECTED && label != null)
            throw new ApiException(HttpStatus.BAD_REQUEST, "REJECTED_REVIEW_HAS_LABEL",
                "A rejected review cannot publish a reviewer label.", false);
        if (!reviews.decide(reviewId, reviewerId, request.decision().name(), label,
            clean(request.notes()), OffsetDateTime.now())) throw reviewConflict();
        return review(reviewId);
    }

    public byte[] image(UUID reviewId, UUID reviewerId) {
        SystemRole role = staff.requireReviewer(reviewerId);
        String key = reviews.assignedImageKey(reviewId, reviewerId, role == SystemRole.ADMIN)
            .orElseThrow(() -> new ApiException(HttpStatus.NOT_FOUND, "REVIEW_NOT_FOUND",
                "Review was not found for the assigned reviewer.", false));
        return storage.read(key);
    }

    private ReviewRepository.ScanIntake ownedScan(UUID scanId, UUID ownerId) {
        return reviews.ownedScan(scanId, ownerId).orElseThrow(() -> new ApiException(HttpStatus.NOT_FOUND,
            "SCAN_NOT_FOUND", "Scan was not found.", false));
    }

    private ReviewResponse review(UUID reviewId) {
        return reviews.get(reviewId).orElseThrow(() -> new ApiException(HttpStatus.NOT_FOUND,
            "REVIEW_NOT_FOUND", "Review was not found.", false));
    }

    private ApiException reviewConflict() {
        return new ApiException(HttpStatus.CONFLICT, "REVIEW_NOT_AVAILABLE",
            "Review is already assigned or no longer pending.", false);
    }

    private String clean(String value) {
        if (value == null || value.isBlank()) return null;
        return value.trim();
    }
}
