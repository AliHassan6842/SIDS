package com.agrosense.survey.domain;

import jakarta.persistence.*;
import java.time.OffsetDateTime;
import java.util.UUID;

@Entity
@Table(name = "survey_points")
public class SurveyPoint {
    @Id
    private UUID id;
    private UUID surveyId;
    private Double locationLat;
    private Double locationLng;
    private OffsetDateTime createdAt;
}
