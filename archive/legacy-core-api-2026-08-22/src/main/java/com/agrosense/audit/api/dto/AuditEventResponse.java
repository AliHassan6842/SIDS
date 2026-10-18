package com.agrosense.audit.api.dto;

import com.agrosense.audit.domain.AuditEvent;

import java.time.Instant;
import java.util.UUID;

public record AuditEventResponse(
        UUID id,
        String action,
        UUID userId,
        String entityType,
        UUID entityId,
        String details,
        Instant createdAt
) {
    public static AuditEventResponse fromEntity(AuditEvent event) {
        return new AuditEventResponse(
                event.getId(),
                event.getAction(),
                event.getUserId(),
                event.getEntityType(),
                event.getEntityId(),
                event.getDetails(),
                event.getCreatedAt()
        );
    }
}
