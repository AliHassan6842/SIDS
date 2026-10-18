package com.agrosense.sync.api.dto;

import java.time.OffsetDateTime;
import java.util.UUID;

/**
 * Transport DTO representing a synchronizable entity event pulled from the server.
 */
public record PullEntityItemDto(
        UUID id,
        String clientEventId,
        String deviceId,
        UUID entityId,
        String entityType,
        Long baseVersion,
        OffsetDateTime createdAtDevice,
        OffsetDateTime serverReceivedAt
) {}
