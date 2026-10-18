package com.agrosense.task.domain;

/**
 * Lifecycle status for agricultural tasks.
 */
public enum TaskStatus {
    /**
     * Task created and waiting for pickup or assignment.
     */
    PENDING,

    /**
     * Task is currently being performed by an assigned scout or agronomist.
     */
    IN_PROGRESS,

    /**
     * Task has been successfully executed and resolved.
     */
    COMPLETED,

    /**
     * Task has been cancelled or dismissed.
     */
    CANCELLED;

    /**
     * Checks if the status is a terminal state (cannot transition further).
     */
    public boolean isTerminal() {
        return this == COMPLETED || this == CANCELLED;
    }

    /**
     * Checks if a transition from this state to the target state is logically permissible.
     *
     * @param targetStatus the desired status to transition to
     * @return true if valid, false otherwise
     */
    public boolean canTransitionTo(TaskStatus targetStatus) {
        if (targetStatus == null || this == targetStatus) {
            return true;
        }

        return switch (this) {
            case PENDING -> targetStatus == IN_PROGRESS || targetStatus == COMPLETED || targetStatus == CANCELLED;
            case IN_PROGRESS -> targetStatus == COMPLETED || targetStatus == CANCELLED || targetStatus == PENDING;
            case COMPLETED, CANCELLED -> false;
        };
    }
}
