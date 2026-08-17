package com.agrosense.weather.domain;

import java.time.Instant;
import java.util.List;

/**
 * Port interface for fetching weather data from external providers.
 */
public interface WeatherProvider {

    /**
     * Gets current weather conditions for the specified latitude and longitude.
     */
    WeatherData getCurrentWeather(double latitude, double longitude);

    /**
     * Gets daily forecast for the specified location for given number of days.
     */
    List<WeatherForecast> getDailyForecast(double latitude, double longitude, int days);

    /**
     * Gets active weather alerts/warnings for the specified location.
     */
    List<WeatherAlert> getAlerts(double latitude, double longitude);

    /**
     * Gets historical weather data for a specific location and timestamp.
     */
    WeatherData getHistoricalWeather(double latitude, double longitude, Instant timestamp);

    /**
     * Returns the name or identifier of this weather provider.
     */
    String getProviderName();

    /**
     * Returns true if the provider is currently operational.
     */
    default boolean isAvailable() {
        return true;
    }
}
