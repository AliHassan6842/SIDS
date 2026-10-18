# SIDS final security review

Date: 2026-08-22  
Method: Codex Security standard, single-pass production-scope audit  
Result: **PARTIAL**

No validated critical, high, medium, or low finding remains in the reviewed production source after the repairs listed below. The result is still PARTIAL rather than PASS because the independent baseline worker could not start at the session thread limit and online Java/Python advisory tooling was unavailable. The live Docker gap present during the sealed scan was subsequently closed by the post-scan verification below.

The Codex Security workbench sealed scan `abd40650-686e-411b-9b00-6c7fa6ac35e5` with zero remaining findings and partial coverage. It warned that the working tree changed during the scan because the four findings were repaired in place. This repository report therefore records both the original finding evidence and the post-repair test results; the sealed workbench artifacts remain bound to their original registered snapshot.

## Scope and threat model

Reviewed production surfaces:

- Browser to Java: bearer-token handling, protected routes, camera lifecycle, upload construction, client-side file gates, CORS/CSRF assumptions, external links, and React rendering sinks.
- Java public boundary: registration/login, JWT creation and verification, current-user propagation, scan ownership, SQL parameters, upload byte/pixel/type gates, private image storage, AI response validation, rate limiting, request IDs, error bodies, secrets, and logging behavior.
- Java to private Python: service-token authentication, request timeouts, multipart fields, response validation, image parsing, inference resource bounds, model manifest/artifact integrity, and absence of request-driven filesystem or outbound-network access.
- Infrastructure: database/API bindings, private AI exposure, required credentials, read-only model volume, private image volume, non-root application containers, health endpoints, and Compose interpolation.

Protected assets are farmer identities and bearer tokens, per-user scan history and images, database credentials, the Java-to-AI service credential, model integrity, agronomy guidance integrity, and service availability. Relevant attackers are an unauthenticated Internet client, an authenticated farmer with malicious identifiers or images, an actor with internal-network reach to the AI service, and a deployment or model-supply-chain actor. Trust boundaries are browser↔Java, Java↔PostgreSQL/private image storage, Java↔Python, and deployment configuration↔runtime containers.

Explicit exclusions requested for this review: `archive/**`, fetched/prepared datasets, dataset image trees, model runs and weights, `node_modules`, `dist`, `target`, test artifacts, generated reports, and historical revisions. The promoted model manifest was reviewed, but the excluded weight was not opened or re-hashed.

## Fixed findings

| ID | Original severity | Finding and prerequisite | Repair evidence | Validation |
|---|---|---|---|---|
| SEC-001 | Medium | Published fallback JWT and Java↔AI secrets could be accepted when services were started outside the guarded Compose path. Forging a victim session additionally required a valid victim UUID; direct AI abuse required network reach. | `application.yml` now requires `DATABASE_PASSWORD`, `AUTH_JWT_SECRET`, and `AI_SERVICE_TOKEN`; `JwtService` rejects short/published placeholders; `AiClient` rejects short/published placeholders; Python `Settings.service_token` is required and rejects placeholders. Compose also requires all three secrets. | Missing and placeholder Python tokens were both rejected in an isolated settings check; `JwtServiceTest` and `AiClientSecretTest` cover Java placeholders. |
| SEC-002 | Medium | The old pre-authentication rate limiter keyed a never-evicted map by raw URI, so unlimited fake suffix paths could allocate unlimited heap. | `RateLimitFilter` now matches exact POST paths, caps buckets at 10,000, and expires prior-minute entries under synchronization. | `RateLimitFilterTest` covers fake suffixes, exact method/path limits, capacity, and expiry. |
| SEC-003 | Low | Unknown login emails skipped BCrypt while existing emails performed cost-12 BCrypt, creating a timing oracle. The public registration conflict response and per-IP limit reduced incremental impact. | `AuthService` now uses a cost-12 dummy hash for missing users and preserves one uniform `BAD_CREDENTIALS` path; `LoginRequest` is bounded at 128 characters without a minimum-length precheck. | `AuthServiceTest.loginUsesSameErrorForUnknownEmailAndWrongPassword` verifies the dummy-hash call and uniform error. |
| SEC-004 | Low | In the locked FastAPI design, route-level authentication could occur after multipart/form parsing, allowing an unauthenticated internal caller to consume parser/spool resources before rejection. Compose keeps the AI service private, which constrained reachability. | The AI service now authenticates `/internal/v1/**` in HTTP middleware before `call_next`; route-level auth dependencies were removed, while bounded upload reads remain. | `test_internal_auth_rejects_before_multipart_parsing` sends malformed multipart without a token and receives 401; the final expanded AI suite passed 22/22. |

## Remaining findings and residual risks

No source-backed vulnerability remains reportable at critical, high, medium, or low severity in the reviewed current tree.

Residual, non-finding risks:

