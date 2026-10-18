package com.agrosense.audit.infrastructure;

import com.agrosense.audit.application.AuditService;
import com.agrosense.audit.application.RecordAuditCommand;
import org.aspectj.lang.ProceedingJoinPoint;
import org.aspectj.lang.annotation.Around;
import org.aspectj.lang.annotation.Aspect;
import org.aspectj.lang.reflect.MethodSignature;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;

import java.lang.reflect.Method;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

@Aspect
@Component
public class AuditAspect {

    private static final Logger log = LoggerFactory.getLogger(AuditAspect.class);

    private final AuditService auditService;
    private final AuditJsonHelper auditJsonHelper;

    public AuditAspect(AuditService auditService, AuditJsonHelper auditJsonHelper) {
        this.auditService = auditService;
        this.auditJsonHelper = auditJsonHelper;
    }

    @Around("@annotation(auditable)")
    public Object auditMethod(ProceedingJoinPoint joinPoint, Auditable auditable) throws Throwable {
        long startTime = System.currentTimeMillis();
        Object result = null;
        Throwable error = null;

        try {
            result = joinPoint.proceed();
            return result;
        } catch (Throwable t) {
            error = t;
            throw t;
        } finally {
            long duration = System.currentTimeMillis() - startTime;
            recordAuditFromJoinPoint(joinPoint, auditable, result, error, duration);
        }
    }

    private void recordAuditFromJoinPoint(
            ProceedingJoinPoint joinPoint,
            Auditable auditable,
            Object result,
            Throwable error,
            long durationMs
    ) {
        try {
            UUID userId = extractCurrentUserId();
            String action = auditable.action();
            String entityType = auditable.entityType();

            Map<String, Object> detailsMap = new HashMap<>();
            detailsMap.put("method", joinPoint.getSignature().toShortString());
            detailsMap.put("executionTimeMs", durationMs);
            detailsMap.put("success", error == null);

            if (error != null) {
                detailsMap.put("error", error.getMessage());
            }

            // Extract method parameter names & values
            if (joinPoint.getSignature() instanceof MethodSignature methodSignature) {
                String[] paramNames = methodSignature.getParameterNames();
                Object[] paramValues = joinPoint.getArgs();
                if (paramNames != null && paramValues != null) {
                    Map<String, Object> params = new HashMap<>();
                    for (int i = 0; i < paramNames.length && i < paramValues.length; i++) {
                        params.put(paramNames[i], paramValues[i] != null ? paramValues[i].toString() : null);
                    }
                    detailsMap.put("parameters", params);
                }
            }

            String detailsJson = auditJsonHelper.toJson(detailsMap);

            RecordAuditCommand command = new RecordAuditCommand(
                    action,
                    userId,
                    entityType.isEmpty() ? null : entityType,
                    null,
                    detailsJson
            );

            auditService.recordEvent(command);
        } catch (Exception e) {
            log.error("Failed to process audit aspect for method {}: {}",
                    joinPoint.getSignature().toShortString(), e.getMessage(), e);
        }
    }

    private UUID extractCurrentUserId() {
        try {
            Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
            if (authentication != null && authentication.isAuthenticated() && authentication.getName() != null) {
                String name = authentication.getName();
                try {
                    return UUID.fromString(name);
                } catch (IllegalArgumentException ignored) {
                    // Name is not a raw UUID (could be sub/username)
                }
            }
        } catch (Exception ignored) {
        }
        return null;
    }
}
