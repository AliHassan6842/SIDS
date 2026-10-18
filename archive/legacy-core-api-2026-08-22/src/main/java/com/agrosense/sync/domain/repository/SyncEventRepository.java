package com.agrosense.sync.domain.repository;

import com.agrosense.sync.domain.model.SyncEvent;

import java.time.OffsetDateTime;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

/**
 * Domain port/repository for persisting and retrieving sync events.
 */
public interface SyncEventRepository {

    SyncEvent save(SyncEvent syncEvent);

    Optional<SyncEvent> findById(UUID id);

    Optional<SyncEvent> findByClientEventId(String clientEventId);

    List<SyncEvent> findByEntityId(UUID entityId);

    List<SyncEvent> findByDeviceId(String deviceId);

    List<SyncEvent> findEventsSince(OffsetDateTime timestamp);

    List<SyncEvent> findEventsByEntityTypeAndSince(String entityType, OffsetDateTime timestamp);
}
