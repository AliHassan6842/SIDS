package com.agrosense.identity.domain;

import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import java.time.Instant;
import java.util.UUID;

@Entity
@Table(name = "users")
public class User {
    @Id
    private UUID id;
    private String sub;
    private String email;
    private String name;
    private Instant createdAt;
    private Instant updatedAt;

    public User() {}

    public User(UUID id, String sub, String email, String name) {
        this.id = id;
        this.sub = sub;
        this.email = email;
        this.name = name;
        this.createdAt = Instant.now();
        this.updatedAt = this.createdAt;
    }

    // Getters and Setters omitted for brevity, but you'd normally generate them
    public UUID getId() { return id; }
    public String getSub() { return sub; }
    public String getEmail() { return email; }
    public String getName() { return name; }
    public Instant getCreatedAt() { return createdAt; }
    public Instant getUpdatedAt() { return updatedAt; }
}
