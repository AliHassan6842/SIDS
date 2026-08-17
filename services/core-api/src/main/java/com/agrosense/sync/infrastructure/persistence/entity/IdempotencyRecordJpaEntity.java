package com.agrosense.sync.infrastructure.persistence.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

import java.time.OffsetDateTime;
import java.util.UUID;

/**
 * JPA Entity mapping to the `idempotency_records` table in PostgreSQL.
 */
@Entity
@Table(name = "idempotency_records")
public class IdempotencyRecordJpaEntity {

    @Id
    private UUID id;

    @Column(name = "client_event_id", unique = true, nullable = false)
    private String clientEventId;

    @Column(name = "resource_type", nullable = false, length = 50)
    private String resourceType;

    @Column(name = "resource_id", nullable = false)
    private UUID resourceId;

    @Column(name = "created_at", nullable = false)
    private OffsetDateTime createdAt;

    public IdempotencyRecordJpaEntity() {
    }

    public IdempotencyRecordJpaEntity(
            UUID id,
            String clientEventId,
            String resourceType,
            UUID resourceId,
            OffsetDateTime createdAt) {
        this.id = id != null ? id : UUID.randomUUID();
        this.clientEventId = clientEventId;
        this.resourceType = resourceType;
        this.resourceId = resourceId;
        this.createdAt = createdAt != null ? createdAt : OffsetDateTime.now();
    }

    public UUID getId() {
        return id;
    }

    public void setId(UUID id) {
        this.id = id;
    }

    public String getClientEventId() {
        return clientEventId;
    }

    public void setClientEventId(String clientEventId) {
        this.clientEventId = clientEventId;
    }

    public String getResourceType() {
        return resourceType;
    }

    public void setResourceType(String resourceType) {
        this.resourceType = resourceType;
    }

    public UUID getResourceId() {
        return resourceId;
    }

    public void setResourceId(UUID resourceId) {
        this.resourceId = resourceId;
    }

    public OffsetDateTime getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(OffsetDateTime createdAt) {
        this.createdAt = createdAt;
    }
}
