package com.agrosense.shared.error.exceptions;

import java.util.Map;

public abstract class BaseException extends RuntimeException {
    private final String code;
    private final boolean retryable;
    private final Map<String, Object> details;

    public BaseException(String message, String code, boolean retryable, Map<String, Object> details) {
        super(message);
        this.code = code;
        this.retryable = retryable;
        this.details = details != null ? details : Map.of();
    }

    public String getCode() {
        return code;
    }

    public boolean isRetryable() {
        return retryable;
    }

    public Map<String, Object> getDetails() {
        return details;
    }
}
