package com.agrosense.notification.infrastructure.providers;

import com.agrosense.notification.domain.NotificationChannel;
import com.agrosense.notification.domain.NotificationDeliveryResult;
import com.agrosense.notification.domain.NotificationMessage;
import com.agrosense.notification.domain.NotificationProvider;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;

import java.util.UUID;

@Component
public class InAppNotificationProvider implements NotificationProvider {

    private static final Logger log = LoggerFactory.getLogger(InAppNotificationProvider.class);
    private static final String PROVIDER_NAME = "IN_APP";

    @Override
    public boolean supports(NotificationChannel channel) {
        return channel == NotificationChannel.IN_APP;
    }

    @Override
    public NotificationDeliveryResult send(NotificationMessage message) {
        log.info("[InAppNotificationProvider] Delivering in-app notification [{}] to user {}: {}",
                message.notificationId(), message.recipientUserId(), message.title());
        // In-app notifications are persisted in DB and queried via REST API / WebSocket
        String internalId = "inapp-" + (message.notificationId() != null ? message.notificationId() : UUID.randomUUID());
        return NotificationDeliveryResult.success(PROVIDER_NAME, internalId);
    }

    @Override
    public String getProviderName() {
        return PROVIDER_NAME;
    }
}
