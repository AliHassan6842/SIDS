package com.agrosense.observation.domain;

import jakarta.persistence.*;
import java.time.OffsetDateTime;
import java.util.UUID;

@Entity
@Table(name = "images")
public class ObservationImage {
    @Id
    private UUID id;
    private UUID observationId;
    private UUID sampleId;
    private String objectKey;
    private String contentType;
    private Long sizeBytes;
    private Integer width;
    private Integer height;
    private OffsetDateTime createdAt;
}
