package com.agrosense.sync.domain.model;

import java.time.OffsetDateTime;
import java.util.Objects;
import java.util.UUID;

/**
 * Domain entity representing a synchronized mutation event originating from an edge or mobile device.
 */
public class SyncEvent {

    private final UUID id;
    private final String clientEventId;
    private final String deviceId;
    private final UUID entityId;
    private final String entityType;
    private final SyncOperation operation;
    private final Long baseVersion;
    private final String payload;
    private final OffsetDateTime createdAtDevice;
    private final OffsetDateTime serverReceivedAt;
    private SyncStatus status;
    private String failureReason;

    public SyncEvent(
            UUID id,
            String clientEventId,
            String deviceId,
            UUID entityId,
            String entityType,
            SyncOperation operation,
            Long baseVersion,
            String payload,
            OffsetDateTime createdAtDevice,
            OffsetDateTime serverReceivedAt,
            SyncStatus status,
            String failureReason) {
        this.id = id != null ? id : UUID.randomUUID();
        this.clientEventId = Objects.requireNonNull(clientEventId, "clientEventId cannot be null");
        this.deviceId = Objects.requireNonNull(deviceId, "deviceId cannot be null");
        this.entityId = Objects.requireNonNull(entityId, "entityId cannot be null");
        this.entityType = Objects.requireNonNull(entityType, "entityType cannot be null");
        this.operation = operation != null ? operation : SyncOperation.UPDATE;
        this.baseVersion = baseVersion;
        this.payload = payload;
        this.createdAtDevice = createdAtDevice != null ? createdAtDevice : OffsetDateTime.now();
        this.serverReceivedAt = serverReceivedAt != null ? serverReceivedAt : OffsetDateTime.now();
        this.status = status != null ? status : SyncStatus.APPLIED;
        this.failureReason = failureReason;
    }

    public static SyncEvent createNew(
            String clientEventId,
            String deviceId,
            UUID entityId,
            String entityType,
            SyncOperation operation,
            Long baseVersion,
            String payload,
            OffsetDateTime createdAtDevice) {
        return new SyncEvent(
                UUID.randomUUID(),
                clientEventId,
                deviceId,
                entityId,
                entityType,
                operation,
                baseVersion,
                payload,
                createdAtDevice != null ? createdAtDevice : OffsetDateTime.now(),
                OffsetDateTime.now(),
                SyncStatus.APPLIED,
                null
        );
    }

    public void markApplied() {
        this.status = SyncStatus.APPLIED;
        this.failureReason = null;
    }

    public void markDuplicate() {
        this.status = SyncStatus.DUPLICATE_IGNORED;
        this.failureReason = null;
    }

    public void markConflict(SyncStatus resolutionStatus) {
        this.status = resolutionStatus;
    }

    public void markFailed(String reason) {
        this.status = SyncStatus.FAILED;
        this.failureReason = reason;
    }

    public UUID getId() {
        return id;
    }

    public String getClientEventId() {
        return clientEventId;
    }

    public String getDeviceId() {
        return deviceId;
    }

    public UUID getEntityId() {
        return entityId;
    }

    public String getEntityType() {
        return entityType;
    }

    public SyncOperation getOperation() {
        return operation;
    }

    public Long getBaseVersion() {
        return baseVersion;
    }

    public String getPayload() {
        return payload;
    }

    public OffsetDateTime getCreatedAtDevice() {
        return createdAtDevice;
    }

    public OffsetDateTime getServerReceivedAt() {
        return serverReceivedAt;
    }

    public SyncStatus getStatus() {
        return status;
    }

    public String getFailureReason() {
        return failureReason;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        SyncEvent syncEvent = (SyncEvent) o;
        return Objects.equals(id, syncEvent.id) || Objects.equals(clientEventId, syncEvent.clientEventId);
    }

    @Override
    public int hashCode() {
        return Objects.hash(id, clientEventId);
    }

    @Override
    public String toString() {
        return "SyncEvent{" +
                "id=" + id +
                ", clientEventId='" + clientEventId + '\'' +
                ", deviceId='" + deviceId + '\'' +
                ", entityId=" + entityId +
                ", entityType='" + entityType + '\'' +
                ", operation=" + operation +
                ", baseVersion=" + baseVersion +
                ", status=" + status +
                '}';
    }
}
