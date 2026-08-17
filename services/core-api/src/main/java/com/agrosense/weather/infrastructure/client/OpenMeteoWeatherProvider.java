package com.agrosense.weather.infrastructure.client;

import com.agrosense.weather.domain.*;
import com.agrosense.weather.infrastructure.config.WeatherProperties;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.context.annotation.Primary;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;

import java.time.Duration;
import java.time.Instant;
import java.time.LocalDate;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

@Component
@Primary
@ConditionalOnProperty(name = "agrosense.weather.provider", havingValue = "open-meteo", matchIfMissing = true)
public class OpenMeteoWeatherProvider implements WeatherProvider {

    private static final Logger log = LoggerFactory.getLogger(OpenMeteoWeatherProvider.class);
    private static final String PROVIDER_NAME = "open-meteo";

    private final RestClient restClient;
    private final WeatherProperties properties;
    private final SimulatedWeatherProvider fallbackProvider;
    private final ObjectMapper objectMapper;

    public OpenMeteoWeatherProvider(
            WeatherProperties properties,
            SimulatedWeatherProvider fallbackProvider,
            ObjectMapper objectMapper
    ) {
        this.properties = properties;
        this.fallbackProvider = fallbackProvider;
        this.objectMapper = objectMapper;
        this.restClient = RestClient.builder()
                .baseUrl(properties.getOpenMeteoBaseUrl())
                .build();
    }

    @Override
    public WeatherData getCurrentWeather(double latitude, double longitude) {
        try {
            String uri = String.format(
                    Locale.ROOT,
                    "/v1/forecast?latitude=%.4f&longitude=%.4f&current=temperature_2m,relative_humidity_2m,precipitation,surface_pressure,wind_speed_10m,wind_direction_10m,weather_code,direct_radiation,uv_index&timezone=auto",
                    latitude,
                    longitude
            );

            String responseBody = restClient.get()
                    .uri(uri)
                    .retrieve()
                    .body(String.class);

            if (responseBody != null) {
                JsonNode root = objectMapper.readTree(responseBody);
                JsonNode current = root.path("current");
                if (!current.isMissingNode()) {
                    int wmoCode = current.path("weather_code").asInt(0);
                    WeatherCondition condition = WeatherCondition.fromWmoCode(wmoCode);

                    return WeatherData.builder()
                            .temperature(current.path("temperature_2m").asDouble())
                            .humidity(current.path("relative_humidity_2m").asDouble())
                            .precipitation(current.path("precipitation").asDouble())
                            .windSpeed(current.path("wind_speed_10m").asDouble())
                            .windDirection(current.path("wind_direction_10m").asDouble())
                            .surfacePressure(current.path("surface_pressure").asDouble())
                            .solarRadiation(current.path("direct_radiation").asDouble())
                            .uvIndex(current.path("uv_index").asDouble())
                            .condition(condition)
                            .provider(PROVIDER_NAME)
                            .timestamp(Instant.now())
                            .rawMetadata(responseBody)
                            .build();
                }
            }
        } catch (Exception e) {
            log.warn("Failed to fetch weather data from Open-Meteo API for ({}, {}): {}. Falling back to simulated provider.",
                    latitude, longitude, e.getMessage());
        }

        return fallbackProvider.getCurrentWeather(latitude, longitude);
    }

    @Override
    public List<WeatherForecast> getDailyForecast(double latitude, double longitude, int days) {
        try {
            int forecastDays = Math.max(1, Math.min(days, 16));
            String uri = String.format(
                    Locale.ROOT,
                    "/v1/forecast?latitude=%.4f&longitude=%.4f&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,wind_speed_10m_max,uv_index_max&forecast_days=%d&timezone=auto",
                    latitude,
                    longitude,
                    forecastDays
            );

            String responseBody = restClient.get()
                    .uri(uri)
                    .retrieve()
                    .body(String.class);

            if (responseBody != null) {
                JsonNode root = objectMapper.readTree(responseBody);
                JsonNode daily = root.path("daily");
                if (!daily.isMissingNode()) {
                    JsonNode timeArray = daily.path("time");
                    JsonNode tempMaxArray = daily.path("temperature_2m_max");
                    JsonNode tempMinArray = daily.path("temperature_2m_min");
                    JsonNode precipSumArray = daily.path("precipitation_sum");
                    JsonNode precipProbArray = daily.path("precipitation_probability_max");
                    JsonNode windSpeedArray = daily.path("wind_speed_10m_max");
                    JsonNode uvIndexArray = daily.path("uv_index_max");
                    JsonNode weatherCodeArray = daily.path("weather_code");

                    List<WeatherForecast> forecasts = new ArrayList<>();
                    int size = timeArray.size();
                    for (int i = 0; i < size; i++) {
                        LocalDate date = LocalDate.parse(timeArray.get(i).asText());
                        double minT = tempMinArray.has(i) ? tempMinArray.get(i).asDouble() : 0.0;
                        double maxT = tempMaxArray.has(i) ? tempMaxArray.get(i).asDouble() : 0.0;
                        double precipSum = precipSumArray.has(i) ? precipSumArray.get(i).asDouble() : 0.0;
                        double precipProb = precipProbArray.has(i) ? precipProbArray.get(i).asDouble() : 0.0;
                        double maxWind = windSpeedArray.has(i) ? windSpeedArray.get(i).asDouble() : 0.0;
                        double maxUv = uvIndexArray.has(i) ? uvIndexArray.get(i).asDouble() : 0.0;
                        int wmoCode = weatherCodeArray.has(i) ? weatherCodeArray.get(i).asInt() : 0;

                        forecasts.add(WeatherForecast.builder()
                                .date(date)
                                .minTemperature(minT)
                                .maxTemperature(maxT)
                                .averageTemperature(Math.round(((minT + maxT) / 2.0) * 10.0) / 10.0)
                                .precipitationSum(precipSum)
                                .precipitationProbability(precipProb)
                                .maxWindSpeed(maxWind)
                                .uvIndexMax(maxUv)
                                .condition(WeatherCondition.fromWmoCode(wmoCode))
                                .build());
                    }
                    if (!forecasts.isEmpty()) {
                        return forecasts;
                    }
                }
            }
        } catch (Exception e) {
            log.warn("Failed to fetch forecast from Open-Meteo for ({}, {}): {}. Falling back to simulated provider.",
                    latitude, longitude, e.getMessage());
        }

        return fallbackProvider.getDailyForecast(latitude, longitude, days);
    }

    @Override
    public List<WeatherAlert> getAlerts(double latitude, double longitude) {
        // Open-Meteo alerts or simulated rule-based alerts based on current weather
        return fallbackProvider.getAlerts(latitude, longitude);
    }

    @Override
    public WeatherData getHistoricalWeather(double latitude, double longitude, Instant timestamp) {
        return fallbackProvider.getHistoricalWeather(latitude, longitude, timestamp);
    }

    @Override
    public String getProviderName() {
        return PROVIDER_NAME;
    }
}
