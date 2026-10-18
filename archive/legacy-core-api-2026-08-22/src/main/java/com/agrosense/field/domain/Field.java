package com.agrosense.field.domain;

import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import jakarta.persistence.Version;
import java.time.Instant;
import java.util.UUID;

@Entity
@Table(name = "fields")
public class Field {
    @Id
    private UUID id;
    private UUID farmId;
    private String name;
    private Double locationLat;
    private Double locationLng;
    private Double area;
    private String areaUnit;
    private UUID activeCropCycleId;
    private Instant createdAt;
    private Instant updatedAt;

    @Version
    private Long version;

    public Field() {}

    public Field(UUID id, UUID farmId, String name, Double locationLat, Double locationLng, Double area, String areaUnit) {
        this.id = id;
        this.farmId = farmId;
        this.name = name;
        this.locationLat = locationLat;
        this.locationLng = locationLng;
        this.area = area;
        this.areaUnit = areaUnit;
        this.createdAt = Instant.now();
        this.updatedAt = this.createdAt;
    }
}
