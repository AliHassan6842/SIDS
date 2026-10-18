package com.agrosense.identity.domain;

import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import java.time.Instant;
import java.util.UUID;

@Entity
@Table(name = "devices")
public class Device {
    @Id
    private UUID id;
    private UUID userId;
    private String deviceName;
    private String fcmToken;
    private Instant createdAt;
    private Instant updatedAt;

    public Device() {}

    public Device(UUID id, UUID userId, String deviceName, String fcmToken) {
        this.id = id;
        this.userId = userId;
        this.deviceName = deviceName;
        this.fcmToken = fcmToken;
        this.createdAt = Instant.now();
        this.updatedAt = this.createdAt;
    }
}
