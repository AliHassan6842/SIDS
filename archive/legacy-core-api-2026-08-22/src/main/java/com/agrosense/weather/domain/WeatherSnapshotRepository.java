package com.agrosense.weather.domain;

import java.time.Instant;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

/**
 * Port interface for persistence of weather snapshots.
 */
public interface WeatherSnapshotRepository {

    /**
     * Persists a weather snapshot.
     */
    WeatherSnapshot save(WeatherSnapshot snapshot);

    /**
     * Finds a weather snapshot by its unique ID.
     */
    Optional<WeatherSnapshot> findById(UUID id);

    /**
     * Finds all weather snapshots recorded for a specific field, ordered by timestamp descending.
     */
    List<WeatherSnapshot> findByFieldId(UUID fieldId);

    /**
     * Finds the most recent weather snapshot for a specific field.
     */
    Optional<WeatherSnapshot> findLatestByFieldId(UUID fieldId);

    /**
     * Finds weather snapshots for a specific field within a timestamp range.
     */
    List<WeatherSnapshot> findByFieldIdAndTimestampBetween(UUID fieldId, Instant start, Instant end);

    /**
     * Deletes a weather snapshot by ID.
     */
    void deleteById(UUID id);
}
