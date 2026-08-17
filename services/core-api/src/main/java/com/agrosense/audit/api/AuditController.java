package com.agrosense.audit.api;

import com.agrosense.audit.api.dto.AuditEventResponse;
import com.agrosense.audit.api.dto.CreateAuditRequest;
import com.agrosense.audit.application.AuditQuery;
import com.agrosense.audit.application.AuditService;
import com.agrosense.audit.domain.AuditEvent;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.UUID;

@RestController
@RequestMapping("/v1/audit-events")
public class AuditController {

    private final AuditService auditService;

    public AuditController(AuditService auditService) {
        this.auditService = auditService;
    }

    @PostMapping
    public ResponseEntity<AuditEventResponse> recordAuditEvent(
            @Valid @RequestBody CreateAuditRequest request
    ) {
        AuditEvent event = auditService.recordEvent(request.toCommand());
        return ResponseEntity.status(HttpStatus.CREATED).body(AuditEventResponse.fromEntity(event));
    }

    @GetMapping
    public ResponseEntity<List<AuditEventResponse>> queryAuditEvents(
            @RequestParam(required = false) UUID userId,
            @RequestParam(required = false) String entityType,
            @RequestParam(required = false) UUID entityId,
            @RequestParam(required = false) String action,
            @RequestParam(defaultValue = "50") int limit
    ) {
        AuditQuery query = new AuditQuery(userId, entityType, entityId, action, limit);
        List<AuditEventResponse> responses = auditService.queryEvents(query)
                .stream()
                .map(AuditEventResponse::fromEntity)
                .toList();
        return ResponseEntity.ok(responses);
    }

    @GetMapping("/{id}")
    public ResponseEntity<AuditEventResponse> getAuditEvent(@PathVariable UUID id) {
        AuditEvent event = auditService.getEventById(id);
        return ResponseEntity.ok(AuditEventResponse.fromEntity(event));
    }

    @GetMapping("/entities/{entityType}/{entityId}")
    public ResponseEntity<List<AuditEventResponse>> getEntityAuditHistory(
            @PathVariable String entityType,
            @PathVariable UUID entityId
    ) {
        List<AuditEventResponse> responses = auditService.getEventsForEntity(entityType, entityId)
                .stream()
                .map(AuditEventResponse::fromEntity)
                .toList();
        return ResponseEntity.ok(responses);
    }
}
