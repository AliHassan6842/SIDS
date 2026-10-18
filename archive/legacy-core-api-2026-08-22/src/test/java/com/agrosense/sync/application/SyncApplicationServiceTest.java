package com.agrosense.sync.application;

import com.agrosense.sync.application.command.*;
import com.agrosense.sync.application.port.EntityVersionReader;
import com.agrosense.sync.domain.model.*;
import com.agrosense.sync.domain.repository.IdempotencyRecordRepository;
import com.agrosense.sync.domain.repository.SyncEventRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.time.OffsetDateTime;
import java.util.*;

import static org.junit.jupiter.api.Assertions.*;

class SyncApplicationServiceTest {

    private SyncApplicationService syncService;
    private SyncProcessorTest.InMemorySyncEventRepository syncEventRepo;
    private SyncProcessorTest.InMemoryIdempotencyRecordRepository idempotencyRepo;

    @BeforeEach
    void setUp() {
        syncEventRepo = new SyncProcessorTest.InMemorySyncEventRepository();
        idempotencyRepo = new SyncProcessorTest.InMemoryIdempotencyRecordRepository();
        IdempotencyService idempotencyService = new IdempotencyService(idempotencyRepo);
        ConflictResolver conflictResolver = new ConflictResolver();
        EntityVersionReader versionReader = (type, id) -> Optional.empty();

        SyncProcessor processor = new SyncProcessor(idempotencyService, conflictResolver, syncEventRepo, versionReader);
        syncService = new SyncApplicationService(processor, idempotencyService, syncEventRepo);
    }

    @Test
    void shouldProcessBatchSuccessfully() {
        UUID farmId = UUID.randomUUID();
        UUID entityId1 = UUID.randomUUID();
        UUID entityId2 = UUID.randomUUID();

        List<SyncEventCommandItem> items = List.of(
                new SyncEventCommandItem("evt-1", entityId1, "observations", SyncOperation.CREATE, 0L, "{}", OffsetDateTime.now(), null),
                new SyncEventCommandItem("evt-2", entityId2, "samples", SyncOperation.CREATE, 0L, "{}", OffsetDateTime.now(), null)
        );

        ProcessSyncBatchCommand command = new ProcessSyncBatchCommand(
                "device-alpha",
                farmId,
                UUID.randomUUID(),
                ConflictResolutionStrategy.LAST_WRITE_WINS,
                items
        );

        SyncBatchResult result = syncService.processSyncBatch(command);

        assertEquals(2, result.totalEvents());
        assertEquals(2, result.appliedCount());
        assertEquals(0, result.conflictCount());
        assertEquals(0, result.failedCount());
    }

    @Test
    void shouldPullChanges() {
        UUID farmId = UUID.randomUUID();
        SyncEvent event = SyncEvent.createNew("evt-pull-1", "dev-1", UUID.randomUUID(), "observations", SyncOperation.CREATE, 1L, "{}", OffsetDateTime.now());
        syncEventRepo.save(event);

        PullSyncChangesQuery query = new PullSyncChangesQuery(
                farmId,
                OffsetDateTime.now().minusDays(1),
                List.of("observations"),
                50
        );

        PullSyncResult pullResult = syncService.pullChanges(query);

        assertEquals(farmId, pullResult.farmId());
        assertFalse(pullResult.events().isEmpty());
        assertEquals("evt-pull-1", pullResult.events().get(0).getClientEventId());
    }

    @Test
    void shouldCheckIdempotencyStatus() {
        idempotencyRepo.save(IdempotencyRecord.create("existing-key", "observations", UUID.randomUUID(), "ok"));

        assertTrue(syncService.checkIdempotency("existing-key").isPresent());
        assertFalse(syncService.checkIdempotency("non-existent-key").isPresent());
    }
}
