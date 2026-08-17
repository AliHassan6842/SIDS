package com.agrosense.task.infrastructure;

import com.agrosense.task.domain.IdempotencyRecord;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;
import java.util.UUID;

/**
 * Spring Data JPA Repository interface for Idempotency tracking.
 */
@Repository
public interface IdempotencyRecordJpaRepository extends JpaRepository<IdempotencyRecord, UUID> {

    Optional<IdempotencyRecord> findByClientEventId(String clientEventId);

    Optional<IdempotencyRecord> findByClientEventIdAndResourceType(String clientEventId, String resourceType);

    boolean existsByClientEventId(String clientEventId);

    boolean existsByClientEventIdAndResourceType(String clientEventId, String resourceType);
}
