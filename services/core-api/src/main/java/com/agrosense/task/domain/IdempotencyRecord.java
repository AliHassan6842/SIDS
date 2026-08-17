package com.agrosense.task.domain;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

import java.time.Instant;
import java.util.Objects;
import java.util.UUID;

/**
 * Tracks client operation keys to guarantee idempotent execution for distributed & offline clients.
 */
@Entity
@Table(name = "idempotency_records")
public class IdempotencyRecord {

    @Id
    private UUID id;

    @Column(name = "client_event_id", nullable = false, unique = true, length = 255)
    private String clientEventId;

    @Column(name = "resource_type", nullable = false, length = 50)
    private String resourceType;

    @Column(name = "resource_id", nullable = false)
    private UUID resourceId;

    @Column(name = "created_at", nullable = false)
    private Instant createdAt;

    public IdempotencyRecord() {
    }

    public IdempotencyRecord(UUID id, String clientEventId, String resourceType, UUID resourceId) {
        this.id = id != null ? id : UUID.randomUUID();
        this.clientEventId = Objects.requireNonNull(clientEventId, "clientEventId cannot be null");
        this.resourceType = Objects.requireNonNull(resourceType, "resourceType cannot be null");
        this.resourceId = Objects.requireNonNull(resourceId, "resourceId cannot be null");
        this.createdAt = Instant.now();
    }

    public static IdempotencyRecord ofTask(String clientEventId, UUID taskId) {
        return new IdempotencyRecord(UUID.randomUUID(), clientEventId, "TASK", taskId);
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

    public Instant getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(Instant createdAt) {
        this.createdAt = createdAt;
    }
}
