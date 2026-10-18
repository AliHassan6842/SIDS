package com.agrosense.audit.infrastructure;

import com.agrosense.audit.domain.AuditEvent;
import com.agrosense.audit.domain.AuditRepository;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Sort;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.UUID;

@Repository
public interface JpaAuditRepository extends JpaRepository<AuditEvent, UUID>, AuditRepository {

    List<AuditEvent> findByUserIdOrderByCreatedAtDesc(UUID userId);

    List<AuditEvent> findByEntityTypeAndEntityIdOrderByCreatedAtDesc(String entityType, UUID entityId);

    List<AuditEvent> findByActionOrderByCreatedAtDesc(String action);

    @Override
    default List<AuditEvent> findByUserId(UUID userId) {
        return findByUserIdOrderByCreatedAtDesc(userId);
    }

    @Override
    default List<AuditEvent> findByEntityTypeAndEntityId(String entityType, UUID entityId) {
        return findByEntityTypeAndEntityIdOrderByCreatedAtDesc(entityType, entityId);
    }

    @Override
    default List<AuditEvent> findByAction(String action) {
        return findByActionOrderByCreatedAtDesc(action);
    }

    @Override
    default List<AuditEvent> findAll(int offset, int limit) {
        PageRequest pageRequest = PageRequest.of(offset / Math.max(1, limit), limit, Sort.by(Sort.Direction.DESC, "createdAt"));
        return findAll(pageRequest).getContent();
    }
}
