package com.agrosense.audit.infrastructure;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;

@Component
public class AuditJsonHelper {

    private static final Logger log = LoggerFactory.getLogger(AuditJsonHelper.class);
    private final ObjectMapper objectMapper;

    public AuditJsonHelper() {
        this.objectMapper = new ObjectMapper();
    }

    public AuditJsonHelper(ObjectMapper objectMapper) {
        this.objectMapper = objectMapper != null ? objectMapper : new ObjectMapper();
    }

    public String toJson(Object object) {
        if (object == null) {
            return "{}";
        }
        if (object instanceof String str) {
            return str;
        }
        try {
            return objectMapper.writeValueAsString(object);
        } catch (Exception e) {
            log.warn("Failed to serialize audit details to JSON: {}", e.getMessage());
            return "{\"raw\":\"" + object.toString().replace("\"", "\\\"") + "\"}";
        }
    }
}
