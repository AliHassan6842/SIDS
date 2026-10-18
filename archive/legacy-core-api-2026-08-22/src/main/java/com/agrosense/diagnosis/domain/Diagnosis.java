package com.agrosense.diagnosis.domain;

import jakarta.persistence.*;
import java.time.OffsetDateTime;
import java.util.UUID;

@Entity
@Table(name = "diagnoses")
public class Diagnosis {
    @Id
    private UUID id;
    private UUID analysisJobId;
    private UUID observationId;
    private String status;
    private OffsetDateTime createdAt;
    private OffsetDateTime updatedAt;
}
