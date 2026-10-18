package com.agrosense.shared.error.exceptions;

import java.util.Map;

public class ResourceNotFoundException extends BaseException {
    public ResourceNotFoundException(String message) {
        super(message, "RESOURCE_NOT_FOUND", false, Map.of());
    }

    public ResourceNotFoundException(String message, String resourceType, String resourceId) {
        super(message, "RESOURCE_NOT_FOUND", false, Map.of("resourceType", resourceType, "resourceId", resourceId));
    }
}
