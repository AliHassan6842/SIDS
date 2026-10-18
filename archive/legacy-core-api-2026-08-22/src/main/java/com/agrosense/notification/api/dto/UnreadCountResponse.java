package com.agrosense.notification.api.dto;

import java.util.UUID;

public record UnreadCountResponse(
        UUID userId,
        long unreadCount
) {
}
