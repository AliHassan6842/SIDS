# Core API boundary

This directory is reserved for the future Java/Spring core API owned by the Java Platform / Backend member. No application has been initialized in F0.

Planned technology includes Spring Boot, Spring Security, Spring Data JPA, Flyway, PostgreSQL/pgvector integration, Valkey, Bucket4j, Resilience4j, OpenAPI, Actuator/Micrometer, JUnit, and Testcontainers.

The core API will own identity integration, authorization, farms and fields, crop cycles, observations and surveys, diagnoses, history, weather context, thresholds, recommendations, treatments, follow-ups, tasks, retrieval orchestration, image-storage orchestration, AI job submission, offline sync, idempotency, auditing, and rate limiting.

**Java owns business truth.** AI output is evidence consumed by the domain; it never overrides authorization, field state, economic-threshold interpretation, agronomic recommendations, or treatment policy.
