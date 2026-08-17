# ADR-007: Use Valkey for transient state and AI jobs

- Status: Accepted
- Date: 2026-08-16

## Context

Caching, rate controls, idempotency, locks, and asynchronous AI work need fast transient coordination.

## Decision

Use Valkey for those responsibilities and never as the permanent system of record.

## Consequences

Valkey data may be rebuilt or expire. Durable job/business outcomes must be recorded in PostgreSQL.
