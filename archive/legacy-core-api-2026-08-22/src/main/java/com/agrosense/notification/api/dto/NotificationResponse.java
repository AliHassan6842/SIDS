package com.agrosense.notification.api.dto;

import com.agrosense.notification.domain.Notification;
import com.agrosense.notification.domain.NotificationStatus;
import com.agrosense.notification.domain.NotificationType;

import java.time.Instant;
import java.util.UUID;

public record NotificationResponse(
        UUID id,
        NotificationType type,
        UUID userId,
        NotificationStatus status,
        String message,
        Instant readAt,
        Instant createdAt,
        Instant updatedAt
) {
    public static NotificationResponse fromEntity(Notification notification) {
        return new NotificationResponse(
                notification.getId(),
                notification.getType(),
                notification.getUserId(),
                notification.getStatus(),
                notification.getMessage(),
                notification.getReadAt(),
                notification.getCreatedAt(),
                notification.getUpdatedAt()
        );
    }
}
