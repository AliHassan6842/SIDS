package com.agrosense.notification.api;

import com.agrosense.notification.api.dto.NotificationResponse;
import com.agrosense.notification.api.dto.SendNotificationRequest;
import com.agrosense.notification.api.dto.UnreadCountResponse;
import com.agrosense.notification.application.NotificationService;
import com.agrosense.notification.domain.Notification;
import com.agrosense.notification.domain.NotificationStatus;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PatchMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.UUID;

@RestController
@RequestMapping("/v1/notifications")
public class NotificationController {

    private final NotificationService notificationService;

    public NotificationController(NotificationService notificationService) {
        this.notificationService = notificationService;
    }

    @PostMapping
    public ResponseEntity<NotificationResponse> sendNotification(
            @Valid @RequestBody SendNotificationRequest request
    ) {
        Notification notification = notificationService.sendNotification(request.toCommand());
        return ResponseEntity.status(HttpStatus.CREATED).body(NotificationResponse.fromEntity(notification));
    }

    @GetMapping
    public ResponseEntity<List<NotificationResponse>> getNotifications(
            @RequestParam UUID userId,
            @RequestParam(required = false) NotificationStatus status
    ) {
        List<NotificationResponse> responses = notificationService.getNotificationsForUser(userId, status)
                .stream()
                .map(NotificationResponse::fromEntity)
                .toList();
        return ResponseEntity.ok(responses);
    }

    @GetMapping("/{id}")
    public ResponseEntity<NotificationResponse> getNotification(
            @PathVariable UUID id,
            @RequestParam UUID userId
    ) {
        Notification notification = notificationService.getNotification(id, userId);
        return ResponseEntity.ok(NotificationResponse.fromEntity(notification));
    }

    @GetMapping("/unread-count")
    public ResponseEntity<UnreadCountResponse> getUnreadCount(@RequestParam UUID userId) {
        long count = notificationService.getUnreadCount(userId);
        return ResponseEntity.ok(new UnreadCountResponse(userId, count));
    }

    @PatchMapping("/{id}/read")
    public ResponseEntity<NotificationResponse> markAsRead(
            @PathVariable UUID id,
            @RequestParam UUID userId
    ) {
        Notification notification = notificationService.markAsRead(id, userId);
        return ResponseEntity.ok(NotificationResponse.fromEntity(notification));
    }

    @PatchMapping("/read-all")
    public ResponseEntity<Void> markAllAsRead(@RequestParam UUID userId) {
        notificationService.markAllAsRead(userId);
        return ResponseEntity.noContent().build();
    }
}
