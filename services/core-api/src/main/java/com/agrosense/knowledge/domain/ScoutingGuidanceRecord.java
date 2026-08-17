package com.agrosense.knowledge.domain;

public record ScoutingGuidanceRecord(
    Long id,
    String crop,
    String pest,
    String growthStage,
    String scoutingMethod,
    String description
) {}
