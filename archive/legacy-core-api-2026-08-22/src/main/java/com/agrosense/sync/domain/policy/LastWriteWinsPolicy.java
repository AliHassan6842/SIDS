package com.agrosense.sync.domain.policy;

import com.agrosense.sync.domain.model.ConflictResolutionResult;
import com.agrosense.sync.domain.model.ConflictResolutionStrategy;
import com.agrosense.sync.domain.model.SyncEvent;

import java.time.OffsetDateTime;

/**
 * Domain policy implementing strict Last-Write-Wins (LWW) resolution based on timestamps.
 */
public class LastWriteWinsPolicy implements ConflictResolutionPolicy {

    private final DefaultConflictResolutionPolicy delegate = new DefaultConflictResolutionPolicy();

    @Override
    public ConflictResolutionResult resolveConflict(
            SyncEvent event,
            Long currentServerVersion,
            OffsetDateTime serverLastModifiedAt,
            ConflictResolutionStrategy strategy) {
        return delegate.resolveConflict(event, currentServerVersion, serverLastModifiedAt, ConflictResolutionStrategy.LAST_WRITE_WINS);
    }
}
