package com.agrosense.task.api;

import com.agrosense.task.api.dto.AssignTaskRequest;
import com.agrosense.task.api.dto.CancelTaskRequest;
import com.agrosense.task.api.dto.CreateTaskRequest;
import com.agrosense.task.api.dto.TaskResponse;
import com.agrosense.task.api.dto.UpdateTaskRequest;
import com.agrosense.task.application.TaskService;
import com.agrosense.task.application.dto.RecommendationTaskSummaryDto;
import com.agrosense.task.application.dto.TaskDto;
import com.agrosense.task.domain.TaskStatus;
import com.agrosense.task.domain.TaskType;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PatchMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.UUID;

/**
 * REST controller exposing endpoints for Task lifecycle management, recommendation tracking, and idempotency.
 */
@RestController
@RequestMapping("/api/v1/tasks")
@Tag(name = "Tasks", description = "Endpoints for managing agricultural tasks, rescouting, and recommendation execution")
public class TaskController {

    private final TaskService taskService;

    public TaskController(TaskService taskService) {
        this.taskService = taskService;
    }

    /**
     * Creates a new task with optional idempotency key.
     */
    @PostMapping
    @Operation(summary = "Create task", description = "Creates a new task with optional idempotency key header or body token")
    public ResponseEntity<TaskResponse> createTask(
            @RequestHeader(value = "X-Idempotency-Key", required = false) String idempotencyHeader,
            @Valid @RequestBody CreateTaskRequest request
    ) {
        String clientEventId = (idempotencyHeader != null && !idempotencyHeader.isBlank())
                ? idempotencyHeader
                : request.clientEventId();

        TaskDto dto = taskService.createTask(request.toCommand(), clientEventId);
        return ResponseEntity.status(HttpStatus.CREATED).body(TaskResponse.fromDto(dto));
    }

    /**
     * Retrieves a task by ID.
     */
    @GetMapping("/{id}")
    @Operation(summary = "Get task by ID")
    public ResponseEntity<TaskResponse> getTaskById(@PathVariable UUID id) {
        TaskDto dto = taskService.getTaskById(id);
        return ResponseEntity.ok(TaskResponse.fromDto(dto));
    }

    /**
     * Queries tasks by various filters.
     */
    @GetMapping
    @Operation(summary = "List tasks", description = "Query tasks by farm, user, field, recommendation, status, or type")
    public ResponseEntity<List<TaskResponse>> listTasks(
            @RequestParam(required = false) UUID farmId,
            @RequestParam(required = false) UUID userId,
            @RequestParam(required = false) UUID fieldId,
            @RequestParam(required = false) UUID recommendationId,
            @RequestParam(required = false) TaskStatus status,
            @RequestParam(required = false) TaskType type
    ) {
        List<TaskDto> dtos;
        if (recommendationId != null) {
            dtos = taskService.getTasksByRecommendation(recommendationId);
        } else if (userId != null) {
            dtos = taskService.getTasksByUser(userId, status);
        } else if (fieldId != null) {
            dtos = taskService.getTasksByField(fieldId, status);
        } else if (farmId != null) {
            dtos = taskService.getTasksByFarm(farmId, status, type);
        } else {
            // When no specific filter is given, return an empty list or throw to avoid unbounded table scans
            dtos = List.of();
        }

        List<TaskResponse> response = dtos.stream().map(TaskResponse::fromDto).toList();
        return ResponseEntity.ok(response);
    }

    /**
     * Transitions task status to IN_PROGRESS.
     */
    @PatchMapping("/{id}/start")
    @Operation(summary = "Start task", description = "Transitions task lifecycle to IN_PROGRESS and assigns worker if specified")
    public ResponseEntity<TaskResponse> startTask(
            @PathVariable UUID id,
            @RequestParam(required = false) UUID workerId
    ) {
        TaskDto dto = taskService.startTask(id, workerId);
        return ResponseEntity.ok(TaskResponse.fromDto(dto));
    }

    /**
     * Transitions task status to COMPLETED.
     */
    @PatchMapping("/{id}/complete")
    @Operation(summary = "Complete task", description = "Transitions task lifecycle to COMPLETED")
    public ResponseEntity<TaskResponse> completeTask(@PathVariable UUID id) {
        TaskDto dto = taskService.completeTask(id);
        return ResponseEntity.ok(TaskResponse.fromDto(dto));
    }

    /**
     * Transitions task status to CANCELLED.
     */
    @PatchMapping("/{id}/cancel")
    @Operation(summary = "Cancel task", description = "Transitions task lifecycle to CANCELLED")
    public ResponseEntity<TaskResponse> cancelTask(
            @PathVariable UUID id,
            @RequestBody(required = false) CancelTaskRequest request
    ) {
        String reason = request != null ? request.reason() : null;
        TaskDto dto = taskService.cancelTask(id, reason);
        return ResponseEntity.ok(TaskResponse.fromDto(dto));
    }

    /**
     * Assigns or reassigns task to a user.
     */
    @PatchMapping("/{id}/assign")
    @Operation(summary = "Assign task", description = "Assigns task to a specific worker")
    public ResponseEntity<TaskResponse> assignTask(
            @PathVariable UUID id,
            @Valid @RequestBody AssignTaskRequest request
    ) {
        TaskDto dto = taskService.assignTask(id, request.userId());
        return ResponseEntity.ok(TaskResponse.fromDto(dto));
    }

    /**
     * Updates mutable properties of a task.
     */
    @PutMapping("/{id}")
    @Operation(summary = "Update task", description = "Updates editable details such as priority, due date, field, or worker")
    public ResponseEntity<TaskResponse> updateTask(
            @PathVariable UUID id,
            @Valid @RequestBody UpdateTaskRequest request
    ) {
        TaskDto dto = taskService.updateTask(id, request.toCommand());
        return ResponseEntity.ok(TaskResponse.fromDto(dto));
    }

    /**
     * Retrieves resolution and task lifecycle summary for an agronomic recommendation.
     */
    @GetMapping("/recommendation/{recommendationId}/summary")
    @Operation(summary = "Recommendation task summary", description = "Provides execution and resolution metrics for tasks linked to a recommendation")
    public ResponseEntity<RecommendationTaskSummaryDto> getRecommendationSummary(
            @PathVariable UUID recommendationId
    ) {
        RecommendationTaskSummaryDto summary = taskService.getRecommendationTaskSummary(recommendationId);
        return ResponseEntity.ok(summary);
    }
}
