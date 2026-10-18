package com.agrosense.observation.domain;

import jakarta.persistence.*;
import java.time.OffsetDateTime;
import java.util.UUID;

@Entity
@Table(name = "samples")
public class Sample {
    @Id
    private UUID id;
    private UUID observationId;
    private Double locationLat;
    private Double locationLng;
    private OffsetDateTime createdAt;
    private OffsetDateTime updatedAt;
}
