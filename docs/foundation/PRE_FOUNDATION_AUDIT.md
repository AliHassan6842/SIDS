# Pre-foundation audit

Audit date: 2026-08-16

## Repository placement and Git

- Workspace root: `D:\vs code\uniSIDS`.
- Target repository: `D:\vs code\uniSIDS\FinalYearProject`.
- The workspace root had a separate Git repository with no commits and two untracked entries: `FinalYearProject/` and `Prompt1.md`.
- `FinalYearProject` was an independent Git repository on `main`, tracking `origin/main`, with a clean working tree before F0.
- Recent inner-repository HEAD at audit time: `2ed47393` (`Changes`).

## Existing frontend

- The frontend occupied the root of `FinalYearProject`; it was not under `apps/web`.
- Framework: React 18, TypeScript, Vite 5, Material UI, Redux Toolkit/Redux Saga, React Router, Zod, and React Hook Form.
- Package identity: `agrosense`, version `1.0.0`, private.
- Existing scripts: `dev`, `build`, `lint`, and `preview`.
- Existing package manager evidence: npm `package-lock.json`; no pnpm workspace or pnpm lockfile.
- Existing generated content: `dev-dist/registerSW.js`.
- The initial working tree contained 46,739 tracked files: 69 under `src`, nine other frontend/repository files, and 46,661 under `node_modules`.
- The committed `node_modules` tree was approximately 173.8 MB on disk despite the existing `.gitignore` rule. F0 preserves and relocates it rather than deleting frontend-owned content.

## Toolchain observed

- Node.js: `v24.18.1`.
- Corepack: `0.35.0`.
- pnpm: `11.18.0` (available through the Windows command shim; PowerShell script execution policy blocks `pnpm.ps1`).
- npm: `11.16.0`.
- No `.nvmrc`, `.node-version`, or `.tool-versions` file existed.

## Existing repository facilities

- Documentation: only the frontend `README.md`.
- Git ignore: frontend-oriented Node, IDE, environment, certificate, and credential patterns.
- Docker: no Dockerfile or Compose configuration.
- CI: no `.github` configuration or other CI files found.
- Services, ML, knowledge, shared packages, infrastructure boundaries, ADRs, and root agent instructions: absent.
- License: no license file found; F0 does not invent one.

## Foundation decision

Use the existing `FinalYearProject` Git repository as the monorepo root. Relocate all frontend-owned working-tree items into `apps/web` through Git-aware moves, retain its npm lockfile and committed dependencies unchanged, then add root pnpm orchestration and documentation outside the protected frontend.
