package com.agrosense.sync.application.command;

import java.time.OffsetDateTime;
import java.util.Collections;
import java.util.List;
import java.util.UUID;

/**
 * Query for pulling synchronization updates made on the server since a specific timestamp.
 */
public record PullSyncChangesQuery(
        UUID farmId,
        OffsetDateTime sinceTimestamp,
        List<String> entityTypes,
        Integer limit
) {
    public PullSyncChangesQuery {
        if (entityTypes == null) {
            entityTypes = Collections.emptyList();
        }
        if (limit == null || limit <= 0) {
            limit = 100;
        }
    }
}
