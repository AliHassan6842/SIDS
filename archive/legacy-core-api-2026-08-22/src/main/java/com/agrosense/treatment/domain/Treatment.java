package com.agrosense.treatment.domain;

import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Enumerated;
import jakarta.persistence.EnumType;
import java.time.LocalDateTime;

@Entity
public class Treatment {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    private String name;
    private String description;
    
    @Enumerated(EnumType.STRING)
    private TreatmentType type;
    
    @Enumerated(EnumType.STRING)
    private TreatmentOutcome outcome;
    
    private LocalDateTime appliedAt;

    protected Treatment() {}

    public Treatment(String name, String description, TreatmentType type) {
        this.name = name;
        this.description = description;
        this.type = type;
        this.outcome = TreatmentOutcome.UNKNOWN;
        this.appliedAt = LocalDateTime.now();
    }

    public void updateOutcome(TreatmentOutcome outcome) {
        this.outcome = outcome;
    }

    public Long getId() { return id; }
    public String getName() { return name; }
    public String getDescription() { return description; }
    public TreatmentType getType() { return type; }
    public TreatmentOutcome getOutcome() { return outcome; }
    public LocalDateTime getAppliedAt() { return appliedAt; }
}
