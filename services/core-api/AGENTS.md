# Core API instructions

- Use a feature-first modular architecture.
- Within meaningful features, prefer `api`, `application`, `domain`, and `infrastructure` boundaries.
- Domain code must not import Spring, JPA, transport, or persistence infrastructure.
- Controllers validate/translate transport concerns and contain no business logic.
- Define repositories as ports/interfaces at the correct boundary; external adapters belong in infrastructure.
- Enforce authorization and farm ownership server-side.
- Java owns business truth and agronomic decisions, including risk, thresholds, recommendations, and treatment policy.
- Treat AI results as versioned inputs with uncertainty, never as authority.
- Use migrations for durable schema changes and integration tests for real infrastructure behavior.
