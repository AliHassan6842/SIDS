package com.agrosense.task.application;

import com.agrosense.shared.error.exceptions.BusinessRuleViolationException;
import com.agrosense.shared.error.exceptions.ResourceNotFoundException;
import com.agrosense.task.application.command.CreateTaskCommand;
import com.agrosense.task.application.command.UpdateTaskCommand;
import com.agrosense.task.application.dto.RecommendationTaskSummaryDto;
import com.agrosense.task.application.dto.TaskDto;
import com.agrosense.task.domain.IdempotencyRecord;
import com.agrosense.task.domain.Task;
import com.agrosense.task.domain.TaskPriority;
import com.agrosense.task.domain.TaskStatus;
import com.agrosense.task.domain.TaskType;
import com.agrosense.task.infrastructure.IdempotencyRecordJpaRepository;
import com.agrosense.task.infrastructure.TaskJpaRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Instant;
import java.util.List;
import java.util.Objects;
import java.util.Optional;
import java.util.UUID;

/**
 * Application service managing Task lifecycle, recommendation tracking, and idempotency guarantees.
 */
@Service
@Transactional
public class TaskService {

    private static final String RESOURCE_TYPE_TASK = "TASK";

    private final TaskJpaRepository taskRepository;
    private final IdempotencyRecordJpaRepository idempotencyRepository;

    public TaskService(TaskJpaRepository taskRepository,
                       IdempotencyRecordJpaRepository idempotencyRepository) {
        this.taskRepository = taskRepository;
        this.idempotencyRepository = idempotencyRepository;
    }

    /**
     * Creates a new task with idempotency verification.
     * If the clientEventId was already processed, returns the existing task to prevent duplicates.
     */
    public TaskDto createTask(CreateTaskCommand command, String clientEventId) {
        // 1. Check idempotency if clientEventId is supplied
        if (clientEventId != null && !clientEventId.isBlank()) {
            Optional<IdempotencyRecord> existingRecord =
                    idempotencyRepository.findByClientEventIdAndResourceType(clientEventId, RESOURCE_TYPE_TASK);

            if (existingRecord.isPresent()) {
                UUID existingTaskId = existingRecord.get().getResourceId();
                return taskRepository.findById(existingTaskId)
                        .map(TaskDto::fromEntity)
                        .orElseThrow(() -> new ResourceNotFoundException(
                                "Referenced idempotent task not found: " + existingTaskId,
                                RESOURCE_TYPE_TASK,
                                existingTaskId.toString()
                        ));
            }
        }

        // 2. Validate domain requirements
        if (command.farmId() == null) {
            throw new BusinessRuleViolationException("Farm ID is required to create a task", "MISSING_FARM_ID");
        }
        if (command.type() == null) {
            throw new BusinessRuleViolationException("Task type is required", "MISSING_TASK_TYPE");
        }

        // 3. Instantiate domain entity
        Task task = Task.create(
                command.farmId(),
                command.fieldId(),
                command.recommendationId(),
                command.userId(),
                command.type(),
                command.priority() != null ? command.priority() : TaskPriority.MEDIUM,
                command.dueAt()
        );

        Task savedTask = taskRepository.save(task);

        // 4. Save idempotency record if clientEventId is supplied
        if (clientEventId != null && !clientEventId.isBlank()) {
            IdempotencyRecord record = IdempotencyRecord.ofTask(clientEventId, savedTask.getId());
            idempotencyRepository.save(record);
        }

        return TaskDto.fromEntity(savedTask);
    }

    /**
     * Creates a follow-up or review task directly linked to an agronomic recommendation.
     */
    public TaskDto createTaskForRecommendation(
            UUID recommendationId,
            UUID farmId,
            UUID fieldId,
            TaskType type,
            TaskPriority priority,
            Instant dueAt,
            UUID assignedUserId,
            String clientEventId
    ) {
        Objects.requireNonNull(recommendationId, "Recommendation ID cannot be null");
        CreateTaskCommand command = new CreateTaskCommand(
                farmId,
                fieldId,
                recommendationId,
                assignedUserId,
                type != null ? type : TaskType.FOLLOW_UP,
                priority != null ? priority : TaskPriority.HIGH,
                dueAt
        );
        return createTask(command, clientEventId);
    }

    /**
     * Retrieves a task by its unique identifier.
     */
    @Transactional(readOnly = true)
    public TaskDto getTaskById(UUID taskId) {
        return TaskDto.fromEntity(findTaskOrThrow(taskId));
    }

