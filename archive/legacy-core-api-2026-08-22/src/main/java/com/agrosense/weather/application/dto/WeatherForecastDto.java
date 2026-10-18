package com.agrosense.weather.application.dto;

import com.agrosense.weather.domain.WeatherForecast;
import java.time.LocalDate;

public record WeatherForecastDto(
        LocalDate date,
        Double minTemperature,
        Double maxTemperature,
        Double averageTemperature,
        Double precipitationProbability,
        Double precipitationSum,
        Double maxWindSpeed,
        Double averageHumidity,
        Double uvIndexMax,
        String condition,
        String conditionDescription
) {
    public static WeatherForecastDto fromDomain(WeatherForecast forecast) {
        if (forecast == null) {
            return null;
        }
        return new WeatherForecastDto(
                forecast.date(),
                forecast.minTemperature(),
                forecast.maxTemperature(),
                forecast.averageTemperature(),
                forecast.precipitationProbability(),
                forecast.precipitationSum(),
                forecast.maxWindSpeed(),
                forecast.averageHumidity(),
                forecast.uvIndexMax(),
                forecast.condition() != null ? forecast.condition().name() : "UNKNOWN",
                forecast.condition() != null ? forecast.condition().getDescription() : "Unknown"
        );
    }
}
