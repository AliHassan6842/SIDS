package com.agrosense.shared.security;

import static org.assertj.core.api.Assertions.assertThat;

import jakarta.servlet.FilterChain;
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneId;
import java.time.ZoneOffset;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;
import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.mock.web.MockHttpServletResponse;

class RateLimitFilterTest {
    @Test
    void doesNotRateLimitFakeSuffixPath() throws Exception {
        RateLimitFilter filter = new RateLimitFilter(Clock.systemUTC(), 2);
        AtomicInteger passed = new AtomicInteger();
        FilterChain chain = (request, response) -> passed.incrementAndGet();

        for (int index = 0; index < 15; index++)
            invoke(filter, "POST", "/fake/api/v1/auth/login", "192.0.2.1", chain);

        assertThat(passed).hasValue(15);
        assertThat(filter.bucketCount()).isZero();
    }

    @Test
    void limitsOnlyExactMethodAndPath() throws Exception {
        RateLimitFilter filter = new RateLimitFilter(Clock.systemUTC(), 20);
        AtomicInteger passed = new AtomicInteger();
        FilterChain chain = (request, response) -> passed.incrementAndGet();

        for (int index = 0; index < 10; index++)
            assertThat(invoke(filter, "POST", "/api/v1/auth/login", "192.0.2.2", chain)).isEqualTo(200);
        assertThat(invoke(filter, "POST", "/api/v1/auth/login", "192.0.2.2", chain)).isEqualTo(429);
        assertThat(invoke(filter, "GET", "/api/v1/auth/login", "192.0.2.2", chain)).isEqualTo(200);
        assertThat(passed).hasValue(11);
    }

    @Test
    void capsBucketsAndExpiresThemOnTheNextMinute() throws Exception {
        MutableClock clock = new MutableClock(Instant.parse("2026-08-22T00:00:00Z"));
        RateLimitFilter filter = new RateLimitFilter(clock, 2);
        AtomicInteger passed = new AtomicInteger();
        FilterChain chain = (request, response) -> passed.incrementAndGet();

        assertThat(invoke(filter, "POST", "/api/v1/scans", "192.0.2.10", chain)).isEqualTo(200);
        assertThat(invoke(filter, "POST", "/api/v1/scans", "192.0.2.11", chain)).isEqualTo(200);
        assertThat(invoke(filter, "POST", "/api/v1/scans", "192.0.2.12", chain)).isEqualTo(429);
        assertThat(filter.bucketCount()).isEqualTo(2);

        clock.advanceSeconds(61);
        assertThat(invoke(filter, "POST", "/api/v1/scans", "192.0.2.12", chain)).isEqualTo(200);
        assertThat(filter.bucketCount()).isEqualTo(1);
    }

    private int invoke(RateLimitFilter filter, String method, String uri, String remoteAddress, FilterChain chain)
        throws Exception {
        MockHttpServletRequest request = new MockHttpServletRequest(method, uri);
        request.setRemoteAddr(remoteAddress);
        request.setAttribute("requestId", "test-request");
        MockHttpServletResponse response = new MockHttpServletResponse();
        filter.doFilter(request, response, chain);
        return response.getStatus();
    }

    private static final class MutableClock extends Clock {
        private Instant instant;
        private MutableClock(Instant instant) { this.instant = instant; }
        void advanceSeconds(long seconds) { instant = instant.plusSeconds(seconds); }
        @Override public ZoneId getZone() { return ZoneOffset.UTC; }
        @Override public Clock withZone(ZoneId zone) { return this; }
        @Override public Instant instant() { return instant; }
    }
}
