package com.agrosense.sync.domain.exception;

import com.agrosense.shared.error.exceptions.BaseException;

import java.util.Map;
import java.util.UUID;

/**
 * Thrown when an offline client attempts to modify an entity using an obsolete base version.
 */
public class StaleVersionException extends BaseException {

    public StaleVersionException(String message, UUID entityId, Long baseVersion, Long currentServerVersion) {
        super(
                message,
                "SYNC_STALE_VERSION",
                true,
                Map.of(
                        "entityId", entityId != null ? entityId.toString() : "unknown",
                        "baseVersion", baseVersion != null ? baseVersion : -1,
                        "currentServerVersion", currentServerVersion != null ? currentServerVersion : -1
                )
        );
    }
}
