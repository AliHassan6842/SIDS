package com.agrosense.sync.api.dto;

import com.agrosense.sync.domain.model.ConflictResolutionStrategy;
import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.NotNull;

import java.util.List;
import java.util.UUID;

/**
 * Request payload for pushing a batch of offline synchronization events.
 */
public record SyncPushRequest(
        @NotBlank(message = "deviceId is required")
        String deviceId,

        @NotNull(message = "farmId is required")
        UUID farmId,

        UUID userId,

        ConflictResolutionStrategy defaultStrategy,

        @NotEmpty(message = "events list cannot be empty")
        @Valid
        List<SyncEventDto> events
) {}
