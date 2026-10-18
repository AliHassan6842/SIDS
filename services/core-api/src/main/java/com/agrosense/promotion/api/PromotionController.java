package com.agrosense.promotion.api;

import static com.agrosense.promotion.api.PromotionDtos.*;

import com.agrosense.promotion.application.PromotionService;
import com.agrosense.shared.security.CurrentUser;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/model-promotions")
public class PromotionController {
    private final PromotionService promotions;

    public PromotionController(PromotionService promotions) {
        this.promotions = promotions;
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public PromotionResponse promote(@AuthenticationPrincipal CurrentUser user,
                                     @Valid @RequestBody PromotionRequest request) {
        return promotions.promote(user.id(), request);
    }
}
