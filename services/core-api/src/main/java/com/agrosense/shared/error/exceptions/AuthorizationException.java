package com.agrosense.shared.error.exceptions;

import java.util.Map;

public class AuthorizationException extends BaseException {
    public AuthorizationException(String message) {
        super(message, "ACCESS_DENIED", false, Map.of());
    }
    
    public AuthorizationException(String message, String code) {
        super(message, code, false, Map.of());
    }
}
