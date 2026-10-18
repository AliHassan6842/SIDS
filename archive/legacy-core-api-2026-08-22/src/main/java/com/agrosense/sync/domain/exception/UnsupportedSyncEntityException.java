package com.agrosense.sync.domain.exception;

import com.agrosense.shared.error.exceptions.BaseException;

import java.util.Map;

/**
 * Thrown when an unrecognized or unsupported entity type is requested for synchronization.
 */
public class UnsupportedSyncEntityException extends BaseException {

    public UnsupportedSyncEntityException(String message, String entityType) {
        super(
                message,
                "SYNC_UNSUPPORTED_ENTITY",
                false,
                Map.of("entityType", entityType != null ? entityType : "unknown")
        );
    }
}
