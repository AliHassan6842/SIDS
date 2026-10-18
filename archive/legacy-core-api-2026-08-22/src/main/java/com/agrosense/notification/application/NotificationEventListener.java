package com.agrosense.notification.application;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.context.event.EventListener;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Component;

@Component
public class NotificationEventListener {

    private static final Logger log = LoggerFactory.getLogger(NotificationEventListener.class);

    private final NotificationService notificationService;

    public NotificationEventListener(NotificationService notificationService) {
        this.notificationService = notificationService;
    }

    @EventListener
    public void onNotificationRequested(NotificationRequestedEvent event) {
        log.info("Received notification request event for user {}: {}", event.userId(), event.type());
        try {
            notificationService.sendNotification(event.toCommand());
        } catch (Exception e) {
            log.error("Error processing notification request for user {}: {}", event.userId(), e.getMessage(), e);
        }
    }
}
