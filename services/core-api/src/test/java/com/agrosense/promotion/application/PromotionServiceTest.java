package com.agrosense.promotion.application;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.Mockito.*;

import com.agrosense.identity.application.StaffAuthorizationService;
import com.agrosense.promotion.api.PromotionDtos.PromotionRequest;
import com.agrosense.promotion.infrastructure.PromotionRepository;
import com.agrosense.review.infrastructure.ReviewRepository;
import com.agrosense.shared.error.ApiException;
import java.util.List;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class PromotionServiceTest {
    private PromotionRepository promotions;
    private ReviewRepository reviews;
    private StaffAuthorizationService staff;
    private PromotionService service;
    private UUID adminId;

    @BeforeEach
    void setUp() {
        promotions = mock(PromotionRepository.class);
        reviews = mock(ReviewRepository.class);
        staff = mock(StaffAuthorizationService.class);
        service = new PromotionService(promotions, reviews, staff);
        adminId = UUID.randomUUID();
    }

    @Test
    void refusesApprovedReviewAfterConsentWithdrawal() {
        UUID reviewId = UUID.randomUUID();
        when(reviews.approvedAndConsented(reviewId)).thenReturn(false);

        assertThatThrownBy(() -> service.promote(adminId, request(List.of(reviewId))))
            .isInstanceOf(ApiException.class)
            .satisfies(error -> assertThat(((ApiException) error).code()).isEqualTo("REVIEW_NOT_PROMOTABLE"));
        verify(staff).requireAdmin(adminId);
        verifyNoInteractions(promotions);
    }

    @Test
    void adminCheckHappensBeforePromotionEvidenceIsRead() {
        doThrow(new ApiException(org.springframework.http.HttpStatus.FORBIDDEN,
            "STAFF_ACCESS_REQUIRED", "Forbidden", false)).when(staff).requireAdmin(adminId);

        assertThatThrownBy(() -> service.promote(adminId, request(List.of(UUID.randomUUID()))))
            .isInstanceOf(ApiException.class)
            .satisfies(error -> assertThat(((ApiException) error).status().value()).isEqualTo(403));
        verifyNoInteractions(reviews, promotions);
    }

    private PromotionRequest request(List<UUID> reviewIds) {
        return new PromotionRequest("sids-detector", "2.0.0", "dataset-v2",
            "a".repeat(64), "b".repeat(64), null, reviewIds);
    }
}
