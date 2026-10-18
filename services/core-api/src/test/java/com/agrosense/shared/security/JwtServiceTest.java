package com.agrosense.shared.security;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import com.auth0.jwt.JWT;
import com.auth0.jwt.algorithms.Algorithm;
import com.auth0.jwt.exceptions.JWTVerificationException;
import java.time.Instant;
import java.util.Date;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class JwtServiceTest {
    private static final String SECRET = "test-secret-that-is-at-least-32-characters-long";
    private static final String ISSUER = "sids-core-api";
    private static final String AUDIENCE = "sids-web";
    private JwtService service;

    @BeforeEach
    void setUp() {
        service = new JwtService(SECRET, ISSUER, AUDIENCE, 30);
    }

    @Test
    void acceptsTokenCreatedForConfiguredIssuerAndAudience() {
        UUID userId = UUID.randomUUID();

        CurrentUser user = service.verify(service.create(userId, "farmer@example.com"));

        assertThat(user).isEqualTo(new CurrentUser(userId, "farmer@example.com"));
    }

    @Test
    void rejectsWrongIssuer() {
        String token = token("different-issuer", AUDIENCE, Instant.now().plusSeconds(60));

        assertThatThrownBy(() -> service.verify(token)).isInstanceOf(JWTVerificationException.class);
    }

    @Test
    void rejectsWrongAudience() {
        String token = token(ISSUER, "different-client", Instant.now().plusSeconds(60));

        assertThatThrownBy(() -> service.verify(token)).isInstanceOf(JWTVerificationException.class);
    }

    @Test
    void rejectsExpiredToken() {
        String token = token(ISSUER, AUDIENCE, Instant.now().minusSeconds(60));

        assertThatThrownBy(() -> service.verify(token)).isInstanceOf(JWTVerificationException.class);
    }

    @Test
    void rejectsPublishedPlaceholderSecret() {
        assertThatThrownBy(() -> new JwtService("replace-with-at-least-32-random-characters", ISSUER, AUDIENCE, 30))
            .isInstanceOf(IllegalStateException.class);
    }

    private String token(String issuer, String audience, Instant expiresAt) {
        return JWT.create()
            .withIssuer(issuer)
            .withAudience(audience)
            .withSubject(UUID.randomUUID().toString())
            .withClaim("email", "farmer@example.com")
            .withExpiresAt(Date.from(expiresAt))
            .sign(Algorithm.HMAC256(SECRET));
    }
}
