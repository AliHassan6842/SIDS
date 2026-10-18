package com.agrosense.sync.domain.policy;

import com.agrosense.sync.domain.model.ConflictResolutionResult;
import com.agrosense.sync.domain.model.ConflictResolutionStrategy;
import com.agrosense.sync.domain.model.SyncEvent;

import java.time.OffsetDateTime;

/**
 * Standard domain implementation of conflict resolution policy.
 * Supports CLIENT_WINS, SERVER_WINS, LAST_WRITE_WINS, and FAIL_ON_CONFLICT.
 */
public class DefaultConflictResolutionPolicy implements ConflictResolutionPolicy {

    @Override
    public ConflictResolutionResult resolveConflict(
            SyncEvent event,
            Long currentServerVersion,
            OffsetDateTime serverLastModifiedAt,
            ConflictResolutionStrategy strategy) {

        if (strategy == null) {
            strategy = ConflictResolutionStrategy.LAST_WRITE_WINS;
        }

        long safeServerVersion = currentServerVersion != null ? currentServerVersion : 0L;

        return switch (strategy) {
            case CLIENT_WINS -> {
                long nextVersion = safeServerVersion + 1;
                yield ConflictResolutionResult.clientWins(
                        nextVersion,
                        "Client update accepted explicitly via CLIENT_WINS strategy.",
                        event.getPayload()
                );
            }
            case SERVER_WINS -> ConflictResolutionResult.serverWins(
                    safeServerVersion,
                    "Server version retained; client update suppressed via SERVER_WINS strategy.",
                    null
            );
            case FAIL_ON_CONFLICT -> ConflictResolutionResult.unresolvedConflict(
                    safeServerVersion,
                    "Conflict detected under strict optimistic locking (baseVersion="
                            + event.getBaseVersion() + ", serverVersion=" + safeServerVersion + ")."
            );
            case LAST_WRITE_WINS -> resolveLastWriteWins(event, safeServerVersion, serverLastModifiedAt);
        };
    }

    private ConflictResolutionResult resolveLastWriteWins(
            SyncEvent event,
            long safeServerVersion,
            OffsetDateTime serverLastModifiedAt) {

        OffsetDateTime deviceTimestamp = event.getCreatedAtDevice();

        // If server timestamp is unavailable or client device timestamp is strictly newer, client wins
        if (serverLastModifiedAt == null || (deviceTimestamp != null && deviceTimestamp.isAfter(serverLastModifiedAt))) {
            long nextVersion = safeServerVersion + 1;
            return ConflictResolutionResult.clientWins(
                    nextVersion,
                    "Conflict resolved: client mutation is newer (" + deviceTimestamp + " > " + serverLastModifiedAt + ").",
                    event.getPayload()
            );
        } else {
            return ConflictResolutionResult.serverWins(
                    safeServerVersion,
                    "Conflict resolved: server state is newer or equal (" + serverLastModifiedAt + " >= " + deviceTimestamp + ").",
                    null
            );
        }
    }
}
