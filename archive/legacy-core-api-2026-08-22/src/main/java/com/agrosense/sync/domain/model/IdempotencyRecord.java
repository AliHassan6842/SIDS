package com.agrosense.sync.domain.model;

import java.time.OffsetDateTime;
import java.util.Objects;
import java.util.UUID;

/**
 * Domain model representing an idempotency record ensuring exactly-once processing of client sync events.
 */
public class IdempotencyRecord {

    private final UUID id;
    private final String clientEventId;
    private final String resourceType;
    private final UUID resourceId;
    private final OffsetDateTime createdAt;
    private final String responseSummary;

    public IdempotencyRecord(
            UUID id,
            String clientEventId,
            String resourceType,
            UUID resourceId,
            OffsetDateTime createdAt,
            String responseSummary) {
        this.id = id != null ? id : UUID.randomUUID();
        this.clientEventId = Objects.requireNonNull(clientEventId, "clientEventId cannot be null");
        this.resourceType = Objects.requireNonNull(resourceType, "resourceType cannot be null");
        this.resourceId = Objects.requireNonNull(resourceId, "resourceId cannot be null");
        this.createdAt = createdAt != null ? createdAt : OffsetDateTime.now();
        this.responseSummary = responseSummary;
    }

    public static IdempotencyRecord create(String clientEventId, String resourceType, UUID resourceId, String responseSummary) {
        return new IdempotencyRecord(
                UUID.randomUUID(),
                clientEventId,
                resourceType,
                resourceId,
                OffsetDateTime.now(),
                responseSummary
        );
    }

    public UUID getId() {
        return id;
    }

    public String getClientEventId() {
        return clientEventId;
    }

    public String getResourceType() {
        return resourceType;
    }

    public UUID getResourceId() {
        return resourceId;
    }

    public OffsetDateTime getCreatedAt() {
        return createdAt;
    }

    public String getResponseSummary() {
        return responseSummary;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        IdempotencyRecord that = (IdempotencyRecord) o;
        return Objects.equals(clientEventId, that.clientEventId);
    }

    @Override
    public int hashCode() {
        return Objects.hash(clientEventId);
    }

    @Override
    public String toString() {
        return "IdempotencyRecord{" +
                "id=" + id +
                ", clientEventId='" + clientEventId + '\'' +
                ", resourceType='" + resourceType + '\'' +
                ", resourceId=" + resourceId +
                ", createdAt=" + createdAt +
                '}';
    }
}
