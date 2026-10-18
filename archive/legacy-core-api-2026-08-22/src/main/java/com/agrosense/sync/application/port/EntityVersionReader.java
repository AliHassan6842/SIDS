package com.agrosense.sync.application.port;

import java.time.OffsetDateTime;
import java.util.Optional;
import java.util.UUID;

/**
 * Port for inspecting the persistent concurrency version and modification timestamp of synchronizable entities.
 */
public interface EntityVersionReader {

    /**
     * Reads current state summary for optimistic locking evaluation.
     */
    Optional<EntityStateSummary> readEntityState(String entityType, UUID entityId);

    /**
     * Entity state summary containing version and modification details.
     */
    record EntityStateSummary(
            UUID entityId,
            String entityType,
            Long version,
            OffsetDateTime lastModifiedAt,
            boolean exists
    ) {}
}
