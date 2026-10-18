package com.agrosense.sync.application;

import com.agrosense.sync.application.command.SyncEventCommandItem;
import com.agrosense.sync.application.command.SyncEventProcessingResult;
import com.agrosense.sync.application.port.EntityVersionReader;
import com.agrosense.sync.domain.model.*;
import com.agrosense.sync.domain.repository.SyncEventRepository;
import org.springframework.stereotype.Service;

import java.time.OffsetDateTime;
import java.util.Optional;
import java.util.UUID;

/**
 * Service responsible for processing individual synchronization events, evaluating idempotency,
 * validating optimistic locking versions, and executing conflict resolution.
 */
@Service
public class SyncProcessor {

    private final IdempotencyService idempotencyService;
    private final ConflictResolver conflictResolver;
    private final SyncEventRepository syncEventRepository;
    private final EntityVersionReader entityVersionReader;

    public SyncProcessor(
            IdempotencyService idempotencyService,
            ConflictResolver conflictResolver,
            SyncEventRepository syncEventRepository,
            EntityVersionReader entityVersionReader) {
        this.idempotencyService = idempotencyService;
        this.conflictResolver = conflictResolver;
        this.syncEventRepository = syncEventRepository;
        this.entityVersionReader = entityVersionReader;
    }

    /**
     * Processes a single sync event with idempotency guarantees and optimistic locking.
     */
    public SyncEventProcessingResult processEvent(
            SyncEventCommandItem item,
            String deviceId,
            ConflictResolutionStrategy fallbackStrategy) {

        String clientEventId = item.clientEventId();
        UUID entityId = item.entityId();
        String entityType = item.entityType();

        // 1. Idempotency Check
        if (idempotencyService.isProcessed(clientEventId)) {
            Optional<SyncEvent> existingEvent = syncEventRepository.findByClientEventId(clientEventId);
            Long existingVersion = existingEvent.map(SyncEvent::getBaseVersion).orElse(0L);
            return SyncEventProcessingResult.duplicate(clientEventId, entityId, entityType, existingVersion);
        }

        // 2. Read persistent entity state for version verification
        Optional<EntityVersionReader.EntityStateSummary> stateSummary =
                entityVersionReader.readEntityState(entityType, entityId);

        Long currentServerVersion = stateSummary.map(EntityVersionReader.EntityStateSummary::version).orElse(null);
        OffsetDateTime serverLastModifiedAt = stateSummary.map(EntityVersionReader.EntityStateSummary::lastModifiedAt).orElse(null);

        // 3. Create domain SyncEvent
        SyncEvent syncEvent = SyncEvent.createNew(
                clientEventId,
                deviceId,
                entityId,
                entityType,
                item.operation(),
                item.baseVersion(),
                item.payload(),
                item.createdAtDevice()
        );

        ConflictResolutionStrategy strategy = item.preferredStrategy() != null
                ? item.preferredStrategy()
                : fallbackStrategy;

        // 4. Optimistic locking & Conflict Handling
        boolean hasConflict = currentServerVersion != null && conflictResolver.detectConflict(item.baseVersion(), currentServerVersion);

        if (hasConflict) {
            ConflictResolutionResult resolution = conflictResolver.resolve(
                    syncEvent,
                    currentServerVersion,
                    serverLastModifiedAt,
                    strategy
            );

            if (resolution.isResolved()) {
                syncEvent.markConflict(resolution.getSyncStatus());
                SyncEvent savedEvent = syncEventRepository.save(syncEvent);
                idempotencyService.recordExecution(clientEventId, entityType, entityId, resolution.getMessage());

                return SyncEventProcessingResult.conflictResolved(
                        clientEventId,
                        entityId,
                        entityType,
                        resolution.getSyncStatus(),
                        item.baseVersion(),
                        currentServerVersion,
                        resolution.getResolvedVersion(),
                        resolution.getMessage(),
                        resolution.getWinningPayload()
                );
            } else {
                syncEvent.markConflict(SyncStatus.CONFLICT_DETECTED);
                syncEventRepository.save(syncEvent);

                return SyncEventProcessingResult.failed(
                        clientEventId,
                        entityId,
                        entityType,
                        SyncStatus.CONFLICT_DETECTED,
                        item.baseVersion(),
                        currentServerVersion,
                        resolution.getMessage()
                );
            }
        }

        // 5. No conflict: apply successfully
        Long newVersion = currentServerVersion != null ? currentServerVersion + 1L : 1L;
        syncEvent.markApplied();
        SyncEvent savedEvent = syncEventRepository.save(syncEvent);
        idempotencyService.recordExecution(clientEventId, entityType, entityId, "Applied successfully at version " + newVersion);

        return SyncEventProcessingResult.applied(
                clientEventId,
                entityId,
                entityType,
                item.baseVersion(),
                newVersion,
                item.payload()
        );
    }
}
