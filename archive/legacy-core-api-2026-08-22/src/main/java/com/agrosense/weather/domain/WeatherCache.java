package com.agrosense.weather.domain;

import java.util.Optional;

/**
 * Port interface for caching weather data by geographic coordinates.
 */
public interface WeatherCache {

    /**
     * Retrieves cached weather data for the specified latitude and longitude if present and not expired.
     */
    Optional<WeatherData> get(double latitude, double longitude);

    /**
     * Stores weather data in cache with a specified time-to-live in seconds.
     */
    void put(double latitude, double longitude, WeatherData data, long ttlSeconds);

    /**
     * Evicts cached weather data for the specified coordinates.
     */
    void evict(double latitude, double longitude);

    /**
     * Clears all cached weather entries.
     */
    void clear();
}
