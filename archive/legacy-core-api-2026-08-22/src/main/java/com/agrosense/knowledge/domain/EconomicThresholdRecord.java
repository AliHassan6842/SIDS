package com.agrosense.knowledge.domain;

public record EconomicThresholdRecord(
    Long id,
    String crop,
    String pest,
    Double thresholdValue,
    String unit,
    String description
) {}
