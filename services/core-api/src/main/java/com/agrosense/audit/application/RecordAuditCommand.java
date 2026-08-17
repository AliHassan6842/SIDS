package com.agrosense.audit.application;

import java.util.UUID;

public record RecordAuditCommand(
        String action,
        UUID userId,
        String entityType,
        UUID entityId,
        String details
) {
    public static RecordAuditCommand of(String action, UUID userId, String entityType, UUID entityId, String details) {
        return new RecordAuditCommand(action, userId, entityType, entityId, details);
    }

    public static RecordAuditCommand ofAction(String action, UUID userId, String details) {
        return new RecordAuditCommand(action, userId, null, null, details);
    }
}
