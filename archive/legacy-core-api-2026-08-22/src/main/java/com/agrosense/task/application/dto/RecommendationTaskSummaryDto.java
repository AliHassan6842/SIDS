package com.agrosense.task.application.dto;

import java.util.UUID;

/**
 * Summary DTO for tracking lifecycle status of tasks generated for a recommendation.
 */
public record RecommendationTaskSummaryDto(
        UUID recommendationId,
        long totalTasks,
        long pendingTasks,
        long inProgressTasks,
        long completedTasks,
        long cancelledTasks,
        boolean isFullyCompleted
) {
    public static RecommendationTaskSummaryDto of(
            UUID recommendationId,
            long totalTasks,
            long pendingTasks,
            long inProgressTasks,
            long completedTasks,
            long cancelledTasks
    ) {
        boolean fullyCompleted = totalTasks > 0 && pendingTasks == 0 && inProgressTasks == 0;
        return new RecommendationTaskSummaryDto(
                recommendationId,
                totalTasks,
                pendingTasks,
                inProgressTasks,
                completedTasks,
                cancelledTasks,
                fullyCompleted
        );
    }
}
