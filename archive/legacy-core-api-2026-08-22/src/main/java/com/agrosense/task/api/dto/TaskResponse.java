package com.agrosense.task.api.dto;

import com.agrosense.task.application.dto.TaskDto;
import com.agrosense.task.domain.TaskPriority;
import com.agrosense.task.domain.TaskStatus;
import com.agrosense.task.domain.TaskType;

import java.time.Instant;
import java.util.UUID;

/**
 * HTTP response payload representing a task.
 */
public record TaskResponse(
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
    public static TaskResponse fromDto(TaskDto dto) {
        if (dto == null) {
            return null;
        }
        return new TaskResponse(
                dto.id(),
                dto.type(),
                dto.status(),
                dto.priority(),
                dto.dueAt(),
                dto.userId(),
                dto.farmId(),
                dto.fieldId(),
                dto.recommendationId(),
                dto.version(),
                dto.createdAt(),
                dto.updatedAt(),
                dto.isOverdue()
        );
    }
}
