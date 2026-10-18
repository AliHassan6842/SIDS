package com.agrosense.audit.application;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.context.event.EventListener;
import org.springframework.stereotype.Component;

@Component
public class AuditEventListener {

    private static final Logger log = LoggerFactory.getLogger(AuditEventListener.class);

    private final AuditService auditService;

    public AuditEventListener(AuditService auditService) {
        this.auditService = auditService;
    }

    @EventListener
    public void onAuditRequested(AuditRecordRequestedEvent event) {
        log.debug("Received audit record request event: action={}, user={}", event.action(), event.userId());
        try {
            auditService.recordEvent(event.toCommand());
        } catch (Exception e) {
            log.error("Failed to record audit event for action {}: {}", event.action(), e.getMessage(), e);
        }
    }
}
