package com.agrosense.sync.domain.model;

import java.util.Objects;

/**
 * Encapsulates the evaluation result of offline conflict resolution.
 */
public class ConflictResolutionResult {

    private final boolean resolved;
    private final ConflictResolutionStrategy strategyApplied;
    private final SyncStatus syncStatus;
    private final Long resolvedVersion;
    private final String message;
    private final Object winningPayload;

    public ConflictResolutionResult(
            boolean resolved,
            ConflictResolutionStrategy strategyApplied,
            SyncStatus syncStatus,
            Long resolvedVersion,
            String message,
            Object winningPayload) {
        this.resolved = resolved;
        this.strategyApplied = strategyApplied;
        this.syncStatus = syncStatus;
        this.resolvedVersion = resolvedVersion;
        this.message = message;
        this.winningPayload = winningPayload;
    }

    public static ConflictResolutionResult clientWins(Long newVersion, String message, Object payload) {
        return new ConflictResolutionResult(
                true,
                ConflictResolutionStrategy.CLIENT_WINS,
                SyncStatus.CONFLICT_RESOLVED_CLIENT_WINS,
                newVersion,
                message != null ? message : "Conflict resolved: client version applied.",
                payload
        );
    }

    public static ConflictResolutionResult serverWins(Long currentServerVersion, String message, Object payload) {
        return new ConflictResolutionResult(
                true,
                ConflictResolutionStrategy.SERVER_WINS,
                SyncStatus.CONFLICT_RESOLVED_SERVER_WINS,
                currentServerVersion,
                message != null ? message : "Conflict resolved: server version preserved.",
                payload
        );
    }

    public static ConflictResolutionResult unresolvedConflict(Long currentServerVersion, String message) {
        return new ConflictResolutionResult(
                false,
                ConflictResolutionStrategy.FAIL_ON_CONFLICT,
                SyncStatus.CONFLICT_DETECTED,
                currentServerVersion,
                message != null ? message : "Optimistic locking conflict detected; manual resolution required.",
                null
        );
    }

    public boolean isResolved() {
        return resolved;
    }

    public ConflictResolutionStrategy getStrategyApplied() {
        return strategyApplied;
    }

    public SyncStatus getSyncStatus() {
        return syncStatus;
    }

    public Long getResolvedVersion() {
        return resolvedVersion;
    }

    public String getMessage() {
        return message;
    }

    public Object getWinningPayload() {
        return winningPayload;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        ConflictResolutionResult that = (ConflictResolutionResult) o;
        return resolved == that.resolved &&
                strategyApplied == that.strategyApplied &&
                syncStatus == that.syncStatus &&
                Objects.equals(resolvedVersion, that.resolvedVersion) &&
                Objects.equals(message, that.message) &&
                Objects.equals(winningPayload, that.winningPayload);
    }

    @Override
    public int hashCode() {
        return Objects.hash(resolved, strategyApplied, syncStatus, resolvedVersion, message, winningPayload);
    }

    @Override
    public String toString() {
        return "ConflictResolutionResult{" +
                "resolved=" + resolved +
                ", strategyApplied=" + strategyApplied +
                ", syncStatus=" + syncStatus +
                ", resolvedVersion=" + resolvedVersion +
                ", message='" + message + '\'' +
                '}';
    }
}
