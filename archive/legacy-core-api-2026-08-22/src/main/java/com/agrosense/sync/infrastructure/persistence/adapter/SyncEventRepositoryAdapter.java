package com.agrosense.sync.infrastructure.persistence.adapter;

import com.agrosense.sync.domain.model.SyncEvent;
import com.agrosense.sync.domain.repository.SyncEventRepository;
import com.agrosense.sync.infrastructure.persistence.entity.SyncEventJpaEntity;
import com.agrosense.sync.infrastructure.persistence.mapper.SyncEventMapper;
import com.agrosense.sync.infrastructure.persistence.repository.SpringDataSyncEventRepository;
import org.springframework.stereotype.Repository;

import java.time.OffsetDateTime;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.stream.Collectors;

/**
 * Adapter implementing the domain SyncEventRepository port backed by Spring Data JPA.
 */
@Repository
public class SyncEventRepositoryAdapter implements SyncEventRepository {

    private final SpringDataSyncEventRepository springDataRepo;

    public SyncEventRepositoryAdapter(SpringDataSyncEventRepository springDataRepo) {
        this.springDataRepo = springDataRepo;
    }

    @Override
    public SyncEvent save(SyncEvent syncEvent) {
        SyncEventJpaEntity entity = SyncEventMapper.toJpaEntity(syncEvent);
        SyncEventJpaEntity saved = springDataRepo.save(entity);
        return SyncEventMapper.toDomain(saved);
    }

    @Override
    public Optional<SyncEvent> findById(UUID id) {
        return springDataRepo.findById(id).map(SyncEventMapper::toDomain);
    }

    @Override
    public Optional<SyncEvent> findByClientEventId(String clientEventId) {
        return springDataRepo.findByClientEventId(clientEventId).map(SyncEventMapper::toDomain);
    }

    @Override
    public List<SyncEvent> findByEntityId(UUID entityId) {
        return springDataRepo.findByEntityId(entityId).stream()
                .map(SyncEventMapper::toDomain)
                .collect(Collectors.toList());
    }

    @Override
    public List<SyncEvent> findByDeviceId(String deviceId) {
        return springDataRepo.findByDeviceId(deviceId).stream()
                .map(SyncEventMapper::toDomain)
                .collect(Collectors.toList());
    }

    @Override
    public List<SyncEvent> findEventsSince(OffsetDateTime timestamp) {
        return springDataRepo.findByServerReceivedAtAfterOrderByServerReceivedAtAsc(timestamp).stream()
                .map(SyncEventMapper::toDomain)
                .collect(Collectors.toList());
    }

    @Override
    public List<SyncEvent> findEventsByEntityTypeAndSince(String entityType, OffsetDateTime timestamp) {
        return springDataRepo.findByEntityTypeAndServerReceivedAtAfterOrderByServerReceivedAtAsc(entityType, timestamp).stream()
                .map(SyncEventMapper::toDomain)
                .collect(Collectors.toList());
    }
}
