package com.agrosense.weather.application.dto;

import com.agrosense.weather.domain.WeatherSnapshot;
import java.time.Instant;
import java.util.UUID;

public record WeatherSnapshotDto(
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
    public static WeatherSnapshotDto fromDomain(WeatherSnapshot snapshot) {
        if (snapshot == null) {
            return null;
        }
        return new WeatherSnapshotDto(
                snapshot.getId(),
                snapshot.getFieldId(),
                snapshot.getTemperature(),
                snapshot.getHumidity(),
                snapshot.getPrecipitation(),
                snapshot.getWind(),
                snapshot.getProvider(),
                snapshot.getRawMetadata(),
                snapshot.getTimestamp()
        );
    }
}
