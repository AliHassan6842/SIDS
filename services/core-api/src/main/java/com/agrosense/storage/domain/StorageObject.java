package com.agrosense.storage.domain;

import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import java.time.Instant;
import java.util.UUID;

@Entity
@Table(name = "storage_objects")
public class StorageObject {
    @Id
    private UUID id;
    private String objectKey;
    private String contentType;
    private Long sizeBytes;
    private String sha256;
    private UUID ownerId;
    private String context;
    private Instant createdAt;

    public StorageObject() {}

    public StorageObject(UUID id, String objectKey, String contentType, Long sizeBytes, String sha256, UUID ownerId, String context) {
        this.id = id;
        this.objectKey = objectKey;
        this.contentType = contentType;
        this.sizeBytes = sizeBytes;
        this.sha256 = sha256;
        this.ownerId = ownerId;
        this.context = context;
        this.createdAt = Instant.now();
    }
}
