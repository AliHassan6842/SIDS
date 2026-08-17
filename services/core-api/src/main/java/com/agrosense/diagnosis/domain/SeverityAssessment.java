package com.agrosense.diagnosis.domain;

import jakarta.persistence.*;
import java.time.OffsetDateTime;
import java.util.UUID;

@Entity
@Table(name = "severity_assessments")
public class SeverityAssessment {
    @Id
    private UUID id;
    private UUID diagnosisId;
    private UUID imageId;
    private UUID sampleId;
    private String severityLevel;
    private Double score;
    private OffsetDateTime createdAt;
}
