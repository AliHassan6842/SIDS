package com.agrosense.sync.application;

import com.agrosense.sync.domain.model.ConflictResolutionResult;
import com.agrosense.sync.domain.model.ConflictResolutionStrategy;
import com.agrosense.sync.domain.model.OptimisticLockVersion;
import com.agrosense.sync.domain.model.SyncEvent;
import com.agrosense.sync.domain.policy.ConflictResolutionPolicy;
import com.agrosense.sync.domain.policy.DefaultConflictResolutionPolicy;
import org.springframework.stereotype.Service;

import java.time.OffsetDateTime;

/**
 * Application service coordinating conflict evaluation and applying domain resolution policies.
 */
@Service
public class ConflictResolver {

    private final ConflictResolutionPolicy defaultPolicy;

    public ConflictResolver() {
        this.defaultPolicy = new DefaultConflictResolutionPolicy();
    }

    public ConflictResolver(ConflictResolutionPolicy defaultPolicy) {
        this.defaultPolicy = defaultPolicy != null ? defaultPolicy : new DefaultConflictResolutionPolicy();
    }

    /**
     * Checks if a conflict exists between the client's baseVersion and the current server entity version.
     */
    public boolean detectConflict(Long clientBaseVersion, Long serverCurrentVersion) {
        OptimisticLockVersion lockVersion = new OptimisticLockVersion(clientBaseVersion, serverCurrentVersion);
        return lockVersion.hasConflict();
    }

    /**
     * Resolves a conflict using the specified strategy and domain policy.
     */
    public ConflictResolutionResult resolve(
            SyncEvent event,
            Long currentServerVersion,
            OffsetDateTime serverLastModifiedAt,
            ConflictResolutionStrategy strategy) {
        return defaultPolicy.resolveConflict(event, currentServerVersion, serverLastModifiedAt, strategy);
    }
}
