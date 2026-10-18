package com.agrosense.shared.error;

import java.util.Map;

public record ApiError(String code, String message, boolean retryable, String requestId, Map<String, Object> details) {}
