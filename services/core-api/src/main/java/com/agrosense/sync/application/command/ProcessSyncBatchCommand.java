package com.agrosense.sync.application.command;

import com.agrosense.sync.domain.model.ConflictResolutionStrategy;

import java.util.Collections;
import java.util.List;
import java.util.UUID;

/**
 * Command representing a batch of offline mutation events received from a client device.
 */
public record ProcessSyncBatchCommand(
        String deviceId,
        UUID farmId,
        UUID userId,
        ConflictResolutionStrategy defaultStrategy,
        List<SyncEventCommandItem> events
) {
    public ProcessSyncBatchCommand {
        if (defaultStrategy == null) {
            defaultStrategy = ConflictResolutionStrategy.LAST_WRITE_WINS;
        }
        if (events == null) {
            events = Collections.emptyList();
        }
    }
}
