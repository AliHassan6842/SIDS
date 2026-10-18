package com.agrosense.survey.domain;

import jakarta.persistence.*;
import java.time.OffsetDateTime;
import java.util.UUID;

@Entity
@Table(name = "survey_protocols")
public class SurveyProtocol {
    @Id
    private UUID id;
    private String name;
    private String cropId;
    private String problemId;
    private String growthStage;
    private Integer minimumSamples;
    private String samplingUnit;
    private String measureType;
    private OffsetDateTime createdAt;
}
