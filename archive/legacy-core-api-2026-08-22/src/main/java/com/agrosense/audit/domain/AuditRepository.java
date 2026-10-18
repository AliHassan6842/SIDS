package com.agrosense.audit.domain;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

public interface AuditRepository {

    AuditEvent save(AuditEvent event);

    List<AuditEvent> saveAll(Iterable<AuditEvent> events);

    Optional<AuditEvent> findById(UUID id);

    List<AuditEvent> findByUserId(UUID userId);

    List<AuditEvent> findByEntityTypeAndEntityId(String entityType, UUID entityId);

    List<AuditEvent> findByAction(String action);

    List<AuditEvent> findAll(int offset, int limit);
}
