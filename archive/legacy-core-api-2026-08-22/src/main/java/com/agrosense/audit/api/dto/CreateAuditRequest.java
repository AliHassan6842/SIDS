package com.agrosense.audit.api.dto;

import com.agrosense.audit.application.RecordAuditCommand;
import jakarta.validation.constraints.NotBlank;

import java.util.UUID;

public record CreateAuditRequest(
        @NotBlank(message = "action is required")
        String action,

        UUID userId,

        String entityType,

        UUID entityId,

        String details
) {
    public RecordAuditCommand toCommand() {
        return new RecordAuditCommand(action, userId, entityType, entityId, details);
    }
}
