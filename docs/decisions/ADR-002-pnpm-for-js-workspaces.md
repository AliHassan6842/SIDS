# ADR-002: Use pnpm for JavaScript workspaces

- Status: Accepted
- Date: 2026-08-16

## Context

The repository needs root orchestration for the existing frontend and future JS/TS packages without treating Java or Python as Node packages.

## Decision

Use a Corepack-pinned pnpm workspace covering `apps/*`, `packages/*`, and `tools/*`. Preserve the frontend's npm lockfile until its owner approves a migration; root scripts delegate frontend execution to npm during this transition. Set pnpm's dependency check to warning-only so orchestration cannot implicitly migrate the protected dependency tree.

## Consequences

Root scripts can target JS/TS packages consistently. Language-native services retain their own build tools, and the temporary dual-lockfile situation is documented.
