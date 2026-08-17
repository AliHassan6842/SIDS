package com.agrosense.sync.infrastructure.persistence.mapper;

import com.agrosense.sync.domain.model.SyncEvent;
import com.agrosense.sync.domain.model.SyncOperation;
import com.agrosense.sync.domain.model.SyncStatus;
import com.agrosense.sync.infrastructure.persistence.entity.SyncEventJpaEntity;

/**
 * Mapper for converting between domain SyncEvent and persistence SyncEventJpaEntity.
 */
public final class SyncEventMapper {

    private SyncEventMapper() {
    }

    public static SyncEventJpaEntity toJpaEntity(SyncEvent domain) {
        if (domain == null) {
            return null;
        }
        return new SyncEventJpaEntity(
                domain.getId(),
                domain.getClientEventId(),
                domain.getDeviceId(),
                domain.getEntityId(),
                domain.getEntityType(),
                domain.getBaseVersion(),
                domain.getCreatedAtDevice(),
                domain.getServerReceivedAt()
        );
    }

    public static SyncEvent toDomain(SyncEventJpaEntity entity) {
        if (entity == null) {
            return null;
        }
        return new SyncEvent(
                entity.getId(),
                entity.getClientEventId(),
                entity.getDeviceId(),
                entity.getEntityId(),
                entity.getEntityType(),
                SyncOperation.UPDATE,
                entity.getBaseVersion(),
                null,
                entity.getCreatedAtDevice(),
                entity.getServerReceivedAt(),
                SyncStatus.APPLIED,
                null
        );
    }
}
