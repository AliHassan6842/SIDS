package com.agrosense.notification.infrastructure;

import com.agrosense.notification.domain.Notification;
import com.agrosense.notification.domain.NotificationRepository;
import com.agrosense.notification.domain.NotificationStatus;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.UUID;

@Repository
public interface JpaNotificationRepository extends JpaRepository<Notification, UUID>, NotificationRepository {

    List<Notification> findByUserIdOrderByCreatedAtDesc(UUID userId);

    List<Notification> findByUserIdAndStatusOrderByCreatedAtDesc(UUID userId, NotificationStatus status);

    @Override
    default List<Notification> findByUserId(UUID userId) {
        return findByUserIdOrderByCreatedAtDesc(userId);
    }

    @Override
    default List<Notification> findByUserIdAndStatus(UUID userId, NotificationStatus status) {
        return findByUserIdAndStatusOrderByCreatedAtDesc(userId, status);
    }

    @Override
    long countByUserIdAndStatus(UUID userId, NotificationStatus status);
}
