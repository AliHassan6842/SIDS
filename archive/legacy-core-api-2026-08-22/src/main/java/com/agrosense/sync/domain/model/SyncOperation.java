package com.agrosense.sync.domain.model;

/**
 * Supported data operations in offline synchronization events.
 */
public enum SyncOperation {
    CREATE,
    UPDATE,
    DELETE,
    PATCH;

    public static SyncOperation fromString(String value) {
        if (value == null || value.isBlank()) {
            return UPDATE;
        }
        try {
            return SyncOperation.valueOf(value.trim().toUpperCase());
        } catch (IllegalArgumentException e) {
            return UPDATE;
        }
    }
}
