package com.agrosense.sync.domain.repository;

import com.agrosense.sync.domain.model.IdempotencyRecord;

import java.util.Optional;

/**
 * Domain port/repository for checking and recording event idempotency.
 */
public interface IdempotencyRecordRepository {

    IdempotencyRecord save(IdempotencyRecord record);

    Optional<IdempotencyRecord> findByClientEventId(String clientEventId);

    boolean existsByClientEventId(String clientEventId);
}
