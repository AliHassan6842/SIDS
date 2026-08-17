package com.agrosense.cropcycle.domain;

import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import jakarta.persistence.Version;
import java.time.Instant;
import java.time.LocalDate;
import java.util.UUID;

@Entity
@Table(name = "crop_cycles")
public class CropCycle {
    @Id
    private UUID id;
    private UUID fieldId;
    private String cropId;
    private String variety;
    private LocalDate sowingDate;
    private LocalDate expectedHarvestDate;
    private LocalDate actualHarvestDate;
    private String status;
    private Instant createdAt;
    private Instant updatedAt;

    @Version
    private Long version;

    public CropCycle() {}

    public CropCycle(UUID id, UUID fieldId, String cropId, String variety, LocalDate sowingDate, LocalDate expectedHarvestDate, String status) {
        this.id = id;
        this.fieldId = fieldId;
        this.cropId = cropId;
        this.variety = variety;
        this.sowingDate = sowingDate;
        this.expectedHarvestDate = expectedHarvestDate;
        this.status = status;
        this.createdAt = Instant.now();
        this.updatedAt = this.createdAt;
    }
}
