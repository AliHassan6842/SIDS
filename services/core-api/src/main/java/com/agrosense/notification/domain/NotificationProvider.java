package com.agrosense.notification.domain;

public interface NotificationProvider {

    /**
     * Determines whether this provider supports the given notification channel.
     *
     * @param channel the delivery channel (e.g. PUSH, EMAIL, IN_APP)
     * @return true if supported, false otherwise
     */
    boolean supports(NotificationChannel channel);

    /**
     * Dispatches a notification message via this provider.
     *
     * @param message the notification message payload
     * @return delivery result with provider status and tracking ID
     */
    NotificationDeliveryResult send(NotificationMessage message);

    /**
     * Returns the distinct identifier/name of this provider (e.g. "FCM", "SENDGRID", "IN_APP").
     */
    String getProviderName();
}
