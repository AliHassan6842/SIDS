package com.agrosense.weather.application.dto;

import com.agrosense.weather.domain.WeatherData;
import java.time.Instant;

public record CurrentWeatherDto(
        Double temperature,
        Double humidity,
        Double precipitation,
        Double windSpeed,
        Double windDirection,
        Double surfacePressure,
        Double solarRadiation,
        Double uvIndex,
        String condition,
        String conditionDescription,
        String provider,
        Instant timestamp
) {
    public static CurrentWeatherDto fromDomain(WeatherData data) {
        if (data == null) {
            return null;
        }
        return new CurrentWeatherDto(
                data.temperature(),
                data.humidity(),
                data.precipitation(),
                data.windSpeed(),
                data.windDirection(),
                data.surfacePressure(),
                data.solarRadiation(),
                data.uvIndex(),
                data.condition() != null ? data.condition().name() : "UNKNOWN",
                data.condition() != null ? data.condition().getDescription() : "Unknown",
                data.provider(),
                data.timestamp()
        );
    }
}
