package com.agrosense.sync.domain.policy;

import com.agrosense.sync.domain.model.ConflictResolutionResult;
import com.agrosense.sync.domain.model.ConflictResolutionStrategy;
import com.agrosense.sync.domain.model.SyncEvent;

import java.time.OffsetDateTime;

/**
 * Domain policy interface for evaluating and resolving offline synchronization conflicts.
 */
public interface ConflictResolutionPolicy {

    /**
     * Resolves a detected conflict between an incoming client sync event and current server entity state.
     *
     * @param event The incoming client sync event
     * @param currentServerVersion Current version of the entity on the server
     * @param serverLastModifiedAt Timestamp when the server entity was last modified
     * @param strategy The specific resolution strategy to apply
     * @return Result of the conflict resolution
     */
    ConflictResolutionResult resolveConflict(
            SyncEvent event,
            Long currentServerVersion,
            OffsetDateTime serverLastModifiedAt,
            ConflictResolutionStrategy strategy
    );
}
