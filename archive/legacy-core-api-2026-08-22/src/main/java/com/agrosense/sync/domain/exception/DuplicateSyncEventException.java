package com.agrosense.sync.domain.exception;

import com.agrosense.shared.error.exceptions.BaseException;

import java.util.Map;

/**
 * Thrown when a sync event with an identical clientEventId has already been recorded.
 */
public class DuplicateSyncEventException extends BaseException {

    public DuplicateSyncEventException(String message, String clientEventId) {
        super(
                message,
                "SYNC_DUPLICATE_EVENT",
                false,
                Map.of("clientEventId", clientEventId != null ? clientEventId : "unknown")
        );
    }
}
