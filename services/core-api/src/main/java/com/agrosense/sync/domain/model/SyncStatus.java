package com.agrosense.sync.domain.model;

/**
 * Represents the lifecycle and processing status of a synchronization event.
 */
public enum SyncStatus {
    /**
     * Event was successfully applied to the system.
     */
    APPLIED,

    /**
     * Event was already processed previously; duplicate ignored idempotently.
     */
    DUPLICATE_IGNORED,

    /**
     * Version mismatch/conflict was detected and resolved in favor of the client.
     */
    CONFLICT_RESOLVED_CLIENT_WINS,

    /**
     * Version mismatch/conflict was detected and resolved in favor of the server.
     */
    CONFLICT_RESOLVED_SERVER_WINS,

    /**
     * Optimistic lock conflict detected and requires manual resolution or retry.
     */
    CONFLICT_DETECTED,

    /**
     * Event rejected due to stale base version under strict concurrency rules.
     */
    REJECTED_STALE_VERSION,

    /**
     * Event processing failed due to validation or system error.
     */
    FAILED
}
