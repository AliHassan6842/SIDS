package com.agrosense.sync.domain;

import com.agrosense.sync.domain.model.*;
import com.agrosense.sync.domain.policy.DefaultConflictResolutionPolicy;
import org.junit.jupiter.api.Test;

import java.time.OffsetDateTime;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.*;

class DefaultConflictResolutionPolicyTest {

    private final DefaultConflictResolutionPolicy policy = new DefaultConflictResolutionPolicy();

    @Test
    void shouldResolveClientWins() {
        SyncEvent event = SyncEvent.createNew(
                "evt-101",
                "device-1",
                UUID.randomUUID(),
                "observations",
                SyncOperation.UPDATE,
                1L,
                "{\"status\":\"COMPLETED\"}",
                OffsetDateTime.now()
        );

        ConflictResolutionResult result = policy.resolveConflict(
                event,
                2L,
                OffsetDateTime.now(),
                ConflictResolutionStrategy.CLIENT_WINS
        );

        assertTrue(result.isResolved());
        assertEquals(SyncStatus.CONFLICT_RESOLVED_CLIENT_WINS, result.getSyncStatus());
        assertEquals(3L, result.getResolvedVersion());
        assertNotNull(result.getWinningPayload());
    }

    @Test
    void shouldResolveServerWins() {
        SyncEvent event = SyncEvent.createNew(
                "evt-102",
                "device-1",
                UUID.randomUUID(),
                "observations",
                SyncOperation.UPDATE,
                1L,
                "{\"status\":\"OLD\"}",
                OffsetDateTime.now()
        );

        ConflictResolutionResult result = policy.resolveConflict(
                event,
                3L,
                OffsetDateTime.now(),
                ConflictResolutionStrategy.SERVER_WINS
        );

        assertTrue(result.isResolved());
        assertEquals(SyncStatus.CONFLICT_RESOLVED_SERVER_WINS, result.getSyncStatus());
        assertEquals(3L, result.getResolvedVersion());
        assertNull(result.getWinningPayload());
    }

    @Test
    void shouldResolveLastWriteWinsWhenClientIsNewer() {
        OffsetDateTime serverTime = OffsetDateTime.now().minusHours(2);
        OffsetDateTime deviceTime = OffsetDateTime.now().minusMinutes(5);

        SyncEvent event = SyncEvent.createNew(
                "evt-103",
                "device-1",
                UUID.randomUUID(),
                "observations",
                SyncOperation.UPDATE,
                1L,
                "{\"note\":\"Recent observation\"}",
                deviceTime
        );

        ConflictResolutionResult result = policy.resolveConflict(
                event,
                2L,
                serverTime,
                ConflictResolutionStrategy.LAST_WRITE_WINS
        );

        assertTrue(result.isResolved());
        assertEquals(SyncStatus.CONFLICT_RESOLVED_CLIENT_WINS, result.getSyncStatus());
        assertEquals(3L, result.getResolvedVersion());
    }

    @Test
    void shouldResolveLastWriteWinsWhenServerIsNewer() {
        OffsetDateTime deviceTime = OffsetDateTime.now().minusHours(5);
        OffsetDateTime serverTime = OffsetDateTime.now().minusMinutes(1);

        SyncEvent event = SyncEvent.createNew(
                "evt-104",
                "device-1",
                UUID.randomUUID(),
                "observations",
                SyncOperation.UPDATE,
                1L,
                "{\"note\":\"Outdated client edit\"}",
                deviceTime
        );

        ConflictResolutionResult result = policy.resolveConflict(
                event,
                4L,
                serverTime,
                ConflictResolutionStrategy.LAST_WRITE_WINS
        );

        assertTrue(result.isResolved());
        assertEquals(SyncStatus.CONFLICT_RESOLVED_SERVER_WINS, result.getSyncStatus());
        assertEquals(4L, result.getResolvedVersion());
    }

    @Test
    void shouldReportUnresolvedConflictWhenFailOnConflictStrategy() {
        SyncEvent event = SyncEvent.createNew(
                "evt-105",
                "device-1",
                UUID.randomUUID(),
                "tasks",
                SyncOperation.UPDATE,
                1L,
                "{}",
                OffsetDateTime.now()
        );

        ConflictResolutionResult result = policy.resolveConflict(
                event,
                3L,
                OffsetDateTime.now(),
                ConflictResolutionStrategy.FAIL_ON_CONFLICT
        );

        assertFalse(result.isResolved());
        assertEquals(SyncStatus.CONFLICT_DETECTED, result.getSyncStatus());
    }
}
