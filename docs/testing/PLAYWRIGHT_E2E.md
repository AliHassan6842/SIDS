# Playwright E2E verification

The deterministic browser suite lives in `apps/web/e2e` and runs in desktop Chromium and a Pixel 5 viewport. API responses and camera states are controlled at browser boundaries; fixtures use the canonical public UUID contracts.

## Commands

```powershell
npm --prefix apps/web run e2e
npm --prefix apps/web run e2e:update
```

The suite covers protected routes, login, registration, home/navigation, permission denied, no camera, camera-ready capture and retake, gallery upload, multipart fields, identified/UNKNOWN/rejected/error results, history, UUID pest details, and desktop/mobile screenshot baselines. The multi-mode cases additionally verify five-crop capability truth, `CROP_PEST`/`GENERAL_INSECT` crop rules, an empty unpromoted general catalog, explicit general UNKNOWN results, owner isolation, consent-before-review, consent withdrawal, and farmer 403 versus reviewer queue access. Pixel 5 baselines explicitly freeze identify entry, camera ready, camera too blurry, image review, known result, unknown result with optional contribution UI, insect library, and history; login and home are frozen for both desktop and mobile.

Every mocked UI test fails on browser `console.error`, unexpected `console.warning`, or uncaught page errors. The only global allowlisted warning is React Router 6's exact `React Router Future Flag Warning` migration notice; it is a documented framework upgrade notice and does not indicate a failed user flow. A negative HTTP test may annotate its exact expected browser resource error (currently the deliberate mocked `503`) while all other console issues still fail.

## Real cross-service smoke

With PostgreSQL, Java Core API, and the private Python service running:

```powershell
npm --prefix apps/web run e2e:real
```

This separate smoke registers a real user, reads the real capability and promoted pest catalogs, and sends a generated 512×512 PNG through Java's authenticated `/api/v1/vision/validate-frame` route to the private Python service. It then creates and persists a real scan, reads the owner-authorized sanitized JPEG, verifies an anonymous image request is denied, and confirms the scan appears in PostgreSQL-backed history. It fails on an unavailable service or a Java→Python/storage/authorization contract error; it is never replaced by a mock. The exact-current post-warmup release run passed 1/1.

`SIDS_REAL_API_URL` may override the default `http://127.0.0.1:8080`.
