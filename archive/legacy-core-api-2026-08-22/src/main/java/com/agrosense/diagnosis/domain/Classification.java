package com.agrosense.diagnosis.domain;

import jakarta.persistence.*;
import java.time.OffsetDateTime;
import java.util.UUID;

@Entity
@Table(name = "classifications")
public class Classification {
    @Id
    private UUID id;
    private UUID diagnosisId;
    private UUID imageId;
    private String label;
    private Double confidence;
    private OffsetDateTime createdAt;
}
