package com.agrosense.sync.api.dto;

import com.agrosense.sync.domain.model.SyncStatus;

import java.util.UUID;

/**
 * Transport DTO representing the outcome of processing an individual sync event.
 */
public record SyncEventResultDto(
        String clientEventId,
        UUID entityId,
        String entityType,
        SyncStatus status,
        Long baseVersion,
        Long resolvedVersion,
        boolean conflictDetected,
        String message,
        ConflictDetailDto conflictDetails
) {}
