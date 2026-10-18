package com.agrosense.analysis.domain;

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
