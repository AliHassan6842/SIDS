import {
  authenticate,
  cropCatalog,
  GENERAL_SCAN_ID,
  generalUnknownScan,
  mockApi,
  OTHER_TENANT_SCAN_ID,
  REVIEW_ID,
} from "./fixtures";
import { expect, test } from "./test";

test("catalog exposes five crop capabilities without promoting unsupported models", async ({ page }) => {
  await authenticate(page);
  await mockApi(page);
  await page.goto("/home");

  const payload = await page.evaluate(async () => {
    const response = await fetch("/api/v1/crops?includeUnavailable=true", {
      headers: { Authorization: "Bearer e2e-test-token" },
    });
    return { status: response.status, body: await response.json() };
  });

  expect(payload.status).toBe(200);
  expect(payload.body).toEqual(cropCatalog);
  expect(payload.body.filter((entry: { identificationSupported: boolean }) => entry.identificationSupported))
    .toEqual([cropCatalog[0]]);
});

test("general catalog contains promoted insects and general scan returns prediction if confident", async ({ page }) => {
  let multipartBody = "";
  await authenticate(page);
  await mockApi(page, {
    scanScenario: "general-unknown", // still mocking a scan that might be unknown
    onScanMultipart: (body) => { multipartBody = body.toString("latin1"); },
  });
  await page.goto("/home");

  const generalCatalog = await page.evaluate(async () => {
    const response = await fetch("/api/v1/pests?kind=GENERAL_INSECT", {
      headers: { Authorization: "Bearer e2e-test-token" },
    });
    return response.json();
  });
  expect(generalCatalog.length).toBeGreaterThan(0);
  expect(generalCatalog[0].slug).toBe("beetle");

  const result = await page.evaluate(async () => {
    const body = new FormData();
    body.set("mode", "GENERAL_INSECT");
    body.set("trainingConsent", "false");
    body.set("image", new File([new Uint8Array([137, 80, 78, 71])], "general.png", { type: "image/png" }));
    const response = await fetch("/api/v1/scans", {
      method: "POST",
      headers: { Authorization: "Bearer e2e-test-token" },
      body,
    });
    return { status: response.status, body: await response.json() };
  });

  expect(result).toEqual({ status: 201, body: generalUnknownScan });
  expect(multipartBody).toContain('name="mode"\r\n\r\nGENERAL_INSECT');
  expect(multipartBody).toContain('name="trainingConsent"\r\n\r\nfalse');
  expect(multipartBody).not.toContain('name="cropId"');
  expect(result.body.pest).toBeNull();
  expect(result.body.model).toBeNull();
});

test("mode and crop multipart rules reject ambiguous requests", async ({ page }) => {
  test.info().annotations.push(
    { type: "expected-console-issue", description: "Failed to load resource: the server responded with a status of 400" },
  );
  await authenticate(page);
  await mockApi(page);
  await page.goto("/home");

  const statuses = await page.evaluate(async () => {
    const submit = async (mode: "CROP_PEST" | "GENERAL_INSECT", cropId?: string) => {
      const body = new FormData();
      body.set("mode", mode);
      body.set("trainingConsent", "false");
      if (cropId) body.set("cropId", cropId);
      body.set("image", new File([new Uint8Array([137, 80, 78, 71])], "insect.png", { type: "image/png" }));
      return (await fetch("/api/v1/scans", {
        method: "POST",
        headers: { Authorization: "Bearer e2e-test-token" },
        body,
      })).status;
    };
    return [
      await submit("GENERAL_INSECT", "10000000-0000-0000-0000-000000000001"),
      await submit("CROP_PEST"),
    ];
  });
  expect(statuses).toEqual([400, 400]);
});

