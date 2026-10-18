package com.agrosense.sync.domain.exception;

import com.agrosense.shared.error.exceptions.BaseException;

import java.util.Map;
import java.util.UUID;

/**
 * Thrown when an unresolvable synchronization conflict or optimistic locking clash is detected.
 */
public class SyncConflictException extends BaseException {

    public SyncConflictException(
            String message,
            String clientEventId,
            UUID entityId,
            String entityType,
            Long baseVersion,
            Long serverVersion) {
        super(
                message,
                "SYNC_CONFLICT_DETECTED",
                false,
                Map.of(
                        "clientEventId", clientEventId != null ? clientEventId : "unknown",
                        "entityId", entityId != null ? entityId.toString() : "unknown",
                        "entityType", entityType != null ? entityType : "unknown",
                        "baseVersion", baseVersion != null ? baseVersion : -1,
                        "serverVersion", serverVersion != null ? serverVersion : -1
                )
        );
    }
}
