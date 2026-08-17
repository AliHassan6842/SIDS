package com.agrosense.task.application.dto;

import com.agrosense.task.domain.Task;
import com.agrosense.task.domain.TaskPriority;
import com.agrosense.task.domain.TaskStatus;
import com.agrosense.task.domain.TaskType;

import java.time.Instant;
import java.util.UUID;

/**
 * Data transfer object representing task state.
 */
public record TaskDto(
        UUID id,
        TaskType type,
        TaskStatus status,
        TaskPriority priority,
        Instant dueAt,
        UUID userId,
        UUID farmId,
        UUID fieldId,
        UUID recommendationId,
        Long version,
        Instant createdAt,
        Instant updatedAt,
        boolean isOverdue
) {
    public static TaskDto fromEntity(Task task) {
        if (task == null) {
            return null;
        }
        return new TaskDto(
                task.getId(),
                task.getType(),
                task.getStatus(),
                task.getPriority(),
                task.getDueAt(),
                task.getUserId(),
                task.getFarmId(),
                task.getFieldId(),
                task.getRecommendationId(),
                task.getVersion(),
                task.getCreatedAt(),
                task.getUpdatedAt(),
                task.isOverdue(Instant.now())
        );
    }
}
