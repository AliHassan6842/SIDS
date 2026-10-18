package com.agrosense.shared.security;

import com.auth0.jwt.JWT;
import com.auth0.jwt.JWTVerifier;
import com.auth0.jwt.algorithms.Algorithm;
import com.auth0.jwt.exceptions.JWTVerificationException;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.Date;
import java.util.UUID;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

@Component
public class JwtService {
    private final Algorithm algorithm;
    private final JWTVerifier verifier;
    private final String issuer;
    private final String audience;
    private final long tokenMinutes;

    public JwtService(@Value("${sids.auth.secret}") String secret,
                      @Value("${sids.auth.issuer}") String issuer,
                      @Value("${sids.auth.audience}") String audience,
                      @Value("${sids.auth.token-minutes}") long tokenMinutes) {
        if (invalidSecret(secret, 32))
            throw new IllegalStateException("AUTH_JWT_SECRET must be a non-placeholder value of at least 32 characters");
        this.algorithm = Algorithm.HMAC256(secret);
        this.issuer = issuer;
        this.audience = audience;
        this.tokenMinutes = tokenMinutes;
        this.verifier = JWT.require(algorithm).withIssuer(issuer).withAudience(audience).build();
    }

    public String create(UUID userId, String email) {
        Instant now = Instant.now();
        return JWT.create().withIssuer(issuer).withAudience(audience).withSubject(userId.toString())
            .withClaim("email", email).withIssuedAt(Date.from(now))
            .withExpiresAt(Date.from(now.plus(tokenMinutes, ChronoUnit.MINUTES))).sign(algorithm);
    }

    public CurrentUser verify(String token) throws JWTVerificationException {
        var jwt = verifier.verify(token);
        return new CurrentUser(UUID.fromString(jwt.getSubject()), jwt.getClaim("email").asString());
    }

    private boolean invalidSecret(String secret, int minimumLength) {
        if (secret == null || secret.isBlank() || secret.length() < minimumLength) return true;
        String normalized = secret.toLowerCase(java.util.Locale.ROOT);
        return normalized.contains("replace-with") || normalized.contains("change-this") || normalized.contains("development-only");
    }
}
