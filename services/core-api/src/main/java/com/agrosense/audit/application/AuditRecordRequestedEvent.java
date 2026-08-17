package com.agrosense.audit.application;

import java.util.UUID;

public record AuditRecordRequestedEvent(
        String action,
        UUID userId,
        String entityType,
        UUID entityId,
        String details
) {
    public static AuditRecordRequestedEvent of(String action, UUID userId, String entityType, UUID entityId, String details) {
        return new AuditRecordRequestedEvent(action, userId, entityType, entityId, details);
    }

    public static AuditRecordRequestedEvent ofAction(String action, UUID userId, String details) {
        return new AuditRecordRequestedEvent(action, userId, null, null, details);
    }

    public RecordAuditCommand toCommand() {
        return new RecordAuditCommand(action, userId, entityType, entityId, details);
    }
}
