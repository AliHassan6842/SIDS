package com.agrosense.audit.application;

import java.util.UUID;

public record AuditQuery(
        UUID userId,
        String entityType,
        UUID entityId,
        String action,
        Integer limit
) {
    public AuditQuery {
        if (limit == null || limit <= 0) {
            limit = 50;
        }
    }
}
