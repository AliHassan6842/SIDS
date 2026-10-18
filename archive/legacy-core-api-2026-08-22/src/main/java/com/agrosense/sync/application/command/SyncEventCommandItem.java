package com.agrosense.sync.application.command;

import com.agrosense.sync.domain.model.ConflictResolutionStrategy;
import com.agrosense.sync.domain.model.SyncOperation;

import java.time.OffsetDateTime;
import java.util.UUID;

/**
 * Command representation of an individual synchronization event in an incoming batch.
 */
public record SyncEventCommandItem(
        String clientEventId,
        UUID entityId,
        String entityType,
        SyncOperation operation,
        Long baseVersion,
        String payload,
        OffsetDateTime createdAtDevice,
        ConflictResolutionStrategy preferredStrategy
) {
    public SyncEventCommandItem {
        if (operation == null) {
            operation = SyncOperation.UPDATE;
        }
        if (createdAtDevice == null) {
            createdAtDevice = OffsetDateTime.now();
        }
    }
}
