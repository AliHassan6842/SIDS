package com.agrosense.diagnosis.domain;

import jakarta.persistence.*;
import java.time.OffsetDateTime;
import java.util.UUID;

@Entity
@Table(name = "detections")
public class Detection {
    @Id
    private UUID id;
    private UUID diagnosisId;
    private UUID imageId;
    private Double bboxX;
    private Double bboxY;
    private Double bboxW;
    private Double bboxH;
    private Double confidence;
    private String label;
    private OffsetDateTime createdAt;
}
