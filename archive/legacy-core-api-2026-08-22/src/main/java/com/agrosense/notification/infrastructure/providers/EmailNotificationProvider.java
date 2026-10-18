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
public class EmailNotificationProvider implements NotificationProvider {

    private static final Logger log = LoggerFactory.getLogger(EmailNotificationProvider.class);
    private static final String PROVIDER_NAME = "EMAIL_SMTP";

    @Override
    public boolean supports(NotificationChannel channel) {
        return channel == NotificationChannel.EMAIL;
    }

    @Override
    public NotificationDeliveryResult send(NotificationMessage message) {
        log.info("[EmailNotificationProvider] Sending email to [{}] with subject [{}]: {}",
                message.recipientEmail(), message.title(), message.body());

        // In production, integrate with JavaMailSender / SES / SendGrid here
        String messageId = "mail-" + UUID.randomUUID();
        return NotificationDeliveryResult.success(PROVIDER_NAME, messageId);
    }

    @Override
    public String getProviderName() {
        return PROVIDER_NAME;
    }
}
