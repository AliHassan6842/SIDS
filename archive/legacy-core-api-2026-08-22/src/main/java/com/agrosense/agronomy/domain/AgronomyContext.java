package com.agrosense.agronomy.domain;

public record AgronomyContext(
    String crop,
    String pest,
    String growthStage,
    Double pestDensity,
    Double cropDamagePercentage,
    boolean hasWeatherAlert
) {}
