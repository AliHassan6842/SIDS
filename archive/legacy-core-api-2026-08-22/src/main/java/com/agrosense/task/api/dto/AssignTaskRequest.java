package com.agrosense.task.api.dto;

import jakarta.validation.constraints.NotNull;
import java.util.UUID;

/**
 * HTTP request payload for assigning a task to a user.
 */
public record AssignTaskRequest(
        @NotNull(message = "userId is required")
        UUID userId
) {}
