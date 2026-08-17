package com.agrosense.sync.application.command;

import java.time.OffsetDateTime;
import java.util.List;

/**
 * Summary result of processing a complete batch of synchronization events.
 */
public record SyncBatchResult(
        int totalEvents,
        int appliedCount,
        int duplicateCount,
        int conflictCount,
        int failedCount,
        List<SyncEventProcessingResult> eventResults,
        OffsetDateTime serverTimestamp
) {
    public static SyncBatchResult fromResults(List<SyncEventProcessingResult> eventResults) {
        int total = eventResults.size();
        int applied = 0;
        int duplicate = 0;
        int conflict = 0;
        int failed = 0;

        for (SyncEventProcessingResult r : eventResults) {
            switch (r.status()) {
                case APPLIED -> applied++;
                case DUPLICATE_IGNORED -> duplicate++;
                case CONFLICT_RESOLVED_CLIENT_WINS, CONFLICT_RESOLVED_SERVER_WINS -> conflict++;
                case CONFLICT_DETECTED, REJECTED_STALE_VERSION, FAILED -> failed++;
            }
        }

        return new SyncBatchResult(
                total,
                applied,
                duplicate,
                conflict,
                failed,
                eventResults,
                OffsetDateTime.now()
        );
    }
}
