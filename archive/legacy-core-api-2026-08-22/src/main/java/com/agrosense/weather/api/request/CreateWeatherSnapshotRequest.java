package com.agrosense.weather.api.request;

import com.agrosense.weather.application.dto.RecordSnapshotCommand;
import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.NotNull;

import java.time.Instant;
import java.util.UUID;

@Schema(description = "Request payload for recording a weather snapshot for a field")
public record CreateWeatherSnapshotRequest(
        @NotNull(message = "fieldId is required")
        @Schema(description = "ID of the field for which the snapshot is recorded", example = "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11")
        UUID fieldId,

        @Schema(description = "Latitude of the field (used if fetching from provider)", example = "-17.8252")
        Double latitude,

        @Schema(description = "Longitude of the field (used if fetching from provider)", example = "31.0335")
        Double longitude,

        @Schema(description = "Optional direct temperature reading in Celsius", example = "24.5")
        Double temperature,

        @Schema(description = "Optional direct relative humidity percentage", example = "65.0")
        Double humidity,

        @Schema(description = "Optional direct precipitation measurement in mm", example = "0.0")
        Double precipitation,

        @Schema(description = "Optional direct wind speed in m/s", example = "3.8")
        Double wind,

        @Schema(description = "Name of the source or provider", example = "on-farm-station")
        String provider,

        @Schema(description = "Optional raw JSON metadata or sensor payload", example = "{\"stationId\":\"ST-01\"}")
        String rawMetadata,

        @Schema(description = "Timestamp of the snapshot (defaults to current time if null)")
        Instant timestamp
) {
    public RecordSnapshotCommand toCommand() {
        return new RecordSnapshotCommand(
                fieldId,
                latitude,
                longitude,
                temperature,
                humidity,
                precipitation,
                wind,
                provider,
                rawMetadata,
                timestamp != null ? timestamp : Instant.now()
        );
    }
}
