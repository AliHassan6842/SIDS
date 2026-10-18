package com.agrosense.weather.infrastructure.client;

import com.agrosense.weather.domain.*;
import org.springframework.stereotype.Component;

import java.time.Instant;
import java.time.LocalDate;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.List;
import java.util.Random;

@Component
public class SimulatedWeatherProvider implements WeatherProvider {

    private static final String PROVIDER_NAME = "simulated";

    @Override
    public WeatherData getCurrentWeather(double latitude, double longitude) {
        long seed = (long) (latitude * 1000 + longitude * 100) + (Instant.now().getEpochSecond() / 3600);
        Random random = new Random(seed);

        double tempBase = 22.0 - (Math.abs(latitude) * 0.2);
        double temp = Math.round((tempBase + (random.nextDouble() * 8.0 - 4.0)) * 10.0) / 10.0;
        double humidity = Math.round((55.0 + random.nextDouble() * 35.0) * 10.0) / 10.0;
        double precipitation = random.nextDouble() < 0.25 ? Math.round(random.nextDouble() * 5.0 * 10.0) / 10.0 : 0.0;
        double windSpeed = Math.round((2.0 + random.nextDouble() * 12.0) * 10.0) / 10.0;
        double windDirection = Math.round(random.nextDouble() * 360.0);
        double pressure = Math.round((1010.0 + random.nextDouble() * 15.0) * 10.0) / 10.0;
        double solarRadiation = Math.round(200.0 + random.nextDouble() * 600.0);
        double uvIndex = Math.round((1.0 + random.nextDouble() * 8.0) * 10.0) / 10.0;

        WeatherCondition condition;
        if (precipitation > 3.0) {
            condition = WeatherCondition.HEAVY_RAIN;
        } else if (precipitation > 0) {
            condition = WeatherCondition.RAIN;
        } else if (humidity > 80.0) {
            condition = WeatherCondition.OVERCAST;
        } else if (humidity > 65.0) {
            condition = WeatherCondition.PARTLY_CLOUDY;
        } else {
            condition = WeatherCondition.CLEAR;
        }

        return WeatherData.builder()
                .temperature(temp)
                .humidity(humidity)
                .precipitation(precipitation)
                .windSpeed(windSpeed)
                .windDirection(windDirection)
                .surfacePressure(pressure)
                .solarRadiation(solarRadiation)
                .uvIndex(uvIndex)
                .condition(condition)
                .provider(PROVIDER_NAME)
                .timestamp(Instant.now())
                .rawMetadata("{\"source\":\"simulated\",\"seed\":" + seed + "}")
                .build();
    }

    @Override
    public List<WeatherForecast> getDailyForecast(double latitude, double longitude, int days) {
        List<WeatherForecast> forecasts = new ArrayList<>();
        LocalDate startDate = LocalDate.now();

        for (int i = 0; i < days; i++) {
            LocalDate date = startDate.plusDays(i);
            long seed = (long) (latitude * 1000 + longitude * 100) + date.toEpochDay();
            Random random = new Random(seed);

            double baseTemp = 20.0 - (Math.abs(latitude) * 0.2);
            double minTemp = Math.round((baseTemp - 4.0 + random.nextDouble() * 3.0) * 10.0) / 10.0;
            double maxTemp = Math.round((baseTemp + 6.0 + random.nextDouble() * 5.0) * 10.0) / 10.0;
            double avgTemp = Math.round(((minTemp + maxTemp) / 2.0) * 10.0) / 10.0;
            double precipProb = Math.round(random.nextDouble() * 70.0);
            double precipSum = precipProb > 40.0 ? Math.round(random.nextDouble() * 8.0 * 10.0) / 10.0 : 0.0;
            double maxWind = Math.round((5.0 + random.nextDouble() * 15.0) * 10.0) / 10.0;
            double avgHumidity = Math.round((50.0 + random.nextDouble() * 40.0) * 10.0) / 10.0;
            double maxUv = Math.round((3.0 + random.nextDouble() * 6.0) * 10.0) / 10.0;

            WeatherCondition condition;
            if (precipSum > 5.0) {
                condition = WeatherCondition.HEAVY_RAIN;
            } else if (precipSum > 0.5) {
                condition = WeatherCondition.RAIN;
            } else if (avgHumidity > 75.0) {
                condition = WeatherCondition.OVERCAST;
            } else {
                condition = WeatherCondition.PARTLY_CLOUDY;
            }

            forecasts.add(WeatherForecast.builder()
                    .date(date)
                    .minTemperature(minTemp)
                    .maxTemperature(maxTemp)
                    .averageTemperature(avgTemp)
                    .precipitationProbability(precipProb)
                    .precipitationSum(precipSum)
                    .maxWindSpeed(maxWind)
                    .averageHumidity(avgHumidity)
                    .uvIndexMax(maxUv)
                    .condition(condition)
                    .build());
        }

        return forecasts;
    }

    @Override
    public List<WeatherAlert> getAlerts(double latitude, double longitude) {
        List<WeatherAlert> alerts = new ArrayList<>();
        WeatherData current = getCurrentWeather(latitude, longitude);

        if (current.windSpeed() != null && current.windSpeed() > 12.0) {
            alerts.add(new WeatherAlert(
                    "ALERT-WIND-" + System.currentTimeMillis() % 10000,
                    "High Wind Warning",
                    "Wind speeds exceeding " + current.windSpeed() + " m/s detected. Exercise caution when spraying.",
                    WeatherAlert.Severity.WARNING,
                    WeatherAlert.Category.WIND,
                    Instant.now(),
                    Instant.now().plus(6, ChronoUnit.HOURS),
                    PROVIDER_NAME
            ));
        }

        if (current.precipitation() != null && current.precipitation() > 4.0) {
            alerts.add(new WeatherAlert(
                    "ALERT-RAIN-" + System.currentTimeMillis() % 10000,
                    "Heavy Rainfall Alert",
                    "Heavy rain may cause soil waterlogging and increase fungal disease risk.",
                    WeatherAlert.Severity.WARNING,
                    WeatherAlert.Category.RAIN,
                    Instant.now(),
                    Instant.now().plus(12, ChronoUnit.HOURS),
                    PROVIDER_NAME
            ));
        }

        return alerts;
    }

    @Override
    public WeatherData getHistoricalWeather(double latitude, double longitude, Instant timestamp) {
        long seed = (long) (latitude * 1000 + longitude * 100) + (timestamp.getEpochSecond() / 3600);
        Random random = new Random(seed);

        double temp = Math.round((18.0 + random.nextDouble() * 10.0) * 10.0) / 10.0;
        double humidity = Math.round((60.0 + random.nextDouble() * 30.0) * 10.0) / 10.0;

        return WeatherData.builder()
                .temperature(temp)
                .humidity(humidity)
                .precipitation(0.0)
                .windSpeed(4.5)
                .condition(WeatherCondition.CLEAR)
                .provider(PROVIDER_NAME)
                .timestamp(timestamp)
                .build();
    }

    @Override
    public String getProviderName() {
        return PROVIDER_NAME;
    }
}
