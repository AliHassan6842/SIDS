package com.agrosense.sync.api.dto;

import java.time.OffsetDateTime;
import java.util.List;

/**
 * Response payload containing processing metrics and per-event outcomes for a sync push batch.
 */
public record SyncPushResponse(
        int totalProcessed,
        int applied,
        int duplicates,
        int conflicts,
        int failed,
        List<SyncEventResultDto> results,
        OffsetDateTime serverTime
) {}
