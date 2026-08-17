# ADR-009: Treat hardware as an optional adapter

- Status: Accepted
- Date: 2026-08-16

## Context

Future traps, cameras, or sensors may enrich SIDS, but current farmer workflows must not depend on unavailable devices.

## Decision

Integrate hardware through optional adapters and stable contracts rather than embedding device assumptions in the core domain.

## Consequences

The platform remains usable without hardware and can add device integrations without rewriting core workflows.
