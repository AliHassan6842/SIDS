package com.agrosense.task.api.dto;

import com.agrosense.task.application.command.UpdateTaskCommand;
import com.agrosense.task.domain.TaskPriority;

import java.time.Instant;
import java.util.UUID;

/**
 * HTTP request payload for updating an existing task.
 */
public record UpdateTaskRequest(
        UUID fieldId,
        UUID userId,
        TaskPriority priority,
        Instant dueAt
) {
    public UpdateTaskCommand toCommand() {
        return new UpdateTaskCommand(fieldId, userId, priority, dueAt);
    }
}
