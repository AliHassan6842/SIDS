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
public class PushNotificationProvider implements NotificationProvider {

    private static final Logger log = LoggerFactory.getLogger(PushNotificationProvider.class);
    private static final String PROVIDER_NAME = "FCM_PUSH";

    @Override
    public boolean supports(NotificationChannel channel) {
        return channel == NotificationChannel.PUSH;
    }

    @Override
    public NotificationDeliveryResult send(NotificationMessage message) {
        log.info("[PushNotificationProvider] Dispatching push notification to device token [{}] / user [{}]: {}",
                message.deviceToken(), message.recipientUserId(), message.title());

        // In production, integrate with Firebase Cloud Messaging / APNs client here
        String messageId = "fcm-" + UUID.randomUUID();
        return NotificationDeliveryResult.success(PROVIDER_NAME, messageId);
    }

    @Override
    public String getProviderName() {
        return PROVIDER_NAME;
    }
}
