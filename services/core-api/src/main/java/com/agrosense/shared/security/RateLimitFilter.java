package com.agrosense.shared.security;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.time.Clock;
import java.time.Instant;
import java.util.HashMap;
import java.util.Map;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

@Component
public class RateLimitFilter extends OncePerRequestFilter {
    private record Window(long minute, int count) {}
    private static final int DEFAULT_MAX_BUCKETS = 10_000;
    private final Map<String, Window> windows = new HashMap<>();
    private final Clock clock;
    private final int maxBuckets;
    private long lastSweepMinute = Long.MIN_VALUE;

    public RateLimitFilter() { this(Clock.systemUTC(), DEFAULT_MAX_BUCKETS); }
    RateLimitFilter(Clock clock, int maxBuckets) {
        this.clock = clock;
        if (maxBuckets < 1) throw new IllegalArgumentException("maxBuckets must be positive");
        this.maxBuckets = maxBuckets;
    }

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain chain)
        throws ServletException, IOException {
        int limit = limitFor(request.getMethod(), request.getRequestURI());
        if (limit > 0 && !allow(request, limit)) {
            response.setStatus(429);
            response.setContentType(MediaType.APPLICATION_JSON_VALUE);
            response.getWriter().write("{\"code\":\"RATE_LIMITED\",\"message\":\"Too many requests.\",\"retryable\":true,\"requestId\":\""
                + request.getAttribute("requestId") + "\",\"details\":{}}");
            return;
        }
        chain.doFilter(request, response);
    }

    private synchronized boolean allow(HttpServletRequest request, int limit) {
        long minute = Instant.now(clock).getEpochSecond() / 60;
        if (minute != lastSweepMinute) {
            windows.entrySet().removeIf(entry -> entry.getValue().minute() != minute);
            lastSweepMinute = minute;
        }
        String key = request.getRemoteAddr() + ':' + request.getMethod() + ':' + request.getRequestURI();
        Window current = windows.get(key);
        if (current == null) {
            if (windows.size() >= maxBuckets) return false;
            windows.put(key, new Window(minute, 1));
            return true;
        }
        Window updated = new Window(minute, current.count() + 1);
        windows.put(key, updated);
        return updated.count() <= limit;
    }

    synchronized int bucketCount() { return windows.size(); }

    private int limitFor(String method, String uri) {
        if (!"POST".equals(method)) return 0;
        return switch (uri) {
            case "/api/v1/auth/login", "/api/v1/auth/register" -> 10;
            case "/api/v1/vision/validate-frame" -> 120;
            case "/api/v1/scans" -> 20;
            default -> 0;
        };
    }
}
