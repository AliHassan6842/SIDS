package com.agrosense.sync.api.dto;

import java.time.OffsetDateTime;
import java.util.UUID;

/**
 * Transport DTO reporting the idempotency registration status of a client event.
 */
public record IdempotencyStatusResponse(
        String clientEventId,
        boolean processed,
        UUID resourceId,
        String resourceType,
        OffsetDateTime processedAt
) {}
