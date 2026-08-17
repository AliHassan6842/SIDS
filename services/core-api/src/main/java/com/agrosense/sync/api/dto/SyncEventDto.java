package com.agrosense.sync.api.dto;

import com.agrosense.sync.domain.model.ConflictResolutionStrategy;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

import java.time.OffsetDateTime;
import java.util.UUID;

/**
 * Transport DTO representing an individual offline event sent by a client device.
 */
public record SyncEventDto(
        @NotBlank(message = "clientEventId is required")
        String clientEventId,

        @NotNull(message = "entityId is required")
        UUID entityId,

        @NotBlank(message = "entityType is required")
        String entityType,

        String operation,

        Long baseVersion,

        String payload,

        OffsetDateTime createdAtDevice,

        ConflictResolutionStrategy preferredStrategy
) {}
