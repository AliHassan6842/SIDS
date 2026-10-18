package com.agrosense.review.api;

import static com.agrosense.review.api.ReviewDtos.*;

import com.agrosense.review.application.ReviewService;
import com.agrosense.shared.security.CurrentUser;
import jakarta.validation.Valid;
import java.util.List;
import java.util.UUID;
import org.springframework.http.CacheControl;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1")
public class ReviewController {
    private final ReviewService reviews;

    public ReviewController(ReviewService reviews) {
        this.reviews = reviews;
    }

    @PutMapping("/scans/{scanId}/training-consent")
    public TrainingConsentResponse consent(@AuthenticationPrincipal CurrentUser user, @PathVariable UUID scanId,
                                            @Valid @RequestBody TrainingConsentRequest request) {
        return reviews.setConsent(scanId, user.id(), request.trainingConsent());
    }

    @PostMapping("/scans/{scanId}/review-submission")
    public ResponseEntity<ReviewResponse> submit(@AuthenticationPrincipal CurrentUser user, @PathVariable UUID scanId,
                                                  @Valid @RequestBody ReviewSubmissionRequest request) {
        return ResponseEntity.status(201).body(reviews.submit(scanId, user.id(), request));
    }

    @GetMapping("/reviews")
    public List<ReviewResponse> queue(@AuthenticationPrincipal CurrentUser user,
                                      @RequestParam(defaultValue="PENDING") String status) {
        return reviews.queue(user.id(), status);
    }

    @PostMapping("/reviews/{reviewId}/claim")
    public ReviewResponse claim(@AuthenticationPrincipal CurrentUser user, @PathVariable UUID reviewId) {
        return reviews.claim(reviewId, user.id());
    }

    @PostMapping("/reviews/{reviewId}/decision")
    public ReviewResponse decide(@AuthenticationPrincipal CurrentUser user, @PathVariable UUID reviewId,
                                  @Valid @RequestBody ReviewDecisionRequest request) {
        return reviews.decide(reviewId, user.id(), request);
    }

    @GetMapping(value="/reviews/{reviewId}/image", produces=MediaType.IMAGE_JPEG_VALUE)
    public ResponseEntity<byte[]> image(@AuthenticationPrincipal CurrentUser user, @PathVariable UUID reviewId) {
        return ResponseEntity.ok().cacheControl(CacheControl.noStore()).body(reviews.image(reviewId, user.id()));
    }
}
