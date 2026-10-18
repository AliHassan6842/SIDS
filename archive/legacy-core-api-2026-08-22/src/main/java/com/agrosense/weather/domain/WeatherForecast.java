package com.agrosense.weather.domain;

import java.time.LocalDate;

public record WeatherForecast(
        LocalDate date,
        Double minTemperature,
        Double maxTemperature,
        Double averageTemperature,
        Double precipitationProbability,
        Double precipitationSum,
        Double maxWindSpeed,
        Double averageHumidity,
        Double uvIndexMax,
        WeatherCondition condition
) {
    public static Builder builder() {
        return new Builder();
    }

    public static class Builder {
        private LocalDate date;
        private Double minTemperature;
        private Double maxTemperature;
        private Double averageTemperature;
        private Double precipitationProbability;
        private Double precipitationSum;
        private Double maxWindSpeed;
        private Double averageHumidity;
        private Double uvIndexMax;
        private WeatherCondition condition = WeatherCondition.UNKNOWN;

        public Builder date(LocalDate date) {
            this.date = date;
            return this;
        }

        public Builder minTemperature(Double minTemperature) {
            this.minTemperature = minTemperature;
            return this;
        }

        public Builder maxTemperature(Double maxTemperature) {
            this.maxTemperature = maxTemperature;
            return this;
        }

        public Builder averageTemperature(Double averageTemperature) {
            this.averageTemperature = averageTemperature;
            return this;
        }

        public Builder precipitationProbability(Double precipitationProbability) {
            this.precipitationProbability = precipitationProbability;
            return this;
        }

        public Builder precipitationSum(Double precipitationSum) {
            this.precipitationSum = precipitationSum;
            return this;
        }

        public Builder maxWindSpeed(Double maxWindSpeed) {
            this.maxWindSpeed = maxWindSpeed;
            return this;
        }

        public Builder averageHumidity(Double averageHumidity) {
            this.averageHumidity = averageHumidity;
            return this;
        }

        public Builder uvIndexMax(Double uvIndexMax) {
            this.uvIndexMax = uvIndexMax;
            return this;
        }

        public Builder condition(WeatherCondition condition) {
            this.condition = condition;
            return this;
        }

        public WeatherForecast build() {
            return new WeatherForecast(
                    date,
                    minTemperature,
                    maxTemperature,
                    averageTemperature,
                    precipitationProbability,
                    precipitationSum,
                    maxWindSpeed,
                    averageHumidity,
                    uvIndexMax,
                    condition
            );
        }
    }
}
