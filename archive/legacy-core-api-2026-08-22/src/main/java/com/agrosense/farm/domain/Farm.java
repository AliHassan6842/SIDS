package com.agrosense.farm.domain;

import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import jakarta.persistence.Version;
import java.time.Instant;
import java.util.UUID;

@Entity
@Table(name = "farms")
public class Farm {
    @Id
    private UUID id;
    private String name;
    private Double locationLat;
    private Double locationLng;
    private Double area;
    private String areaUnit;
    private Instant createdAt;
    private Instant updatedAt;
    
    @Version
    private Long version;

    public Farm() {}

    public Farm(UUID id, String name, Double locationLat, Double locationLng, Double area, String areaUnit) {
        this.id = id;
        this.name = name;
        this.locationLat = locationLat;
        this.locationLng = locationLng;
        this.area = area;
        this.areaUnit = areaUnit;
        this.createdAt = Instant.now();
        this.updatedAt = this.createdAt;
    }
}
