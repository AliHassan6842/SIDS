package com.agrosense.agronomy.domain;

public record DecisionResult(
    DecisionState state,
    String reason,
    Double confidence
) {}
