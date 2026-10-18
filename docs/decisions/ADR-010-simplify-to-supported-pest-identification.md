# ADR-010: Simplify production to supported pest identification

## Status

Accepted on 2026-08-22. This decision supersedes production aspects of ADR-007 and any earlier design that requires disease specialists, field incidence, agronomic thresholds, pesticide decisions, RAG, pgvector, or asynchronous AI jobs.

## Context

The defensible FYP claim is limited to identifying selected supported agricultural pests from controlled close-up images. The legacy architecture contained unrelated and unverified domain complexity that increased safety, security, testing, and demonstration risk.

## Decision

The browser calls Java only. Java authenticates the user, validates ownership and crop support, sanitizes/stores the image, calls private Python synchronously, verifies that any returned `pestId` is allowed for the selected crop, retrieves predefined attributed guidance, persists the scan, and returns the result.

Python performs bounded image validation and approved-model inference and returns only `IDENTIFIED`, `UNKNOWN`, or `REJECTED_IMAGE` plus evidence and model metadata. It owns no farmer authorization or guidance policy.

PostgreSQL remains durable truth. Private object storage (or a private local adapter in development) stores images. No Valkey work queue or pgvector dependency is used by this synchronous scope.

## Consequences

- Product routes and APIs become smaller and testable end to end.
- Unsupported and uncertain inputs are explicit rather than forced into a class.
- Legacy production code is archived outside compiled/imported source and retained in Git history.
- Supported crops and pests cannot be seeded until dataset scope is measured and frozen.
