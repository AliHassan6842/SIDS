package com.agrosense.field.domain;

import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import java.time.Instant;
import java.util.UUID;

@Entity
@Table(name = "field_boundaries")
public class FieldBoundary {
    @Id
    private UUID id;
    private UUID fieldId;
    private String boundaryPolygon; // We can store JSONB as a String or map to a custom type
    private Instant createdAt;

    public FieldBoundary() {}

    public FieldBoundary(UUID id, UUID fieldId, String boundaryPolygon) {
        this.id = id;
        this.fieldId = fieldId;
        this.boundaryPolygon = boundaryPolygon;
        this.createdAt = Instant.now();
    }
}
