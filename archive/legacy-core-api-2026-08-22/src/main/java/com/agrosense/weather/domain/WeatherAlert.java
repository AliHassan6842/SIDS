package com.agrosense.weather.domain;

import java.time.Instant;

public record WeatherAlert(
        String id,
        String title,
        String description,
        Severity severity,
        Category category,
        Instant effectiveFrom,
        Instant effectiveTo,
        String source
) {
    public enum Severity {
        INFO,
        WARNING,
        CRITICAL,
        EXTREME
    }

    public enum Category {
        RAIN,
        WIND,
        FROST,
        HEAT,
        DROUGHT,
        STORM,
        HAIL,
        OTHER
    }
}
