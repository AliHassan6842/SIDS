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
public class LoggingNotificationProvider implements NotificationProvider {

    private static final Logger log = LoggerFactory.getLogger(LoggingNotificationProvider.class);
    private static final String PROVIDER_NAME = "LOGGING_PROVIDER";

    @Override
    public boolean supports(NotificationChannel channel) {
        return channel == NotificationChannel.SMS;
    }

    @Override
    public NotificationDeliveryResult send(NotificationMessage message) {
        log.info("[LoggingNotificationProvider] Logged notification delivery [id={}, channel={}, type={}, user={}]: {}",
                message.notificationId(), message.channel(), message.type(), message.recipientUserId(), message.body());
        return NotificationDeliveryResult.success(PROVIDER_NAME, "log-" + UUID.randomUUID());
    }

    @Override
    public String getProviderName() {
        return PROVIDER_NAME;
    }
}
