import os

base_dir = r"d:\vs code\uniSIDS\FinalYearProject\services\core-api\src\main\java\com\agrosense"

files = {
    "observation/domain/Observation.java": """package com.agrosense.observation.domain;

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
""",
    "observation/domain/Sample.java": """package com.agrosense.observation.domain;

import jakarta.persistence.*;
import java.time.OffsetDateTime;
import java.util.UUID;

@Entity
@Table(name = "samples")
public class Sample {
    @Id
    private UUID id;
    private UUID observationId;
    private Double locationLat;
    private Double locationLng;
    private OffsetDateTime createdAt;
    private OffsetDateTime updatedAt;
}
""",
    "observation/domain/ObservationImage.java": """package com.agrosense.observation.domain;

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
""",
    "survey/domain/SurveyProtocol.java": """package com.agrosense.survey.domain;

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
""",
    "survey/domain/FieldSurvey.java": """package com.agrosense.survey.domain;

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
""",
    "survey/domain/SurveyPoint.java": """package com.agrosense.survey.domain;

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
""",
    "survey/domain/SurveyMeasurement.java": """package com.agrosense.survey.domain;

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
""",
    "analysis/domain/AnalysisJob.java": """package com.agrosense.analysis.domain;

import jakarta.persistence.*;
import java.time.OffsetDateTime;
import java.util.UUID;

@Entity
@Table(name = "analysis_jobs")
public class AnalysisJob {
    @Id
    private UUID id;
    private UUID observationId;
    private String status;
    private OffsetDateTime createdAt;
    private OffsetDateTime updatedAt;
}
""",
    "analysis/infrastructure/AIResultConsumer.java": """package com.agrosense.analysis.infrastructure;

import org.springframework.data.redis.connection.stream.ObjectRecord;
import org.springframework.data.redis.stream.StreamListener;
import org.springframework.stereotype.Service;

@Service
public class AIResultConsumer implements StreamListener<String, ObjectRecord<String, String>> {
    @Override
    public void onMessage(ObjectRecord<String, String> message) {
        // Implement AI Result Consumer with manual ack and idempotency
    }
}
""",
    "diagnosis/domain/Diagnosis.java": """package com.agrosense.diagnosis.domain;

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
""",
    "diagnosis/domain/Detection.java": """package com.agrosense.diagnosis.domain;

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
""",
    "diagnosis/domain/Classification.java": """package com.agrosense.diagnosis.domain;

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
""",
    "diagnosis/domain/SeverityAssessment.java": """package com.agrosense.diagnosis.domain;

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
"""
}

for path, content in files.items():
    full_path = os.path.join(base_dir, path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

print("Scaffolding complete.")
