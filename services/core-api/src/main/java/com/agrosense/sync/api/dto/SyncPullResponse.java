package com.agrosense.sync.api.dto;

import java.time.OffsetDateTime;
import java.util.List;
import java.util.UUID;

/**
 * Response payload containing server changes for delta synchronization.
 */
public record SyncPullResponse(
        UUID farmId,
        OffsetDateTime serverTimestamp,
        List<PullEntityItemDto> events,
        boolean hasMore
) {}
