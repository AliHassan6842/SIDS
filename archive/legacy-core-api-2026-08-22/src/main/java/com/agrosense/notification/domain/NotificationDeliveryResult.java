package com.agrosense.notification.domain;

public record NotificationDeliveryResult(
        boolean success,
        String providerName,
        String externalMessageId,
        String errorMessage
) {
    public static NotificationDeliveryResult success(String providerName, String externalMessageId) {
        return new NotificationDeliveryResult(true, providerName, externalMessageId, null);
    }

    public static NotificationDeliveryResult failure(String providerName, String errorMessage) {
        return new NotificationDeliveryResult(false, providerName, null, errorMessage);
    }
}
