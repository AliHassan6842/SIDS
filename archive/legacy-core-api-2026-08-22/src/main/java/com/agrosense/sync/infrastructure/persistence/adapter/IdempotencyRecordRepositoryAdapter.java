package com.agrosense.sync.infrastructure.persistence.adapter;

import com.agrosense.sync.domain.model.IdempotencyRecord;
import com.agrosense.sync.domain.repository.IdempotencyRecordRepository;
import com.agrosense.sync.infrastructure.persistence.entity.IdempotencyRecordJpaEntity;
import com.agrosense.sync.infrastructure.persistence.mapper.IdempotencyRecordMapper;
import com.agrosense.sync.infrastructure.persistence.repository.SpringDataIdempotencyRecordRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

/**
 * Adapter implementing the domain IdempotencyRecordRepository port backed by Spring Data JPA.
 */
@Repository
public class IdempotencyRecordRepositoryAdapter implements IdempotencyRecordRepository {

    private final SpringDataIdempotencyRecordRepository springDataRepo;

    public IdempotencyRecordRepositoryAdapter(SpringDataIdempotencyRecordRepository springDataRepo) {
        this.springDataRepo = springDataRepo;
    }

    @Override
    public IdempotencyRecord save(IdempotencyRecord record) {
        IdempotencyRecordJpaEntity entity = IdempotencyRecordMapper.toJpaEntity(record);
        IdempotencyRecordJpaEntity saved = springDataRepo.save(entity);
        return IdempotencyRecordMapper.toDomain(saved);
    }

    @Override
    public Optional<IdempotencyRecord> findByClientEventId(String clientEventId) {
        return springDataRepo.findByClientEventId(clientEventId).map(IdempotencyRecordMapper::toDomain);
    }

    @Override
    public boolean existsByClientEventId(String clientEventId) {
        return springDataRepo.existsByClientEventId(clientEventId);
    }
}
