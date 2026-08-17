package com.agrosense.weather.infrastructure.persistence;

import com.agrosense.weather.domain.WeatherSnapshot;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

import java.time.Instant;
import java.util.UUID;

@Entity
@Table(name = "weather_snapshots")
public class WeatherSnapshotEntity {

    @Id
    private UUID id;

    @Column(name = "field_id", nullable = false)
    private UUID fieldId;

    @Column(name = "temperature", precision = 5, scale = 2)
    private Double temperature;

    @Column(name = "humidity", precision = 5, scale = 2)
    private Double humidity;

    @Column(name = "precipitation", precision = 5, scale = 2)
    private Double precipitation;

    @Column(name = "wind", precision = 5, scale = 2)
    private Double wind;

    @Column(name = "provider", nullable = false, length = 50)
    private String provider;

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "raw_metadata", columnDefinition = "jsonb")
    private String rawMetadata;

    @Column(name = "timestamp", nullable = false)
    private Instant timestamp;

    public WeatherSnapshotEntity() {
    }

    public WeatherSnapshotEntity(
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
        this.fieldId = fieldId;
        this.temperature = temperature;
        this.humidity = humidity;
        this.precipitation = precipitation;
        this.wind = wind;
        this.provider = provider != null ? provider : "unknown";
        this.rawMetadata = rawMetadata;
        this.timestamp = timestamp != null ? timestamp : Instant.now();
    }

    public static WeatherSnapshotEntity fromDomain(WeatherSnapshot domain) {
        if (domain == null) {
            return null;
        }
        return new WeatherSnapshotEntity(
                domain.getId(),
                domain.getFieldId(),
                domain.getTemperature(),
                domain.getHumidity(),
                domain.getPrecipitation(),
                domain.getWind(),
                domain.getProvider(),
                domain.getRawMetadata(),
                domain.getTimestamp()
        );
    }

    public WeatherSnapshot toDomain() {
        return new WeatherSnapshot(
                this.id,
                this.fieldId,
                this.temperature,
                this.humidity,
                this.precipitation,
                this.wind,
                this.provider,
                this.rawMetadata,
                this.timestamp
        );
    }

    public UUID getId() {
        return id;
    }

    public void setId(UUID id) {
        this.id = id;
    }

    public UUID getFieldId() {
        return fieldId;
    }

    public void setFieldId(UUID fieldId) {
        this.fieldId = fieldId;
    }

    public Double getTemperature() {
        return temperature;
    }

    public void setTemperature(Double temperature) {
        this.temperature = temperature;
    }

    public Double getHumidity() {
        return humidity;
    }

    public void setHumidity(Double humidity) {
        this.humidity = humidity;
    }

    public Double getPrecipitation() {
        return precipitation;
    }

    public void setPrecipitation(Double precipitation) {
        this.precipitation = precipitation;
    }

    public Double getWind() {
        return wind;
    }

    public void setWind(Double wind) {
        this.wind = wind;
    }

    public String getProvider() {
        return provider;
    }

    public void setProvider(String provider) {
        this.provider = provider;
    }

    public String getRawMetadata() {
        return rawMetadata;
    }

    public void setRawMetadata(String rawMetadata) {
        this.rawMetadata = rawMetadata;
    }

    public Instant getTimestamp() {
        return timestamp;
    }

    public void setTimestamp(Instant timestamp) {
        this.timestamp = timestamp;
    }
}
