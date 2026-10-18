package com.agrosense.audit.domain;

public final class AuditAction {

    // Identity & Security
    public static final String USER_REGISTERED = "USER_REGISTERED";
    public static final String USER_LOGIN = "USER_LOGIN";
    public static final String USER_LOGOUT = "USER_LOGOUT";
    public static final String USER_UPDATED = "USER_UPDATED";
    public static final String DEVICE_REGISTERED = "DEVICE_REGISTERED";
    public static final String SECURITY_ACCESS_DENIED = "SECURITY_ACCESS_DENIED";

    // Farm & Field Operations
    public static final String FARM_CREATED = "FARM_CREATED";
    public static final String FARM_UPDATED = "FARM_UPDATED";
    public static final String FARM_DELETED = "FARM_DELETED";
    public static final String FIELD_CREATED = "FIELD_CREATED";
    public static final String FIELD_UPDATED = "FIELD_UPDATED";
    public static final String FIELD_BOUNDARY_UPDATED = "FIELD_BOUNDARY_UPDATED";

    // Crop Cycle & Scouting
    public static final String CROP_CYCLE_CREATED = "CROP_CYCLE_CREATED";
    public static final String CROP_CYCLE_UPDATED = "CROP_CYCLE_UPDATED";
    public static final String CROP_CYCLE_COMPLETED = "CROP_CYCLE_COMPLETED";
    public static final String SURVEY_RECORDED = "SURVEY_RECORDED";
    public static final String OBSERVATION_RECORDED = "OBSERVATION_RECORDED";

    // Diagnosis & Agronomy
    public static final String DIAGNOSIS_REQUESTED = "DIAGNOSIS_REQUESTED";
    public static final String DIAGNOSIS_COMPLETED = "DIAGNOSIS_COMPLETED";
    public static final String RECOMMENDATION_GENERATED = "RECOMMENDATION_GENERATED";
    public static final String TREATMENT_APPLIED = "TREATMENT_APPLIED";
    public static final String TREATMENT_UPDATED = "TREATMENT_UPDATED";

    // Tasks & Notifications
    public static final String TASK_CREATED = "TASK_CREATED";
    public static final String TASK_COMPLETED = "TASK_COMPLETED";
    public static final String NOTIFICATION_DISPATCHED = "NOTIFICATION_DISPATCHED";

    // Offline Sync & Storage
    public static final String SYNC_EVENT_PROCESSED = "SYNC_EVENT_PROCESSED";
    public static final String STORAGE_OBJECT_STORED = "STORAGE_OBJECT_STORED";
    public static final String STORAGE_OBJECT_DELETED = "STORAGE_OBJECT_DELETED";

    private AuditAction() {}
}