    /**
     * Retrieves tasks for a given farm, optionally filtering by status and type.
     */
    @Transactional(readOnly = true)
    public List<TaskDto> getTasksByFarm(UUID farmId, TaskStatus status, TaskType type) {
        List<Task> tasks;
        if (status != null && type != null) {
            tasks = taskRepository.findByFarmIdAndTypeAndStatus(farmId, type, status);
        } else if (status != null) {
            tasks = taskRepository.findByFarmIdAndStatus(farmId, status);
        } else if (type != null) {
            tasks = taskRepository.findByFarmIdAndType(farmId, type);
        } else {
            tasks = taskRepository.findByFarmId(farmId);
        }
        return tasks.stream().map(TaskDto::fromEntity).toList();
    }

    /**
     * Retrieves tasks assigned to a specific user/scout.
     */
    @Transactional(readOnly = true)
    public List<TaskDto> getTasksByUser(UUID userId, TaskStatus status) {
        List<Task> tasks = (status != null)
                ? taskRepository.findByUserIdAndStatus(userId, status)
                : taskRepository.findByUserId(userId);
        return tasks.stream().map(TaskDto::fromEntity).toList();
    }

    /**
     * Retrieves tasks associated with a field.
     */
    @Transactional(readOnly = true)
    public List<TaskDto> getTasksByField(UUID fieldId, TaskStatus status) {
        List<Task> tasks = (status != null)
                ? taskRepository.findByFieldIdAndStatus(fieldId, status)
                : taskRepository.findByFieldId(fieldId);
        return tasks.stream().map(TaskDto::fromEntity).toList();
    }

    /**
     * Retrieves all tasks linked to a specific recommendation.
     */
    @Transactional(readOnly = true)
    public List<TaskDto> getTasksByRecommendation(UUID recommendationId) {
        return taskRepository.findByRecommendationId(recommendationId)
                .stream()
                .map(TaskDto::fromEntity)
                .toList();
    }

    /**
     * Tracks recommendation task completion metrics and resolution status.
     */
    @Transactional(readOnly = true)
    public RecommendationTaskSummaryDto getRecommendationTaskSummary(UUID recommendationId) {
        List<Task> tasks = taskRepository.findByRecommendationId(recommendationId);
        long total = tasks.size();
        long pending = tasks.stream().filter(t -> t.getStatus() == TaskStatus.PENDING).count();
        long inProgress = tasks.stream().filter(t -> t.getStatus() == TaskStatus.IN_PROGRESS).count();
        long completed = tasks.stream().filter(t -> t.getStatus() == TaskStatus.COMPLETED).count();
        long cancelled = tasks.stream().filter(t -> t.getStatus() == TaskStatus.CANCELLED).count();

        return RecommendationTaskSummaryDto.of(recommendationId, total, pending, inProgress, completed, cancelled);
    }

    /**
     * Starts execution of a task, transitioning status to IN_PROGRESS.
     */
    public TaskDto startTask(UUID taskId, UUID workerId) {
        Task task = findTaskOrThrow(taskId);
        task.start(workerId);
        return TaskDto.fromEntity(taskRepository.save(task));
    }

    /**
     * Marks a task as COMPLETED.
     */
    public TaskDto completeTask(UUID taskId) {
        Task task = findTaskOrThrow(taskId);
        task.complete();
        return TaskDto.fromEntity(taskRepository.save(task));
    }

    /**
     * Cancels a task.
     */
    public TaskDto cancelTask(UUID taskId, String reason) {
        Task task = findTaskOrThrow(taskId);
        task.cancel();
        return TaskDto.fromEntity(taskRepository.save(task));
    }

    /**
     * Reassigns a task to another worker.
     */
    public TaskDto assignTask(UUID taskId, UUID newUserId) {
        Task task = findTaskOrThrow(taskId);
        task.assignTo(newUserId);
        return TaskDto.fromEntity(taskRepository.save(task));
    }

    /**
     * Reschedules the task due date.
     */
    public TaskDto rescheduleTask(UUID taskId, Instant newDueAt) {
        Task task = findTaskOrThrow(taskId);
        task.reschedule(newDueAt);
        return TaskDto.fromEntity(taskRepository.save(task));
    }

    /**
     * Updates mutable fields of an existing task.
     */
    public TaskDto updateTask(UUID taskId, UpdateTaskCommand command) {
        Task task = findTaskOrThrow(taskId);
        if (command.fieldId() != null) {
            task.setFieldId(command.fieldId());
        }
        if (command.userId() != null) {
            task.assignTo(command.userId());
        }
        if (command.priority() != null) {
            task.changePriority(command.priority());
        }
        if (command.dueAt() != null) {
            task.reschedule(command.dueAt());
        }
        return TaskDto.fromEntity(taskRepository.save(task));
    }

    private Task findTaskOrThrow(UUID taskId) {
        return taskRepository.findById(taskId)
                .orElseThrow(() -> new ResourceNotFoundException(
                        "Task not found with ID: " + taskId,
                        RESOURCE_TYPE_TASK,
                        taskId.toString()
                ));
    }
}
