package com.agrosense.sync.infrastructure.persistence.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

import java.time.OffsetDateTime;
import java.util.UUID;

/**
 * JPA Entity mapping to the `sync_events` table in PostgreSQL.
 */
@Entity
@Table(name = "sync_events")
public class SyncEventJpaEntity {

    @Id
    private UUID id;

    @Column(name = "client_event_id", nullable = false)
    private String clientEventId;

    @Column(name = "device_id", nullable = false)
    private String deviceId;

    @Column(name = "entity_id", nullable = false)
    private UUID entityId;

    @Column(name = "entity_type", nullable = false, length = 50)
    private String entityType;

    @Column(name = "base_version")
    private Long baseVersion;

    @Column(name = "created_at_device", nullable = false)
    private OffsetDateTime createdAtDevice;

    @Column(name = "server_received_at", nullable = false)
    private OffsetDateTime serverReceivedAt;

    public SyncEventJpaEntity() {
    }

    public SyncEventJpaEntity(
            UUID id,
            String clientEventId,
            String deviceId,
            UUID entityId,
            String entityType,
            Long baseVersion,
            OffsetDateTime createdAtDevice,
            OffsetDateTime serverReceivedAt) {
        this.id = id != null ? id : UUID.randomUUID();
        this.clientEventId = clientEventId;
        this.deviceId = deviceId;
        this.entityId = entityId;
        this.entityType = entityType;
        this.baseVersion = baseVersion;
        this.createdAtDevice = createdAtDevice != null ? createdAtDevice : OffsetDateTime.now();
        this.serverReceivedAt = serverReceivedAt != null ? serverReceivedAt : OffsetDateTime.now();
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

    public String getDeviceId() {
        return deviceId;
    }

    public void setDeviceId(String deviceId) {
        this.deviceId = deviceId;
    }

    public UUID getEntityId() {
        return entityId;
    }

    public void setEntityId(UUID entityId) {
        this.entityId = entityId;
    }

    public String getEntityType() {
        return entityType;
    }

    public void setEntityType(String entityType) {
        this.entityType = entityType;
    }

    public Long getBaseVersion() {
        return baseVersion;
    }

    public void setBaseVersion(Long baseVersion) {
        this.baseVersion = baseVersion;
    }

    public OffsetDateTime getCreatedAtDevice() {
        return createdAtDevice;
    }

    public void setCreatedAtDevice(OffsetDateTime createdAtDevice) {
        this.createdAtDevice = createdAtDevice;
    }

    public OffsetDateTime getServerReceivedAt() {
        return serverReceivedAt;
    }

    public void setServerReceivedAt(OffsetDateTime serverReceivedAt) {
        this.serverReceivedAt = serverReceivedAt;
    }
}
