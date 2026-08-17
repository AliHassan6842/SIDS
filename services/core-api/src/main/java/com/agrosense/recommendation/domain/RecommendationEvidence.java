package com.agrosense.recommendation.domain;

public record RecommendationEvidence(
    String source,
    String description,
    Double relevanceScore
) {}
