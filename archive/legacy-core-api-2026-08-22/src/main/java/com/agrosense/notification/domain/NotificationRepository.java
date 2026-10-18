package com.agrosense.notification.domain;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

public interface NotificationRepository {

    Notification save(Notification notification);

    List<Notification> saveAll(Iterable<Notification> notifications);

    Optional<Notification> findById(UUID id);

    List<Notification> findByUserId(UUID userId);

    List<Notification> findByUserIdAndStatus(UUID userId, NotificationStatus status);

    long countByUserIdAndStatus(UUID userId, NotificationStatus status);

    void deleteById(UUID id);
}
