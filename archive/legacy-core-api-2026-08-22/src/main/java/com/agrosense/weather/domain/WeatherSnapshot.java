package com.agrosense.weather.domain;

import java.time.Instant;
import java.util.Objects;
import java.util.UUID;

public class WeatherSnapshot {
    private final UUID id;
    private final UUID fieldId;
    private final Double temperature;
    private final Double humidity;
    private final Double precipitation;
    private final Double wind;
    private final String provider;
    private final String rawMetadata;
    private final Instant timestamp;

    public WeatherSnapshot(
            UUID id,
            UUID fieldId,
            Double temperature,
            Double humidity,
            Double precipitation,
            Double wind,
            String provider,
            String rawMetadata,
            Instant timestamp
    ) {
        this.id = id != null ? id : UUID.randomUUID();
        this.fieldId = Objects.requireNonNull(fieldId, "fieldId must not be null");
        this.temperature = temperature;
        this.humidity = humidity;
        this.precipitation = precipitation;
        this.wind = wind;
        this.provider = provider != null ? provider : "unknown";
        this.rawMetadata = rawMetadata;
        this.timestamp = timestamp != null ? timestamp : Instant.now();
    }

    public static WeatherSnapshot fromWeatherData(UUID fieldId, WeatherData weatherData) {
        Objects.requireNonNull(fieldId, "fieldId must not be null");
        Objects.requireNonNull(weatherData, "weatherData must not be null");
        return new WeatherSnapshot(
                UUID.randomUUID(),
                fieldId,
                weatherData.temperature(),
                weatherData.humidity(),
                weatherData.precipitation(),
                weatherData.windSpeed(),
                weatherData.provider(),
                weatherData.rawMetadata(),
                weatherData.timestamp()
        );
    }

    public UUID getId() {
        return id;
    }

    public UUID getFieldId() {
        return fieldId;
    }

    public Double getTemperature() {
        return temperature;
    }

    public Double getHumidity() {
        return humidity;
    }

    public Double getPrecipitation() {
        return precipitation;
    }

    public Double getWind() {
        return wind;
    }

    public String getProvider() {
        return provider;
    }

    public String getRawMetadata() {
        return rawMetadata;
    }

    public Instant getTimestamp() {
        return timestamp;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        WeatherSnapshot that = (WeatherSnapshot) o;
        return Objects.equals(id, that.id);
    }

    @Override
    public int hashCode() {
        return Objects.hash(id);
    }

    @Override
    public String toString() {
        return "WeatherSnapshot{" +
                "id=" + id +
                ", fieldId=" + fieldId +
                ", temperature=" + temperature +
                ", humidity=" + humidity +
                ", precipitation=" + precipitation +
                ", wind=" + wind +
                ", provider='" + provider + '\'' +
                ", timestamp=" + timestamp +
                '}';
    }
}
