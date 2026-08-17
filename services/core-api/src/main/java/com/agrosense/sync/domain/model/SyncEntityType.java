package com.agrosense.sync.domain.model;

/**
 * Enumeration of domain entity types supported by the offline synchronization system.
 */
public enum SyncEntityType {
    OBSERVATION("observations"),
    SAMPLE("samples"),
    TASK("tasks"),
    FIELD("fields"),
    FARM("farms"),
    CROP_CYCLE("crop_cycles"),
    FIELD_SURVEY("field_surveys"),
    SURVEY_POINT("survey_points"),
    SURVEY_MEASUREMENT("survey_measurements"),
    TREATMENT("treatments"),
    TREATMENT_OUTCOME("treatment_outcomes"),
    STORAGE_OBJECT("storage_objects"),
    UNKNOWN("unknown");

    private final String tableName;

    SyncEntityType(String tableName) {
        this.tableName = tableName;
    }

    public String getTableName() {
        return tableName;
    }

    public static SyncEntityType fromString(String value) {
        if (value == null || value.isBlank()) {
            return UNKNOWN;
        }
        String normalized = value.trim().toUpperCase().replace("-", "_");
        for (SyncEntityType type : values()) {
            if (type.name().equalsIgnoreCase(normalized) || type.tableName.equalsIgnoreCase(value.trim())) {
                return type;
            }
        }
        return UNKNOWN;
    }
}
