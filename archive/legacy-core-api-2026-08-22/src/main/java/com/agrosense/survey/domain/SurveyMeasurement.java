package com.agrosense.survey.domain;

import jakarta.persistence.*;
import java.time.OffsetDateTime;
import java.util.UUID;

@Entity
@Table(name = "survey_measurements")
public class SurveyMeasurement {
    @Id
    private UUID id;
    private UUID pointId;
    private String measureType;
    private Double value;
    private String unit;
    private OffsetDateTime createdAt;
}
