package com.agrosense.sync.infrastructure.persistence.repository;

import com.agrosense.sync.infrastructure.persistence.entity.IdempotencyRecordJpaEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;
import java.util.UUID;

@Repository
public interface SpringDataIdempotencyRecordRepository extends JpaRepository<IdempotencyRecordJpaEntity, UUID> {

    Optional<IdempotencyRecordJpaEntity> findByClientEventId(String clientEventId);

    boolean existsByClientEventId(String clientEventId);
}
