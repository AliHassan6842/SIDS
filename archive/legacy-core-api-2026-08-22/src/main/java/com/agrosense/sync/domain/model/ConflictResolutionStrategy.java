package com.agrosense.sync.domain.model;

/**
 * Strategies for handling conflicts between offline client updates and server state.
 */
public enum ConflictResolutionStrategy {
    /**
     * Compare device timestamp and server last updated timestamp; newer timestamp wins.
     */
    LAST_WRITE_WINS,

    /**
     * Always accept the client update and overwrite the server state, incrementing server version.
     */
    CLIENT_WINS,

    /**
     * Retain the server's current state and reject/suppress the client's conflicting modification.
     */
    SERVER_WINS,

    /**
     * Reject the update immediately and flag the conflict for explicit manual resolution.
     */
    FAIL_ON_CONFLICT;

    public static ConflictResolutionStrategy fromString(String value) {
        if (value == null || value.isBlank()) {
            return LAST_WRITE_WINS;
        }
        try {
            return ConflictResolutionStrategy.valueOf(value.trim().toUpperCase());
        } catch (IllegalArgumentException e) {
            return LAST_WRITE_WINS;
        }
    }
}
