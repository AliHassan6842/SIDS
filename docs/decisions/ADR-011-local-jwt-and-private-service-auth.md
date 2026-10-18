# ADR-011: Use audience-bound local JWTs and private service authentication

## Status

Accepted for the self-contained FYP deployment on 2026-08-22.

## Context

The previous Core API expected an external OIDC issuer that the repository did not start, while the frontend used a simulated token. The FYP needs reproducible register/login behavior and must prevent browser access to Python.

## Decision

Core API issues short-lived HMAC-signed JWTs after BCrypt password verification. Tokens validate signature, issuer, audience, subject, and expiry. The authenticated subject—not caller-supplied user IDs—owns scan queries and image retrieval.

Java authenticates to Python with a separate high-entropy service token and the deployment network does not publish the Python port. Production deployments should replace the shared service token with mTLS or short-lived workload identity when available.

## Consequences

- The project starts without an external identity provider.
- Secrets must be generated into ignored `.env`; committed configuration contains placeholders only.
- Logout is client-side token disposal until revocation/refresh becomes a demonstrated requirement.
- Rotating the JWT secret invalidates all active tokens.
