package com.agrosense.task.infrastructure;

import com.agrosense.task.domain.Task;
import com.agrosense.task.domain.TaskPriority;
import com.agrosense.task.domain.TaskStatus;
import com.agrosense.task.domain.TaskType;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.time.Instant;
import java.util.List;
import java.util.UUID;

/**
 * Spring Data JPA Repository interface for Task management.
 */
@Repository
public interface TaskJpaRepository extends JpaRepository<Task, UUID> {

    List<Task> findByFarmId(UUID farmId);

    List<Task> findByFarmIdAndStatus(UUID farmId, TaskStatus status);

    List<Task> findByFarmIdAndType(UUID farmId, TaskType type);

    List<Task> findByFarmIdAndTypeAndStatus(UUID farmId, TaskType type, TaskStatus status);

    List<Task> findByUserId(UUID userId);

    List<Task> findByUserIdAndStatus(UUID userId, TaskStatus status);

    List<Task> findByFieldId(UUID fieldId);

    List<Task> findByFieldIdAndStatus(UUID fieldId, TaskStatus status);

    List<Task> findByRecommendationId(UUID recommendationId);

    List<Task> findByRecommendationIdAndStatus(UUID recommendationId, TaskStatus status);

    List<Task> findByFarmIdAndPriority(UUID farmId, TaskPriority priority);

    List<Task> findByFarmIdAndDueAtBeforeAndStatusNot(UUID farmId, Instant dueAt, TaskStatus status);

    long countByRecommendationId(UUID recommendationId);

    long countByRecommendationIdAndStatus(UUID recommendationId, TaskStatus status);
}
