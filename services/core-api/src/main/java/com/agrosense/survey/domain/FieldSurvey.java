package com.agrosense.survey.domain;

import jakarta.persistence.*;
import java.time.OffsetDateTime;
import java.util.UUID;

@Entity
@Table(name = "field_surveys")
public class FieldSurvey {
    @Id
    private UUID id;
    private UUID farmId;
    private UUID fieldId;
    private UUID protocolId;
    private UUID observationId;
    private UUID userId;
    private String status;
    private OffsetDateTime createdAt;
    private OffsetDateTime updatedAt;
}