- The rate limiter is bounded but process-local. A future multi-instance deployment should use the architecture-designated Valkey limiter so limits are shared across replicas. Proxy deployment also needs an explicit trusted-client-IP policy; blindly trusting forwarded headers would permit bypass.
- Browser bearer tokens remain in `localStorage`. No remotely controlled HTML/JavaScript sink was found—React renders server strings as text and the catalog has no public mutation route—but any future XSS or third-party script would gain token access. A strict deployment CSP and short token lifetime remain useful defense in depth.
- The model loader verifies the artifact SHA-256 from a strict manifest and the Compose mount is read-only. The checksum proves consistency, not publisher identity; production promotion should eventually sign manifests or verify them against a separately protected registry.
- The application returns generic unexpected-error bodies, but the Java exception handler does not itself emit a correlated server log. Operational logging and alerting should be confirmed in the deployment platform.

## Controls verified

- Frontend route guards are usability controls only; Java authenticates every non-login/register/health request. Identifiers are encoded before URL construction. Gallery input is limited client-side to JPEG/PNG and 12 MB, while Java independently enforces the authoritative 8 MB multipart/byte limits.
- React code contains no `dangerouslySetInnerHTML`, direct `innerHTML`, dynamic evaluation, or request-controlled script construction. Guidance source links originate from seeded database knowledge and use `rel="noreferrer"` when opening a new tab.
- Java uses stateless bearer authentication, HMAC JWT verification with issuer, audience, expiry, and a non-placeholder minimum-length secret. Scan list/get/image queries include both scan UUID and authenticated user UUID; image responses use `Cache-Control: no-store`.
- SQL values are bound parameters. The one dynamic catalog column is selected only by internal constant callers (`id` or `slug`), not request text.
- Java accepts only JPEG/PNG magic, checks compressed bytes and decoded dimensions before full processing, converts to RGB, and re-encodes sanitized JPEG. Storage keys are constructed from server-generated UUIDs and normalized beneath the configured private root.
- Java validates private AI status/reason/model/confidence/bounding-box values and allowlists the predicted pest slug against the selected crop before persistence.
- Python checks MIME and magic, disables truncated-image loading, enforces byte and pixel bounds, verifies then converts and re-encodes images, bounds inference concurrency, and returns UNKNOWN rather than forcing an unsupported class. Runtime request data does not select filesystem paths or outbound URLs.
- The model manifest forbids extra fields, bounds input size/threshold, requires a 64-hex checksum, resolves the configured artifact, verifies its SHA-256 before loading, and fails readiness when unavailable.
- Compose binds PostgreSQL and Java only to `127.0.0.1`; Python uses internal `expose` rather than a host port. Java and Python application containers run as UID 65532; the model mount is read-only and scan images use a private named volume.
- The real `.env` is present but ignored; only `.env.example` is tracked. The example contains instructions/placeholders, not usable credentials.

## Validation evidence

- Python Ruff and mypy — PASS; `pytest services/ai-service/tests` — PASS, 22 passed, including private mode/crop validation and general-mode label suppression.
- `services\core-api\mvnw.cmd test` with Temurin JDK 21 — PASS, exit 0; 59 tests, 0 failures, 0 errors, 0 skipped. PostgreSQL 16.15 Testcontainers validated and applied Flyway V001 through V010.
- Isolated Python settings check — PASS, missing token rejected; published placeholder rejected.
- `npm --prefix apps\web audit --omit=dev --offline --json` — PASS for the cached/offline production audit set, 0 known production vulnerabilities across 10 production dependencies. This does not substitute for an online advisory refresh.
- `docker compose -f infra/docker-compose.yml config --quiet` with ephemeral non-placeholder values — PASS.
- Production secret/XSS sink search — no published runtime fallback remained; no frontend dangerous HTML or dynamic-evaluation sink was found.
- `mvnw.cmd -o -q dependency:tree -Dscope=runtime` — BLOCKED offline because `maven-dependency-plugin` was not present in the local Maven cache. No network fallback was used.
- `pip-audit` and Poetry CLI — unavailable; nothing was installed or downloaded during the offline source review.

The live cross-service security path was not available during the sealed static scan; it was executed successfully afterward as recorded below. Deterministic frontend E2E and contract results are tracked separately.
## Post-scan release verification

After the sealed security scan, the expanded Compose stack was rebuilt with generated local secrets. PostgreSQL, the private AI service, and Core API were healthy after the AI cold-start warmup repair; Flyway applied V001–V010. The exact-current real-stack Playwright smoke passed, including registration, authenticated Java multipart, private Python processing, persistence/history, owner-authorized JPEG retrieval, and anonymous HTTP 403 denial. Java passed 59 tests, Python passed 22, the deterministic Playwright matrix passed 46 with 10 intentional skips, and frontend production dependencies remained at zero known npm vulnerabilities. Database-backed reviewer/admin checks, owner-scoped consent/intake, atomic claims, revocable consent, and hash-bound immutable promotion records were also added and tested. These checks close the earlier live-stack evidence gap, but the overall security label remains `PARTIAL` because the independent-repeat and online Maven/Python advisory limitations still apply.
