# ADR-003: Protect the existing frontend

- Status: Accepted
- Date: 2026-08-16

## Context

The frontend is owned by another team member and predates the monorepo foundation.

## Decision

Relocate it to `apps/web`, preserve its contents, and require explicit user authorization for any further edits under that directory.

## Consequences

Foundation and backend work cannot opportunistically refactor, format, upgrade, or fix the frontend. Needed contract changes are proposed to its owner.
