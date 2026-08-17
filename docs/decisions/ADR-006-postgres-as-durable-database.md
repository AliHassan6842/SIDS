# ADR-006: Use PostgreSQL as the durable database

- Status: Accepted
- Date: 2026-08-16

## Context

SIDS requires transactional business records and future hybrid knowledge retrieval.

## Decision

Use PostgreSQL for durable state, with full-text search and pgvector for retrieval. Store image objects outside the database.

## Consequences

One durable platform supports relational and vector needs. A separate vector database requires future evidence and a new ADR.
