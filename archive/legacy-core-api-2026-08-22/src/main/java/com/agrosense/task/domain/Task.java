package com.agrosense.task.domain;

import com.agrosense.shared.error.exceptions.BusinessRuleViolationException;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import jakarta.persistence.Version;

import java.time.Instant;
import java.util.Objects;
import java.util.UUID;

/**
 * Represents a field scouting, inspection, or follow-up task.
 */
@Entity
@Table(name = "tasks")
public class Task {

    @Id
    private UUID id;

    @Enumerated(EnumType.STRING)
    @Column(name = "type", nullable = false, length = 50)
    private TaskType type;

    @Enumerated(EnumType.STRING)
    @Column(name = "status", nullable = false, length = 50)
    private TaskStatus status;

    @Enumerated(EnumType.STRING)
    @Column(name = "priority", nullable = false, length = 50)
    private TaskPriority priority;

    @Column(name = "due_at")
    private Instant dueAt;

    @Column(name = "user_id")
    private UUID userId;

    @Column(name = "farm_id", nullable = false)
    private UUID farmId;

    @Column(name = "field_id")
    private UUID fieldId;

    @Column(name = "recommendation_id")
    private UUID recommendationId;

    @Version
    @Column(name = "version", nullable = false)
    private Long version;

    @Column(name = "created_at", nullable = false)
    private Instant createdAt;

    @Column(name = "updated_at", nullable = false)
    private Instant updatedAt;

    public Task() {
    }

    public Task(UUID id,
                TaskType type,
                TaskPriority priority,
                UUID farmId,
                UUID fieldId,
                UUID recommendationId,
                UUID userId,
                Instant dueAt) {
        this.id = id != null ? id : UUID.randomUUID();
        this.type = Objects.requireNonNull(type, "Task type cannot be null");
        this.priority = priority != null ? priority : TaskPriority.MEDIUM;
        this.farmId = Objects.requireNonNull(farmId, "Farm ID cannot be null");
        this.fieldId = fieldId;
        this.recommendationId = recommendationId;
        this.userId = userId;
        this.dueAt = dueAt;
        this.status = TaskStatus.PENDING;
        this.version = 0L;
        this.createdAt = Instant.now();
        this.updatedAt = this.createdAt;
    }

    public static Task create(UUID farmId,
                              UUID fieldId,
                              UUID recommendationId,
                              UUID userId,
                              TaskType type,
                              TaskPriority priority,
                              Instant dueAt) {
        return new Task(UUID.randomUUID(), type, priority, farmId, fieldId, recommendationId, userId, dueAt);
    }

    /**
     * Starts execution of the task and optionally assigns/confirms the worker.
     */
    public void start(UUID workerId) {
        ensureCanTransitionTo(TaskStatus.IN_PROGRESS);
        if (workerId != null) {
            this.userId = workerId;
        }
        this.status = TaskStatus.IN_PROGRESS;
        this.updatedAt = Instant.now();
    }

    /**
     * Marks the task as completed.
     */
    public void complete() {
        ensureCanTransitionTo(TaskStatus.COMPLETED);
        this.status = TaskStatus.COMPLETED;
        this.updatedAt = Instant.now();
    }

    /**
     * Cancels the task.
     */
    public void cancel() {
        ensureCanTransitionTo(TaskStatus.CANCELLED);
        this.status = TaskStatus.CANCELLED;
        this.updatedAt = Instant.now();
    }

    /**
     * Assigns the task to a specific user.
     */
    public void assignTo(UUID newUserId) {
        if (this.status.isTerminal()) {
            throw new BusinessRuleViolationException(
                    "Cannot assign a task that is in terminal state: " + this.status,
                    "TASK_TERMINAL_STATE"
            );
        }
        this.userId = newUserId;
        this.updatedAt = Instant.now();
    }

    /**
     * Reschedules the task due date.
     */
    public void reschedule(Instant newDueAt) {
        if (this.status.isTerminal()) {
            throw new BusinessRuleViolationException(
                    "Cannot reschedule a task that is in terminal state: " + this.status,
                    "TASK_TERMINAL_STATE"
            );
        }
        this.dueAt = newDueAt;
        this.updatedAt = Instant.now();
    }

    /**
     * Updates task priority.
     */
    public void changePriority(TaskPriority newPriority) {
        if (this.status.isTerminal()) {
            throw new BusinessRuleViolationException(
                    "Cannot update priority on a task in terminal state: " + this.status,
                    "TASK_TERMINAL_STATE"
            );
        }
        if (newPriority != null) {
            this.priority = newPriority;
            this.updatedAt = Instant.now();
        }
    }

    /**
     * Checks if task is overdue relative to a reference time.
     */
    public boolean isOverdue(Instant referenceTime) {
        if (this.status.isTerminal() || this.dueAt == null) {
            return false;
        }
        return this.dueAt.isBefore(referenceTime != null ? referenceTime : Instant.now());
    }

    private void ensureCanTransitionTo(TaskStatus targetStatus) {
        if (!this.status.canTransitionTo(targetStatus)) {
            throw new BusinessRuleViolationException(
                    String.format("Invalid task lifecycle transition from %s to %s for task %s", this.status, targetStatus, this.id),
                    "INVALID_TASK_TRANSITION"
            );
        }
    }

    // Getters and Setters
    public UUID getId() {
        return id;
    }

    public void setId(UUID id) {
        this.id = id;
    }

    public TaskType getType() {
        return type;
    }

    public void setType(TaskType type) {
        this.type = type;
    }

    public TaskStatus getStatus() {
        return status;
    }

    public void setStatus(TaskStatus status) {
        this.status = status;
    }

    public TaskPriority getPriority() {
        return priority;
    }

    public void setPriority(TaskPriority priority) {
        this.priority = priority;
    }

    public Instant getDueAt() {
        return dueAt;
    }

    public void setDueAt(Instant dueAt) {
        this.dueAt = dueAt;
    }

    public UUID getUserId() {
        return userId;
    }

    public void setUserId(UUID userId) {
        this.userId = userId;
    }

    public UUID getFarmId() {
        return farmId;
    }

    public void setFarmId(UUID farmId) {
        this.farmId = farmId;
    }

    public UUID getFieldId() {
        return fieldId;
    }

    public void setFieldId(UUID fieldId) {
        this.fieldId = fieldId;
    }

    public UUID getRecommendationId() {
        return recommendationId;
    }

    public void setRecommendationId(UUID recommendationId) {
        this.recommendationId = recommendationId;
    }

    public Long getVersion() {
        return version;
    }

    public void setVersion(Long version) {
        this.version = version;
    }

    public Instant getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(Instant createdAt) {
        this.createdAt = createdAt;
    }

    public Instant getUpdatedAt() {
        return updatedAt;
    }

    public void setUpdatedAt(Instant updatedAt) {
        this.updatedAt = updatedAt;
    }
}
