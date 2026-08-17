# ADR-001: Use a monorepo

- Status: Accepted
- Date: 2026-08-16

## Context

SIDS needs coordinated frontend, Java, Python, research, knowledge, contracts, infrastructure, and documentation with clear ownership.

## Decision

Keep these systems in one repository with explicit top-level boundaries and scoped `AGENTS.md` instructions.

## Consequences

Cross-boundary changes are reviewable together, while owners must avoid accidental coupling and broad tooling changes.
