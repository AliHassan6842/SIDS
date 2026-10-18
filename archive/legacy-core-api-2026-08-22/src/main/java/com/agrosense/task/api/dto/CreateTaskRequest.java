package com.agrosense.task.api.dto;

import com.agrosense.task.application.command.CreateTaskCommand;
import com.agrosense.task.domain.TaskPriority;
import com.agrosense.task.domain.TaskType;
import jakarta.validation.constraints.NotNull;

import java.time.Instant;
import java.util.UUID;

/**
 * HTTP request payload for creating a task.
 */
public record CreateTaskRequest(
        @NotNull(message = "farmId is required")
        UUID farmId,

        UUID fieldId,

        UUID recommendationId,

        UUID userId,

        @NotNull(message = "type is required")
        TaskType type,

        TaskPriority priority,

        Instant dueAt,

        String clientEventId
) {
    public CreateTaskCommand toCommand() {
        return new CreateTaskCommand(
                farmId,
                fieldId,
                recommendationId,
                userId,
                type,
                priority != null ? priority : TaskPriority.MEDIUM,
                dueAt
        );
    }
}
