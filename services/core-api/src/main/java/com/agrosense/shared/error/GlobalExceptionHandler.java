package com.agrosense.shared.error;

import jakarta.servlet.http.HttpServletRequest;
import java.util.Map;
import java.util.UUID;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.method.annotation.MethodArgumentTypeMismatchException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.multipart.MaxUploadSizeExceededException;

@RestControllerAdvice
public class GlobalExceptionHandler {
    @ExceptionHandler(ApiException.class)
    ResponseEntity<ApiError> api(ApiException e, HttpServletRequest request) {
        return ResponseEntity.status(e.status()).body(error(e.code(), e.getMessage(), e.retryable(), request));
    }
    @ExceptionHandler(MethodArgumentNotValidException.class)
    ResponseEntity<ApiError> validation(MethodArgumentNotValidException e, HttpServletRequest request) {
        return ResponseEntity.badRequest().body(error("VALIDATION_FAILED", "Request validation failed.", false, request));
    }
    @ExceptionHandler(MethodArgumentTypeMismatchException.class)
    ResponseEntity<ApiError> invalidPathValue(MethodArgumentTypeMismatchException e, HttpServletRequest request) {
        return ResponseEntity.badRequest().body(error("VALIDATION_FAILED", "Request validation failed.", false, request));
    }
    @ExceptionHandler(MaxUploadSizeExceededException.class)
    ResponseEntity<ApiError> uploadTooLarge(MaxUploadSizeExceededException e, HttpServletRequest request) {
        return ResponseEntity.status(HttpStatus.PAYLOAD_TOO_LARGE)
            .body(error("IMAGE_TOO_LARGE", "Image exceeds the byte limit.", true, request));
    }
    @ExceptionHandler(Exception.class)
    ResponseEntity<ApiError> unexpected(Exception e, HttpServletRequest request) {
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
            .body(error("INTERNAL_ERROR", "The request could not be completed.", true, request));
    }
    private ApiError error(String code, String message, boolean retryable, HttpServletRequest request) {
        Object existing = request.getAttribute("requestId");
        return new ApiError(code, message, retryable, existing == null ? UUID.randomUUID().toString() : existing.toString(), Map.of());
    }
}