test("consent is explicit, review is separate, and owner isolation is closed", async ({ page }) => {
  test.info().annotations.push(
    { type: "expected-console-issue", description: "Failed to load resource: the server responded with a status of 409" },
    { type: "expected-console-issue", description: "Failed to load resource: the server responded with a status of 404" },
  );
  await authenticate(page);
  await mockApi(page);
  await page.goto("/home");

  const beforeConsent = await page.evaluate(async (scanId) => {
    const response = await fetch(`/api/v1/scans/${scanId}/review-submission`, {
      method: "POST",
      headers: { Authorization: "Bearer e2e-test-token", "Content-Type": "application/json" },
      body: JSON.stringify({ notes: "Please review this unknown insect." }),
    });
    return response.status;
  }, GENERAL_SCAN_ID);
  expect(beforeConsent).toBe(409);

  const consented = await page.evaluate(async (scanId) => {
    const response = await fetch(`/api/v1/scans/${scanId}/training-consent`, {
      method: "PUT",
      headers: { Authorization: "Bearer e2e-test-token", "Content-Type": "application/json" },
      body: JSON.stringify({ trainingConsent: true }),
    });
    return response.json();
  }, GENERAL_SCAN_ID);
  expect(consented).toEqual(expect.objectContaining({ trainingConsent: true, reviewStatus: "NOT_SUBMITTED" }));

  const submission = await page.evaluate(async (scanId) => {
    const response = await fetch(`/api/v1/scans/${scanId}/review-submission`, {
      method: "POST",
      headers: { Authorization: "Bearer e2e-test-token", "Content-Type": "application/json" },
      body: JSON.stringify({ notes: "Please review this unknown insect." }),
    });
    return { status: response.status, body: await response.json() };
  }, GENERAL_SCAN_ID);
  expect(submission).toEqual(expect.objectContaining({ status: 201 }));
  expect(submission.body.status).toBe("PENDING");

  const otherTenant = await page.evaluate(async (scanId) => {
    const response = await fetch(`/api/v1/scans/${scanId}`, {
      headers: { Authorization: "Bearer e2e-test-token" },
    });
    return response.status;
  }, OTHER_TENANT_SCAN_ID);
  expect(otherTenant).toBe(404);
});

test("result UI requires separate consent before expert review and reflects withdrawal", async ({ page }) => {
  await authenticate(page);
  await mockApi(page);
  await page.goto(`/result/${GENERAL_SCAN_ID}`);

  const consent = page.getByRole("checkbox", { name: "Allow this image to be considered after expert review" });
  const submit = page.getByRole("button", { name: "Submit for expert review" });
  await expect(consent).not.toBeChecked();
  await expect(submit).toBeDisabled();

  await consent.click();
  await expect(page.getByRole("status")).toHaveText("Consent saved. You can now submit this scan for review.");
  await expect(submit).toBeEnabled();
  await submit.click();
  await expect(page.getByText("Review status: Pending")).toBeVisible();
  await expect(page.getByRole("status")).toHaveText("Submitted for expert review. It will not enter training unless a reviewer approves it.");

  await consent.click();
  await expect(page.getByText("Review status: Rejected")).toBeVisible();
  await expect(page.getByRole("status")).toHaveText("Consent withdrawn. This image will not be used for future training.");
});

test("review queue, claim, decision, and image are closed to farmer tokens", async ({ page }) => {
  test.info().annotations.push(
    { type: "expected-console-issue", description: "Failed to load resource: the server responded with a status of 403" },
  );
  await authenticate(page);
  await mockApi(page);
  await page.goto("/home");

  const farmerStatuses = await page.evaluate(async (reviewId) => Promise.all([
    fetch("/api/v1/reviews?status=PENDING", {
      headers: { Authorization: "Bearer e2e-test-token" },
    }),
    fetch(`/api/v1/reviews/${reviewId}/claim`, {
      method: "POST",
      headers: { Authorization: "Bearer e2e-test-token" },
    }),
    fetch(`/api/v1/reviews/${reviewId}/decision`, {
      method: "POST",
      headers: { Authorization: "Bearer e2e-test-token", "Content-Type": "application/json" },
      body: JSON.stringify({ decision: "REJECTED", notes: "Not suitable." }),
    }),
    fetch(`/api/v1/reviews/${reviewId}/image`, {
      headers: { Authorization: "Bearer e2e-test-token" },
    }),
  ]).then((responses) => responses.map((response) => response.status)), REVIEW_ID);
  expect(farmerStatuses).toEqual([403, 403, 403, 403]);

  const reviewer = await page.evaluate(async () => {
    const response = await fetch("/api/v1/reviews?status=PENDING", {
      headers: { Authorization: "Bearer reviewer-e2e-token" },
    });
    return { status: response.status, body: await response.json() };
  });
  expect(reviewer).toEqual({ status: 200, body: [] });
});
