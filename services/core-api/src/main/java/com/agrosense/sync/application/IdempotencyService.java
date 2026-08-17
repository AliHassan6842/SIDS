package com.agrosense.sync.application;

import com.agrosense.sync.domain.model.IdempotencyRecord;
import com.agrosense.sync.domain.repository.IdempotencyRecordRepository;
import org.springframework.stereotype.Service;

import java.util.Optional;
import java.util.UUID;

/**
 * Application service for checking and registering idempotent event executions.
 */
@Service
public class IdempotencyService {

    private final IdempotencyRecordRepository idempotencyRecordRepository;

    public IdempotencyService(IdempotencyRecordRepository idempotencyRecordRepository) {
        this.idempotencyRecordRepository = idempotencyRecordRepository;
    }

    /**
     * Checks if a clientEventId has already been recorded.
     */
    public boolean isProcessed(String clientEventId) {
        if (clientEventId == null || clientEventId.isBlank()) {
            return false;
        }
        return idempotencyRecordRepository.existsByClientEventId(clientEventId);
    }

    /**
     * Retrieves an existing idempotency record if present.
     */
    public Optional<IdempotencyRecord> findRecord(String clientEventId) {
        if (clientEventId == null || clientEventId.isBlank()) {
            return Optional.empty();
        }
        return idempotencyRecordRepository.findByClientEventId(clientEventId);
    }

    /**
     * Records the execution of an event to guarantee future requests with the same clientEventId are treated idempotently.
     */
    public IdempotencyRecord recordExecution(String clientEventId, String resourceType, UUID resourceId, String summary) {
        IdempotencyRecord record = IdempotencyRecord.create(
                clientEventId,
                resourceType != null ? resourceType : "UNKNOWN",
                resourceId != null ? resourceId : UUID.randomUUID(),
                summary
        );
        return idempotencyRecordRepository.save(record);
    }
}
