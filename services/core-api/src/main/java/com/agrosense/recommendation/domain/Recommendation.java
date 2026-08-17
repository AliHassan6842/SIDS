package com.agrosense.recommendation.domain;

import java.util.List;

public record Recommendation(
    String title,
    String description,
    RecommendationPolicy policy,
    List<RecommendationEvidence> evidences
) {}
