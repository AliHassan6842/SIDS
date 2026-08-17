package com.agrosense.task.application.command;

import com.agrosense.task.domain.TaskPriority;

import java.time.Instant;
import java.util.UUID;

/**
 * Command to update mutable details of an existing task.
 */
public record UpdateTaskCommand(
        UUID fieldId,
        UUID userId,
        TaskPriority priority,
        Instant dueAt
) {}
