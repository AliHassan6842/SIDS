package com.agrosense.sync.application;

import com.agrosense.sync.application.command.SyncEventCommandItem;
import com.agrosense.sync.application.command.SyncEventProcessingResult;
import com.agrosense.sync.application.port.EntityVersionReader;
import com.agrosense.sync.domain.model.*;
import com.agrosense.sync.domain.repository.IdempotencyRecordRepository;
import com.agrosense.sync.domain.repository.SyncEventRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.time.OffsetDateTime;
import java.util.*;

import static org.junit.jupiter.api.Assertions.*;

class SyncProcessorTest {

    private InMemorySyncEventRepository syncEventRepo;
    private InMemoryIdempotencyRecordRepository idempotencyRepo;
    private SyncProcessor syncProcessor;

    @BeforeEach
    void setUp() {
        syncEventRepo = new InMemorySyncEventRepository();
        idempotencyRepo = new InMemoryIdempotencyRecordRepository();
        IdempotencyService idempotencyService = new IdempotencyService(idempotencyRepo);
        ConflictResolver conflictResolver = new ConflictResolver();
        EntityVersionReader versionReader = (type, id) -> {
            if ("existing-entity".equals(type)) {
                return Optional.of(new EntityVersionReader.EntityStateSummary(
                        id, type, 3L, OffsetDateTime.now().minusHours(1), true
                ));
            }
            return Optional.empty();
        };

        syncProcessor = new SyncProcessor(
                idempotencyService,
                conflictResolver,
                syncEventRepo,
                versionReader
        );
    }

    @Test
    void shouldProcessNewEventSuccessfully() {
        UUID entityId = UUID.randomUUID();
        SyncEventCommandItem item = new SyncEventCommandItem(
                "evt-100",
                entityId,
                "observations",
                SyncOperation.CREATE,
                0L,
                "{\"status\":\"NEW\"}",
                OffsetDateTime.now(),
                ConflictResolutionStrategy.LAST_WRITE_WINS
        );

        SyncEventProcessingResult result = syncProcessor.processEvent(item, "device-1", ConflictResolutionStrategy.LAST_WRITE_WINS);

        assertEquals(SyncStatus.APPLIED, result.status());
        assertEquals(1L, result.resolvedVersion());
        assertFalse(result.conflictDetected());
        assertTrue(idempotencyRepo.existsByClientEventId("evt-100"));
    }

    @Test
    void shouldIgnoreDuplicateEventIdempotently() {
        UUID entityId = UUID.randomUUID();
        idempotencyRepo.save(IdempotencyRecord.create("evt-duplicate", "observations", entityId, "done"));

        SyncEventCommandItem item = new SyncEventCommandItem(
                "evt-duplicate",
                entityId,
                "observations",
                SyncOperation.UPDATE,
                1L,
                "{}",
                OffsetDateTime.now(),
                ConflictResolutionStrategy.LAST_WRITE_WINS
        );

        SyncEventProcessingResult result = syncProcessor.processEvent(item, "device-1", ConflictResolutionStrategy.LAST_WRITE_WINS);

        assertEquals(SyncStatus.DUPLICATE_IGNORED, result.status());
        assertFalse(result.conflictDetected());
    }

    @Test
    void shouldResolveConflictWhenVersionsDiffer() {
        UUID entityId = UUID.randomUUID();
        SyncEventCommandItem item = new SyncEventCommandItem(
                "evt-conflict",
                entityId,
                "existing-entity",
                SyncOperation.UPDATE,
                1L, // client is behind server version 3L
                "{\"name\":\"offline updated\"}",
                OffsetDateTime.now(), // client is newer than server minusHours(1)
                ConflictResolutionStrategy.LAST_WRITE_WINS
        );

        SyncEventProcessingResult result = syncProcessor.processEvent(item, "device-1", ConflictResolutionStrategy.LAST_WRITE_WINS);

        assertEquals(SyncStatus.CONFLICT_RESOLVED_CLIENT_WINS, result.status());
        assertTrue(result.conflictDetected());
        assertEquals(4L, result.resolvedVersion());
    }

    // In-memory test doubles
    static class InMemorySyncEventRepository implements SyncEventRepository {
        private final Map<String, SyncEvent> storage = new HashMap<>();

        @Override
        public SyncEvent save(SyncEvent syncEvent) {
            storage.put(syncEvent.getClientEventId(), syncEvent);
            return syncEvent;
        }

        @Override
        public Optional<SyncEvent> findById(UUID id) {
            return storage.values().stream().filter(e -> e.getId().equals(id)).findFirst();
        }

        @Override
        public Optional<SyncEvent> findByClientEventId(String clientEventId) {
            return Optional.ofNullable(storage.get(clientEventId));
        }

        @Override
        public List<SyncEvent> findByEntityId(UUID entityId) {
            return storage.values().stream().filter(e -> e.getEntityId().equals(entityId)).toList();
        }

        @Override
        public List<SyncEvent> findByDeviceId(String deviceId) {
            return storage.values().stream().filter(e -> e.getDeviceId().equals(deviceId)).toList();
        }

        @Override
        public List<SyncEvent> findEventsSince(OffsetDateTime timestamp) {
            return new ArrayList<>(storage.values());
        }

        @Override
        public List<SyncEvent> findEventsByEntityTypeAndSince(String entityType, OffsetDateTime timestamp) {
            return storage.values().stream().filter(e -> e.getEntityType().equalsIgnoreCase(entityType)).toList();
        }
    }

    static class InMemoryIdempotencyRecordRepository implements IdempotencyRecordRepository {
        private final Map<String, IdempotencyRecord> storage = new HashMap<>();

        @Override
        public IdempotencyRecord save(IdempotencyRecord record) {
            storage.put(record.getClientEventId(), record);
            return record;
        }

        @Override
        public Optional<IdempotencyRecord> findByClientEventId(String clientEventId) {
            return Optional.ofNullable(storage.get(clientEventId));
        }

        @Override
        public boolean existsByClientEventId(String clientEventId) {
            return storage.containsKey(clientEventId);
        }
    }
}
