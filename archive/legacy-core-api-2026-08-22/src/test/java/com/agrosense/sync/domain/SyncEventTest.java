package com.agrosense.sync.domain;

import com.agrosense.sync.domain.model.SyncEvent;
import com.agrosense.sync.domain.model.SyncOperation;
import com.agrosense.sync.domain.model.SyncStatus;
import org.junit.jupiter.api.Test;

import java.time.OffsetDateTime;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.*;

class SyncEventTest {

    @Test
    void shouldCreateAndMutateSyncEventState() {
        UUID entityId = UUID.randomUUID();
        SyncEvent event = SyncEvent.createNew(
                "client-evt-001",
                "device-alpha",
                entityId,
                "observations",
                SyncOperation.CREATE,
                0L,
                "{\"type\":\"DIAGNOSIS\"}",
                OffsetDateTime.now()
        );

        assertNotNull(event.getId());
        assertEquals("client-evt-001", event.getClientEventId());
        assertEquals("device-alpha", event.getDeviceId());
        assertEquals(entityId, event.getEntityId());
        assertEquals(SyncStatus.APPLIED, event.getStatus());

        event.markDuplicate();
        assertEquals(SyncStatus.DUPLICATE_IGNORED, event.getStatus());

        event.markConflict(SyncStatus.CONFLICT_RESOLVED_CLIENT_WINS);
        assertEquals(SyncStatus.CONFLICT_RESOLVED_CLIENT_WINS, event.getStatus());

        event.markFailed("Network timeout during propagation");
        assertEquals(SyncStatus.FAILED, event.getStatus());
        assertEquals("Network timeout during propagation", event.getFailureReason());
    }
}
