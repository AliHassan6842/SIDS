package com.agrosense.task.api.dto;

/**
 * HTTP request payload for cancelling a task.
 */
public record CancelTaskRequest(
        String reason
) {}
