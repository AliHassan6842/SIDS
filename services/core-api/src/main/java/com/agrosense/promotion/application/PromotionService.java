package com.agrosense.promotion.application;

import static com.agrosense.promotion.api.PromotionDtos.*;

import com.agrosense.identity.application.StaffAuthorizationService;
import com.agrosense.promotion.infrastructure.PromotionRepository;
import com.agrosense.review.infrastructure.ReviewRepository;
import com.agrosense.shared.error.ApiException;
import java.time.OffsetDateTime;
import java.util.HashSet;
import java.util.UUID;
import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class PromotionService {
    private final PromotionRepository promotions;
    private final ReviewRepository reviews;
    private final StaffAuthorizationService staff;

    public PromotionService(PromotionRepository promotions, ReviewRepository reviews,
                            StaffAuthorizationService staff) {
        this.promotions = promotions;
        this.reviews = reviews;
        this.staff = staff;
    }

    @Transactional
    public PromotionResponse promote(UUID actorId, PromotionRequest request) {
        staff.requireAdmin(actorId);
        if (new HashSet<>(request.reviewIds()).size() != request.reviewIds().size())
            throw invalid("DUPLICATE_PROMOTION_REVIEW", "reviewIds must not contain duplicates.");
        for (UUID reviewId : request.reviewIds()) {
            if (!reviews.approvedAndConsented(reviewId)) throw invalid("REVIEW_NOT_PROMOTABLE",
                "Every promotion review must be approved and currently consented.");
        }
        if (request.supersedesPromotionId() != null) {
            PromotionResponse previous = promotions.get(request.supersedesPromotionId()).orElseThrow(() ->
                invalid("PROMOTION_NOT_FOUND", "The superseded promotion was not found."));
            if (!previous.modelId().equals(request.modelId())) throw invalid("PROMOTION_MODEL_MISMATCH",
                "A promotion may only supersede the same model id.");
        }
        try {
            return promotions.insert(UUID.randomUUID(), request, actorId, OffsetDateTime.now());
        } catch (DataIntegrityViolationException exception) {
            throw new ApiException(HttpStatus.CONFLICT, "PROMOTION_ALREADY_EXISTS",
                "This model and dataset version is already promoted.", false);
        }
    }

    private ApiException invalid(String code, String message) {
        return new ApiException(HttpStatus.BAD_REQUEST, code, message, false);
    }
}
