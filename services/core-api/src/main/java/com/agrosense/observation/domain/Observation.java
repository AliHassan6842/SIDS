package com.agrosense.observation.domain;

import jakarta.persistence.*;
import java.time.OffsetDateTime;
import java.util.UUID;

@Entity
@Table(name = "observations")
public class Observation {
    @Id
    private UUID id;
    private UUID farmId;
    private UUID fieldId;
    private UUID cropCycleId;
    private UUID userId;
    private String type;
    private String status;
    private OffsetDateTime createdAt;
    private OffsetDateTime updatedAt;
}
