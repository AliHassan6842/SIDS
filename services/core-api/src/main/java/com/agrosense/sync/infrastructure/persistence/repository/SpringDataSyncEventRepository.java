package com.agrosense.sync.infrastructure.persistence.repository;

import com.agrosense.sync.infrastructure.persistence.entity.SyncEventJpaEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.time.OffsetDateTime;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Repository
public interface SpringDataSyncEventRepository extends JpaRepository<SyncEventJpaEntity, UUID> {

    Optional<SyncEventJpaEntity> findByClientEventId(String clientEventId);

    List<SyncEventJpaEntity> findByEntityId(UUID entityId);

    List<SyncEventJpaEntity> findByDeviceId(String deviceId);

    List<SyncEventJpaEntity> findByServerReceivedAtAfterOrderByServerReceivedAtAsc(OffsetDateTime timestamp);

    List<SyncEventJpaEntity> findByEntityTypeAndServerReceivedAtAfterOrderByServerReceivedAtAsc(String entityType, OffsetDateTime timestamp);
}
