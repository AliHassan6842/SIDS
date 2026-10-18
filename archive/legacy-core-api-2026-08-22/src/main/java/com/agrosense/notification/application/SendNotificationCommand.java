package com.agrosense.notification.application;

import com.agrosense.notification.domain.NotificationChannel;
import com.agrosense.notification.domain.NotificationPriority;
import com.agrosense.notification.domain.NotificationType;

import java.util.Map;
import java.util.UUID;

public record SendNotificationCommand(
        UUID userId,
        NotificationType type,
        String title,
        String message,
        NotificationChannel channel,
        NotificationPriority priority,
        String recipientEmail,
        String deviceToken,
        Map<String, String> metadata
) {
    public SendNotificationCommand {
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

    public static SendNotificationCommand simple(UUID userId, NotificationType type, String message) {
        return new SendNotificationCommand(
                userId,
                type,
                type.name(),
                message,
                NotificationChannel.IN_APP,
                NotificationPriority.NORMAL,
                null,
                null,
                Map.of()
        );
    }
}
