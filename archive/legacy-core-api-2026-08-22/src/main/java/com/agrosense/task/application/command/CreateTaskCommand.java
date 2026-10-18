package com.agrosense.task.application.command;

import com.agrosense.task.domain.TaskPriority;
import com.agrosense.task.domain.TaskType;

import java.time.Instant;
import java.util.UUID;

/**
 * Command to create a new task.
 */
public record CreateTaskCommand(
        UUID farmId,
        UUID fieldId,
        UUID recommendationId,
        UUID userId,
        TaskType type,
        TaskPriority priority,
        Instant dueAt
) {}
