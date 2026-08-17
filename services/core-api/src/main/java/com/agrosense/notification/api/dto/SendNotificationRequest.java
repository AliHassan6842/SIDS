package com.agrosense.notification.api.dto;

import com.agrosense.notification.application.SendNotificationCommand;
import com.agrosense.notification.domain.NotificationChannel;
import com.agrosense.notification.domain.NotificationPriority;
import com.agrosense.notification.domain.NotificationType;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

import java.util.Map;
import java.util.UUID;

public record SendNotificationRequest(
        @NotNull(message = "userId is required")
        UUID userId,

        @NotNull(message = "type is required")
        NotificationType type,

        @NotBlank(message = "message is required")
        String message,

        String title,

        NotificationChannel channel,

        NotificationPriority priority,

        String recipientEmail,

        String deviceToken,

        Map<String, String> metadata
) {
    public SendNotificationCommand toCommand() {
        return new SendNotificationCommand(
                userId,
                type,
                title != null ? title : type.name(),
                message,
                channel != null ? channel : NotificationChannel.IN_APP,
                priority != null ? priority : NotificationPriority.NORMAL,
                recipientEmail,
                deviceToken,
                metadata != null ? metadata : Map.of()
        );
    }
}
