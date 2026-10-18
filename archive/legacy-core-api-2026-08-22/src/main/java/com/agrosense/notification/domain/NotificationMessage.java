package com.agrosense.notification.domain;

import java.util.Map;
import java.util.UUID;

public record NotificationMessage(
        UUID notificationId,
        UUID recipientUserId,
        String recipientEmail,
        String deviceToken,
        String title,
        String body,
        NotificationType type,
        NotificationPriority priority,
        NotificationChannel channel,
        Map<String, String> metadata
) {
    public NotificationMessage {
        if (metadata == null) {
            metadata = Map.of();
        }
        if (priority == null) {
            priority = NotificationPriority.NORMAL;
        }
        if (channel == null) {
            channel = NotificationChannel.IN_APP;
        }
    }

    public static NotificationMessage of(
            UUID notificationId,
            UUID recipientUserId,
            String title,
            String body,
            NotificationType type,
            NotificationChannel channel
    ) {
        return new NotificationMessage(
                notificationId,
                recipientUserId,
                null,
                null,
                title,
                body,
                type,
                NotificationPriority.NORMAL,
                channel,
                Map.of()
        );
    }
}
