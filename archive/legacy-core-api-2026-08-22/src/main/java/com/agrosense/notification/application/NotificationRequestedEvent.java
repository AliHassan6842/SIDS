package com.agrosense.notification.application;

import com.agrosense.notification.domain.NotificationChannel;
import com.agrosense.notification.domain.NotificationPriority;
import com.agrosense.notification.domain.NotificationType;

import java.util.Map;
import java.util.UUID;

public record NotificationRequestedEvent(
        UUID userId,
        NotificationType type,
        String title,
        String message,
        NotificationChannel channel,
        NotificationPriority priority,
        Map<String, String> metadata
) {
    public NotificationRequestedEvent {
        if (channel == null) {
            channel = NotificationChannel.IN_APP;
        }
        if (priority == null) {
            priority = NotificationPriority.NORMAL;
        }
        if (metadata == null) {
            metadata = Map.of();
        }
    }

    public static NotificationRequestedEvent of(UUID userId, NotificationType type, String title, String message) {
        return new NotificationRequestedEvent(userId, type, title, message, NotificationChannel.IN_APP, NotificationPriority.NORMAL, Map.of());
    }

    public SendNotificationCommand toCommand() {
        return new SendNotificationCommand(
                userId,
                type,
                title,
                message,
                channel,
                priority,
                null,
                null,
                metadata
        );
    }
}
