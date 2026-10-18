package com.agrosense.shared.error;

import java.util.Map;

public record ErrorResponse(
        String code,
        String message,
        String requestId,
        boolean retryable,
        Map<String, Object> details
) {
}
