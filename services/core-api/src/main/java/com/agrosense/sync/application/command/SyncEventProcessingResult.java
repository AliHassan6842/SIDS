package com.agrosense.sync.application.command;

import com.agrosense.sync.domain.model.SyncStatus;

import java.util.UUID;

/**
 * Result of processing an individual synchronization event.
 */
public record SyncEventProcessingResult(
        String clientEventId,
        UUID entityId,
        String entityType,
        SyncStatus status,
        Long baseVersion,
        Long serverVersion,
        Long resolvedVersion,
        boolean conflictDetected,
        String message,
        Object payload
) {
    public static SyncEventProcessingResult applied(
            String clientEventId,
            UUID entityId,
            String entityType,
            Long baseVersion,
            Long newVersion,
            Object payload) {
        return new SyncEventProcessingResult(
                clientEventId,
                entityId,
                entityType,
                SyncStatus.APPLIED,
                baseVersion,
                newVersion,
                newVersion,
                false,
                "Event successfully applied.",
                payload
        );
    }

    public static SyncEventProcessingResult duplicate(
            String clientEventId,
            UUID entityId,
            String entityType,
            Long currentVersion) {
        return new SyncEventProcessingResult(
                clientEventId,
                entityId,
                entityType,
                SyncStatus.DUPLICATE_IGNORED,
                currentVersion,
                currentVersion,
                currentVersion,
                false,
                "Event already processed; duplicate ignored idempotently.",
                null
        );
    }

    public static SyncEventProcessingResult conflictResolved(
            String clientEventId,
            UUID entityId,
            String entityType,
            SyncStatus status,
            Long baseVersion,
            Long serverVersion,
            Long resolvedVersion,
            String message,
            Object payload) {
        return new SyncEventProcessingResult(
                clientEventId,
                entityId,
                entityType,
                status,
                baseVersion,
                serverVersion,
                resolvedVersion,
                true,
                message,
                payload
        );
    }

    public static SyncEventProcessingResult failed(
            String clientEventId,
            UUID entityId,
            String entityType,
            SyncStatus status,
            Long baseVersion,
            Long serverVersion,
            String message) {
        return new SyncEventProcessingResult(
                clientEventId,
                entityId,
                entityType,
                status != null ? status : SyncStatus.FAILED,
                baseVersion,
                serverVersion,
                serverVersion,
                status == SyncStatus.CONFLICT_DETECTED || status == SyncStatus.REJECTED_STALE_VERSION,
                message,
                null
        );
    }
}
