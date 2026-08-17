package com.agrosense.weather.domain;

import java.time.Instant;

public record WeatherData(
        Double temperature,
        Double humidity,
        Double precipitation,
        Double windSpeed,
        Double windDirection,
        Double surfacePressure,
        Double solarRadiation,
        Double uvIndex,
        WeatherCondition condition,
        String provider,
        Instant timestamp,
        String rawMetadata
) {
    public static Builder builder() {
        return new Builder();
    }

    public static class Builder {
        private Double temperature;
        private Double humidity;
        private Double precipitation;
        private Double windSpeed;
        private Double windDirection;
        private Double surfacePressure;
        private Double solarRadiation;
        private Double uvIndex;
        private WeatherCondition condition = WeatherCondition.UNKNOWN;
        private String provider = "unknown";
        private Instant timestamp = Instant.now();
        private String rawMetadata;

        public Builder temperature(Double temperature) {
            this.temperature = temperature;
            return this;
        }

        public Builder humidity(Double humidity) {
            this.humidity = humidity;
            return this;
        }

        public Builder precipitation(Double precipitation) {
            this.precipitation = precipitation;
            return this;
        }

        public Builder windSpeed(Double windSpeed) {
            this.windSpeed = windSpeed;
            return this;
        }

        public Builder windDirection(Double windDirection) {
            this.windDirection = windDirection;
            return this;
        }

        public Builder surfacePressure(Double surfacePressure) {
            this.surfacePressure = surfacePressure;
            return this;
        }

        public Builder solarRadiation(Double solarRadiation) {
            this.solarRadiation = solarRadiation;
            return this;
        }

        public Builder uvIndex(Double uvIndex) {
            this.uvIndex = uvIndex;
            return this;
        }

        public Builder condition(WeatherCondition condition) {
            this.condition = condition;
            return this;
        }

        public Builder provider(String provider) {
            this.provider = provider;
            return this;
        }

        public Builder timestamp(Instant timestamp) {
            this.timestamp = timestamp;
            return this;
        }

        public Builder rawMetadata(String rawMetadata) {
            this.rawMetadata = rawMetadata;
            return this;
        }

        public WeatherData build() {
            return new WeatherData(
                    temperature,
                    humidity,
                    precipitation,
                    windSpeed,
                    windDirection,
                    surfacePressure,
                    solarRadiation,
                    uvIndex,
                    condition,
                    provider,
                    timestamp != null ? timestamp : Instant.now(),
                    rawMetadata
            );
        }
    }
}
