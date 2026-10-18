package com.agrosense.weather.application.dto;

import java.time.Instant;
import java.util.UUID;

public record RecordSnapshotCommand(
        UUID fieldId,
        Double latitude,
        Double longitude,
        Double temperature,
        Double humidity,
        Double precipitation,
        Double wind,
        String provider,
        String rawMetadata,
        Instant timestamp
) {
    public static RecordSnapshotCommand forCoordinates(UUID fieldId, double latitude, double longitude) {
        return new RecordSnapshotCommand(fieldId, latitude, longitude, null, null, null, null, null, null, null);
    }
}
