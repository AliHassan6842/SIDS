package com.agrosense.sync.infrastructure.persistence.mapper;

import com.agrosense.sync.domain.model.IdempotencyRecord;
import com.agrosense.sync.infrastructure.persistence.entity.IdempotencyRecordJpaEntity;

/**
 * Mapper for converting between domain IdempotencyRecord and persistence IdempotencyRecordJpaEntity.
 */
public final class IdempotencyRecordMapper {

    private IdempotencyRecordMapper() {
    }

    public static IdempotencyRecordJpaEntity toJpaEntity(IdempotencyRecord domain) {
        if (domain == null) {
            return null;
        }
        return new IdempotencyRecordJpaEntity(
                domain.getId(),
                domain.getClientEventId(),
                domain.getResourceType(),
                domain.getResourceId(),
                domain.getCreatedAt()
        );
    }

    public static IdempotencyRecord toDomain(IdempotencyRecordJpaEntity entity) {
        if (entity == null) {
            return null;
        }
        return new IdempotencyRecord(
                entity.getId(),
                entity.getClientEventId(),
                entity.getResourceType(),
                entity.getResourceId(),
                entity.getCreatedAt(),
                null
        );
    }
}
