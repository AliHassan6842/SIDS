package com.agrosense.weather.application;

import com.agrosense.shared.error.exceptions.ResourceNotFoundException;
import com.agrosense.weather.application.dto.*;
import com.agrosense.weather.domain.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Instant;
import java.util.List;
import java.util.Objects;
import java.util.UUID;

@Service
public class WeatherService {

    private static final Logger log = LoggerFactory.getLogger(WeatherService.class);
    private static final long DEFAULT_CACHE_TTL_SECONDS = 1800; // 30 minutes

    private final WeatherProvider weatherProvider;
    private final WeatherSnapshotRepository snapshotRepository;
    private final WeatherCache weatherCache;

    public WeatherService(
            WeatherProvider weatherProvider,
            WeatherSnapshotRepository snapshotRepository,
            WeatherCache weatherCache
    ) {
        this.weatherProvider = weatherProvider;
        this.snapshotRepository = snapshotRepository;
        this.weatherCache = weatherCache;
    }

    /**
     * Gets current weather for coordinates with caching.
     */
    public CurrentWeatherDto getCurrentWeather(double latitude, double longitude) {
        WeatherData weatherData = getOrFetchWeatherData(latitude, longitude);
        return CurrentWeatherDto.fromDomain(weatherData);
    }

    /**
     * Gets current weather for a specific field, optionally creating a persistent snapshot.
     */
    @Transactional
    public CurrentWeatherDto getCurrentWeatherForField(UUID fieldId, double latitude, double longitude, boolean autoSnapshot) {
        WeatherData weatherData = getOrFetchWeatherData(latitude, longitude);
        if (autoSnapshot && fieldId != null) {
            WeatherSnapshot snapshot = WeatherSnapshot.fromWeatherData(fieldId, weatherData);
            snapshotRepository.save(snapshot);
            log.debug("Auto-saved weather snapshot for field {}", fieldId);
        }
        return CurrentWeatherDto.fromDomain(weatherData);
    }

    /**
     * Gets daily forecast for a given location.
     */
    public List<WeatherForecastDto> getForecast(double latitude, double longitude, int days) {
        int boundedDays = Math.max(1, Math.min(days, 16));
        List<WeatherForecast> forecasts = weatherProvider.getDailyForecast(latitude, longitude, boundedDays);
        return forecasts.stream()
                .map(WeatherForecastDto::fromDomain)
                .toList();
    }

    /**
     * Gets active weather alerts for a given location.
     */
    public List<WeatherAlertDto> getAlerts(double latitude, double longitude) {
        List<WeatherAlert> alerts = weatherProvider.getAlerts(latitude, longitude);
        return alerts.stream()
                .map(WeatherAlertDto::fromDomain)
                .toList();
    }

    /**
     * Records a weather snapshot for a field by fetching current provider readings.
     */
    @Transactional
    public WeatherSnapshotDto recordSnapshot(UUID fieldId, double latitude, double longitude) {
        Objects.requireNonNull(fieldId, "fieldId must not be null");
        WeatherData weatherData = weatherProvider.getCurrentWeather(latitude, longitude);
        WeatherSnapshot snapshot = WeatherSnapshot.fromWeatherData(fieldId, weatherData);
        WeatherSnapshot saved = snapshotRepository.save(snapshot);
        log.info("Recorded weather snapshot {} for field {}", saved.getId(), fieldId);
        return WeatherSnapshotDto.fromDomain(saved);
    }

    /**
     * Records a weather snapshot from a command (supports explicit IoT measurements or coordinate lookup).
     */
    @Transactional
    public WeatherSnapshotDto recordSnapshot(RecordSnapshotCommand command) {
        Objects.requireNonNull(command, "command must not be null");
        Objects.requireNonNull(command.fieldId(), "fieldId must not be null");

        WeatherSnapshot snapshot;
        if (command.temperature() != null || command.humidity() != null) {
            // Direct measurement provided
            snapshot = new WeatherSnapshot(
                    UUID.randomUUID(),
                    command.fieldId(),
                    command.temperature(),
                    command.humidity(),
                    command.precipitation(),
                    command.wind(),
                    command.provider() != null ? command.provider() : "manual-or-sensor",
                    command.rawMetadata(),
                    command.timestamp() != null ? command.timestamp() : Instant.now()
            );
        } else if (command.latitude() != null && command.longitude() != null) {
            // Fetch from provider
            WeatherData weatherData = weatherProvider.getCurrentWeather(command.latitude(), command.longitude());
            snapshot = WeatherSnapshot.fromWeatherData(command.fieldId(), weatherData);
        } else {
            throw new IllegalArgumentException("Either weather measurements or latitude/longitude coordinates must be provided");
        }

        WeatherSnapshot saved = snapshotRepository.save(snapshot);
        log.info("Recorded weather snapshot {} for field {}", saved.getId(), command.fieldId());
        return WeatherSnapshotDto.fromDomain(saved);
    }

    /**
     * Retrieves the latest weather snapshot for a specific field.
     */
    @Transactional(readOnly = true)
    public WeatherSnapshotDto getLatestSnapshot(UUID fieldId) {
        Objects.requireNonNull(fieldId, "fieldId must not be null");
        WeatherSnapshot snapshot = snapshotRepository.findLatestByFieldId(fieldId)
                .orElseThrow(() -> new ResourceNotFoundException(
                        "No weather snapshot found for field: " + fieldId,
                        "WeatherSnapshot",
                        fieldId.toString()
                ));
        return WeatherSnapshotDto.fromDomain(snapshot);
    }

    /**
     * Retrieves historical weather snapshots for a field with optional date range.
     */
    @Transactional(readOnly = true)
    public List<WeatherSnapshotDto> getSnapshotHistory(UUID fieldId, Instant from, Instant to) {
        Objects.requireNonNull(fieldId, "fieldId must not be null");
        List<WeatherSnapshot> snapshots;
        if (from != null && to != null) {
            snapshots = snapshotRepository.findByFieldIdAndTimestampBetween(fieldId, from, to);
        } else {
            snapshots = snapshotRepository.findByFieldId(fieldId);
        }
        return snapshots.stream()
                .map(WeatherSnapshotDto::fromDomain)
                .toList();
    }

    /**
     * Retrieves a single snapshot by ID.
     */
    @Transactional(readOnly = true)
    public WeatherSnapshotDto getSnapshotById(UUID snapshotId) {
        Objects.requireNonNull(snapshotId, "snapshotId must not be null");
        WeatherSnapshot snapshot = snapshotRepository.findById(snapshotId)
                .orElseThrow(() -> new ResourceNotFoundException(
                        "Weather snapshot not found with ID: " + snapshotId,
                        "WeatherSnapshot",
                        snapshotId.toString()
                ));
        return WeatherSnapshotDto.fromDomain(snapshot);
    }

    private WeatherData getOrFetchWeatherData(double latitude, double longitude) {
        return weatherCache.get(latitude, longitude)
                .orElseGet(() -> {
                    log.debug("Weather cache miss for coordinates ({}, {}). Fetching from provider...", latitude, longitude);
                    WeatherData fetched = weatherProvider.getCurrentWeather(latitude, longitude);
                    weatherCache.put(latitude, longitude, fetched, DEFAULT_CACHE_TTL_SECONDS);
                    return fetched;
                });
    }
}
