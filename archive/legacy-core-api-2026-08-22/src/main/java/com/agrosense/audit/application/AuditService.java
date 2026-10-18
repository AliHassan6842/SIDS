package com.agrosense.audit.application;

import com.agrosense.audit.domain.AuditEvent;
import com.agrosense.audit.domain.AuditRepository;
import com.agrosense.shared.error.exceptions.ResourceNotFoundException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Objects;
import java.util.Optional;
import java.util.UUID;

@Service
@Transactional
public class AuditService {

    private static final Logger log = LoggerFactory.getLogger(AuditService.class);

    private final AuditRepository auditRepository;

    public AuditService(AuditRepository auditRepository) {
        this.auditRepository = auditRepository;
    }

    /**
     * Records a new audit event for an action.
     */
    public AuditEvent recordEvent(RecordAuditCommand command) {
        Objects.requireNonNull(command, "RecordAuditCommand cannot be null");
        Objects.requireNonNull(command.action(), "Action cannot be null");

        AuditEvent event = AuditEvent.create(
                command.action(),
                command.userId(),
                command.entityType(),
                command.entityId(),
                command.details()
        );

        AuditEvent saved = auditRepository.save(event);
        log.info("Recorded audit event: action={}, entityType={}, entityId={}, userId={}",
                saved.getAction(), saved.getEntityType(), saved.getEntityId(), saved.getUserId());
        return saved;
    }

    /**
     * Convenience method to record an event directly.
     */
    public AuditEvent recordEvent(String action, UUID userId, String entityType, UUID entityId, String details) {
        return recordEvent(new RecordAuditCommand(action, userId, entityType, entityId, details));
    }

    @Transactional(readOnly = true)
    public AuditEvent getEventById(UUID id) {
        return auditRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Audit event not found", "AuditEvent", id.toString()));
    }

    @Transactional(readOnly = true)
    public List<AuditEvent> getEventsForUser(UUID userId) {
        return auditRepository.findByUserId(userId);
    }

    @Transactional(readOnly = true)
    public List<AuditEvent> getEventsForEntity(String entityType, UUID entityId) {
        return auditRepository.findByEntityTypeAndEntityId(entityType, entityId);
    }

    @Transactional(readOnly = true)
    public List<AuditEvent> getEventsForAction(String action) {
        return auditRepository.findByAction(action);
    }

    @Transactional(readOnly = true)
    public List<AuditEvent> queryEvents(AuditQuery query) {
        if (query.entityType() != null && query.entityId() != null) {
            return auditRepository.findByEntityTypeAndEntityId(query.entityType(), query.entityId());
        }
        if (query.userId() != null) {
            return auditRepository.findByUserId(query.userId());
        }
        if (query.action() != null) {
            return auditRepository.findByAction(query.action());
        }
        return auditRepository.findAll(0, query.limit());
    }
}
