package com.agrosense.task.domain;

/**
 * Supported task types within the AgroSense digital crop scout lifecycle.
 */
public enum TaskType {
    /**
     * Re-scout a field or sample point to verify pest/disease progression.
     */
    RESCOUT,

    /**
     * General follow-up task triggered by observations or farmer actions.
     */
    FOLLOW_UP,

    /**
     * Comprehensive on-site field or crop condition inspection.
     */
    INSPECTION,

    /**
     * Post-treatment verification to check efficacy of chemical/biological applications.
     */
    TREATMENT_FOLLOW_UP,

    /**
     * Agronomist or expert review required for ambiguous/high-risk diagnoses.
     */
    EXPERT_REVIEW
}
