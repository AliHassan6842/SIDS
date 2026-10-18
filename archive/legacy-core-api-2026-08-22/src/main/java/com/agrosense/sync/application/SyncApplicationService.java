package com.agrosense.sync.application;

import com.agrosense.sync.application.command.*;
import com.agrosense.sync.domain.model.IdempotencyRecord;
import com.agrosense.sync.domain.model.SyncEvent;
import com.agrosense.sync.domain.repository.SyncEventRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.OffsetDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

/**
 * Main application service orchestrating offline synchronization push/pull batches and idempotency lookups.
 */
@Service
public class SyncApplicationService {

    private final SyncProcessor syncProcessor;
    private final IdempotencyService idempotencyService;
    private final SyncEventRepository syncEventRepository;

    public SyncApplicationService(
            SyncProcessor syncProcessor,
            IdempotencyService idempotencyService,
            SyncEventRepository syncEventRepository) {
        this.syncProcessor = syncProcessor;
        this.idempotencyService = idempotencyService;
        this.syncEventRepository = syncEventRepository;
    }

    /**
     * Processes an incoming batch of offline synchronization events.
     */
    @Transactional
    public SyncBatchResult processSyncBatch(ProcessSyncBatchCommand command) {
        List<SyncEventProcessingResult> results = new ArrayList<>();

        for (SyncEventCommandItem item : command.events()) {
            SyncEventProcessingResult result = syncProcessor.processEvent(
                    item,
                    command.deviceId(),
                    command.defaultStrategy()
            );
            results.add(result);
        }

        return SyncBatchResult.fromResults(results);
    }

    /**
     * Pulls synchronization changes from the server recorded since a given timestamp.
     */
    @Transactional(readOnly = true)
    public PullSyncResult pullChanges(PullSyncChangesQuery query) {
        OffsetDateTime since = query.sinceTimestamp() != null
                ? query.sinceTimestamp()
                : OffsetDateTime.now().minusDays(30);

        List<SyncEvent> events;
        if (query.entityTypes() != null && !query.entityTypes().isEmpty()) {
            events = new ArrayList<>();
            for (String type : query.entityTypes()) {
                events.addAll(syncEventRepository.findEventsByEntityTypeAndSince(type, since));
            }
        } else {
            events = syncEventRepository.findEventsSince(since);
        }

        int limit = query.limit();
        boolean hasMore = events.size() > limit;
        List<SyncEvent> limitedEvents = hasMore ? events.subList(0, limit) : events;

        return new PullSyncResult(
                query.farmId(),
                OffsetDateTime.now(),
                limitedEvents,
                hasMore
        );
    }

    /**
     * Retrieves idempotency status for a specific clientEventId.
     */
    @Transactional(readOnly = true)
    public Optional<IdempotencyRecord> checkIdempotency(String clientEventId) {
        return idempotencyService.findRecord(clientEventId);
    }
}
