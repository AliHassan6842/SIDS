package com.agrosense.notification.application;

import com.agrosense.notification.domain.Notification;
import com.agrosense.notification.domain.NotificationChannel;
import com.agrosense.notification.domain.NotificationDeliveryResult;
import com.agrosense.notification.domain.NotificationMessage;
import com.agrosense.notification.domain.NotificationProvider;
import com.agrosense.notification.domain.NotificationRepository;
import com.agrosense.notification.domain.NotificationStatus;
import com.agrosense.shared.error.exceptions.AuthorizationException;
import com.agrosense.shared.error.exceptions.ResourceNotFoundException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Objects;
import java.util.UUID;

@Service
@Transactional
public class NotificationService {

    private static final Logger log = LoggerFactory.getLogger(NotificationService.class);

    private final NotificationRepository notificationRepository;
    private final List<NotificationProvider> notificationProviders;

    public NotificationService(
            NotificationRepository notificationRepository,
            List<NotificationProvider> notificationProviders
    ) {
        this.notificationRepository = notificationRepository;
        this.notificationProviders = notificationProviders != null ? notificationProviders : List.of();
    }

    /**
     * Creates and persists a notification record, then asynchronously or synchronously
     * dispatches it to eligible NotificationProviders based on channel.
     */
    public Notification sendNotification(SendNotificationCommand command) {
        Objects.requireNonNull(command, "SendNotificationCommand cannot be null");
        Objects.requireNonNull(command.userId(), "User ID cannot be null");
        Objects.requireNonNull(command.type(), "Notification Type cannot be null");
        Objects.requireNonNull(command.message(), "Message cannot be null");

        // 1. Create domain entity and persist
        Notification notification = Notification.create(
                command.userId(),
                command.type(),
                command.message()
        );
        Notification saved = notificationRepository.save(notification);

        // 2. Dispatch decoupled payload to providers
        NotificationMessage message = new NotificationMessage(
                saved.getId(),
                command.userId(),
                command.recipientEmail(),
                command.deviceToken(),
                command.title() != null ? command.title() : command.type().name(),
                command.message(),
                command.type(),
                command.priority(),
                command.channel(),
                command.metadata()
        );

        dispatchToProviders(message);

        return saved;
    }

    /**
     * Dispatches notification message to registered providers supporting the requested channel.
     */
    private void dispatchToProviders(NotificationMessage message) {
        for (NotificationProvider provider : notificationProviders) {
            try {
                if (message.channel() == NotificationChannel.ALL || provider.supports(message.channel())) {
                    NotificationDeliveryResult result = provider.send(message);
                    log.debug("Dispatched notification {} via {}: success={}",
                            message.notificationId(), provider.getProviderName(), result.success());
                }
            } catch (Exception ex) {
                log.error("Failed to deliver notification {} via provider {}: {}",
                        message.notificationId(), provider.getProviderName(), ex.getMessage(), ex);
            }
        }
    }

    /**
     * Marks a specific notification as READ.
     */
    public Notification markAsRead(UUID notificationId, UUID userId) {
        Notification notification = notificationRepository.findById(notificationId)
                .orElseThrow(() -> new ResourceNotFoundException("Notification not found", "Notification", notificationId.toString()));

        if (!notification.getUserId().equals(userId)) {
            throw new AuthorizationException("User is not authorized to update this notification");
        }

        notification.markAsRead();
        return notificationRepository.save(notification);
    }

    /**
     * Marks all unread notifications for a user as READ.
     */
    public void markAllAsRead(UUID userId) {
        List<Notification> unreadNotifications = notificationRepository.findByUserIdAndStatus(userId, NotificationStatus.UNREAD);
        for (Notification notification : unreadNotifications) {
            notification.markAsRead();
        }
        notificationRepository.saveAll(unreadNotifications);
    }

    @Transactional(readOnly = true)
    public List<Notification> getNotificationsForUser(UUID userId, NotificationStatus status) {
        if (status != null) {
            return notificationRepository.findByUserIdAndStatus(userId, status);
        }
        return notificationRepository.findByUserId(userId);
    }

    @Transactional(readOnly = true)
    public Notification getNotification(UUID notificationId, UUID userId) {
        Notification notification = notificationRepository.findById(notificationId)
                .orElseThrow(() -> new ResourceNotFoundException("Notification not found", "Notification", notificationId.toString()));

        if (!notification.getUserId().equals(userId)) {
            throw new AuthorizationException("User is not authorized to view this notification");
        }
        return notification;
    }

    @Transactional(readOnly = true)
    public long getUnreadCount(UUID userId) {
        return notificationRepository.countByUserIdAndStatus(userId, NotificationStatus.UNREAD);
    }
}
