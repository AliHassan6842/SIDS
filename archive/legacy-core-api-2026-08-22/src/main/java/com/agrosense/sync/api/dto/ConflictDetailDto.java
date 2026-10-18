package com.agrosense.sync.api.dto;

/**
 * Transport DTO detailing optimistic locking conflict evaluation and resolution metrics.
 */
public record ConflictDetailDto(
        Long clientBaseVersion,
        Long serverCurrentVersion,
        String strategyApplied,
        String resolutionSummary
) {}
