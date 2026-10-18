package com.agrosense.audit.domain;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import java.time.Instant;
import java.util.Objects;
import java.util.UUID;

@Entity
@Table(name = "audit_events")
public class AuditEvent {

    @Id
    private UUID id;

    @Column(name = "action", nullable = false, length = 100)
    private String action;

    @Column(name = "user_id")
    private UUID userId;

    @Column(name = "entity_type", length = 50)
    private String entityType;

    @Column(name = "entity_id")
    private UUID entityId;

    @Column(name = "details", columnDefinition = "jsonb")
    private String details;

    @Column(name = "created_at", nullable = false)
    private Instant createdAt;

    public AuditEvent() {
    }

    public AuditEvent(UUID id, String action, UUID userId, String entityType, UUID entityId, String details) {
        this.id = id != null ? id : UUID.randomUUID();
        this.action = Objects.requireNonNull(action, "Action cannot be null");
        this.userId = userId;
        this.entityType = entityType;
        this.entityId = entityId;
        this.details = details;
        this.createdAt = Instant.now();
    }

    public static AuditEvent create(String action, UUID userId, String entityType, UUID entityId, String details) {
        return new AuditEvent(UUID.randomUUID(), action, userId, entityType, entityId, details);
    }

    public static AuditEvent ofAction(String action, UUID userId, String details) {
        return new AuditEvent(UUID.randomUUID(), action, userId, null, null, details);
    }

    public UUID getId() {
        return id;
    }

    public void setId(UUID id) {
        this.id = id;
    }

    public String getAction() {
        return action;
    }

    public void setAction(String action) {
        this.action = action;
    }

    public UUID getUserId() {
        return userId;
    }

    public void setUserId(UUID userId) {
        this.userId = userId;
    }

    public String getEntityType() {
        return entityType;
    }

    public void setEntityType(String entityType) {
        this.entityType = entityType;
    }

    public UUID getEntityId() {
        return entityId;
    }

    public void setEntityId(UUID entityId) {
        this.entityId = entityId;
    }

    public String getDetails() {
        return details;
    }

    public void setDetails(String details) {
        this.details = details;
    }

    public Instant getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(Instant createdAt) {
        this.createdAt = createdAt;
    }
}
