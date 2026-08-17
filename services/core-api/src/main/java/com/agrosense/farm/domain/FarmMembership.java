package com.agrosense.farm.domain;

import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import java.time.Instant;
import java.util.UUID;

@Entity
@Table(name = "farm_memberships")
public class FarmMembership {
    @Id
    private UUID id;
    private UUID farmId;
    private UUID userId;
    private String role;
    private Instant createdAt;
    private Instant updatedAt;

    public FarmMembership() {}

    public FarmMembership(UUID id, UUID farmId, UUID userId, String role) {
        this.id = id;
        this.farmId = farmId;
        this.userId = userId;
        this.role = role;
        this.createdAt = Instant.now();
        this.updatedAt = this.createdAt;
    }
}
