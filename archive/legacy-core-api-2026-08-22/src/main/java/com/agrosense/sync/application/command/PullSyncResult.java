package com.agrosense.sync.application.command;

import com.agrosense.sync.domain.model.SyncEvent;

import java.time.OffsetDateTime;
import java.util.List;
import java.util.UUID;

/**
 * Result of pulling synchronization events from the server.
 */
public record PullSyncResult(
        UUID farmId,
        OffsetDateTime serverTimestamp,
        List<SyncEvent> events,
        boolean hasMore
) {}
