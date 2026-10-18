package com.agrosense.shared.error.exceptions;

import java.util.Map;

public class BusinessRuleViolationException extends BaseException {
    public BusinessRuleViolationException(String message) {
        super(message, "BUSINESS_RULE_VIOLATION", false, Map.of());
    }

    public BusinessRuleViolationException(String message, String code) {
        super(message, code, false, Map.of());
    }

    public BusinessRuleViolationException(String message, String code, Map<String, Object> details) {
        super(message, code, false, details);
    }
}
