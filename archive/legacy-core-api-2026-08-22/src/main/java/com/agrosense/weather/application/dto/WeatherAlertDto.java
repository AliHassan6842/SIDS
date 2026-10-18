package com.agrosense.weather.application.dto;

import com.agrosense.weather.domain.WeatherAlert;
import java.time.Instant;

public record WeatherAlertDto(
        String id,
        String title,
        String description,
        String severity,
        String category,
        Instant effectiveFrom,
        Instant effectiveTo,
        String source
) {
    public static WeatherAlertDto fromDomain(WeatherAlert alert) {
        if (alert == null) {
            return null;
        }
        return new WeatherAlertDto(
                alert.id(),
                alert.title(),
                alert.description(),
                alert.severity() != null ? alert.severity().name() : "INFO",
                alert.category() != null ? alert.category().name() : "OTHER",
                alert.effectiveFrom(),
                alert.effectiveTo(),
                alert.source()
        );
    }
}
