package com.agrosense.weather.infrastructure.config;

import org.springframework.boot.context.properties.ConfigurationProperties;

@ConfigurationProperties(prefix = "agrosense.weather")
public class WeatherProperties {

    /**
     * Provider type: "open-meteo" or "simulated".
     */
    private String provider = "open-meteo";

    /**
     * Cache time-to-live in seconds (default: 1800 = 30 minutes).
     */
    private long cacheTtlSeconds = 1800;

    /**
     * Base URL for Open-Meteo API.
     */
    private String openMeteoBaseUrl = "https://api.open-meteo.com";

    /**
     * HTTP request timeout in seconds.
     */
    private int timeoutSeconds = 5;

    public String getProvider() {
        return provider;
    }

    public void setProvider(String provider) {
        this.provider = provider;
    }

    public long getCacheTtlSeconds() {
        return cacheTtlSeconds;
    }

    public void setCacheTtlSeconds(long cacheTtlSeconds) {
        this.cacheTtlSeconds = cacheTtlSeconds;
    }

    public String getOpenMeteoBaseUrl() {
        return openMeteoBaseUrl;
    }

    public void setOpenMeteoBaseUrl(String openMeteoBaseUrl) {
        this.openMeteoBaseUrl = openMeteoBaseUrl;
    }

    public int getTimeoutSeconds() {
        return timeoutSeconds;
    }

    public void setTimeoutSeconds(int timeoutSeconds) {
        this.timeoutSeconds = timeoutSeconds;
    }
}
