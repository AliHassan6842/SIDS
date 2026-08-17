# Ownership

| Owner | Paths | Authority |
| --- | --- | --- |
| Frontend member | `apps/web` | Frontend source, configuration, dependencies, UX, and local contracts |
| Java platform member | `services/core-api`, Java-owned domain/infra | Business truth, authorization, agronomic decisions, persistence orchestration |
| AI/research lead | `services/ai-service`, `ml`, AI/research side of `knowledge` | Production inference computation, research, evaluation, approved knowledge preparation |
| Shared | `packages/contracts`, `infra`, `docs`, `.github` | Reviewed interfaces, infrastructure, decisions, and CI |

Changes crossing an ownership boundary require coordination. A needed frontend contract change must be documented for the frontend owner rather than applied by non-frontend tasks.
