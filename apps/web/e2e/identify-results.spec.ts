import {
  authenticate,
  chooseTestImage,
  CROP_ID,
  KNOWN_SCAN_ID,
  mockApi,
  PEST_ID,
  REJECTED_SCAN_ID,
  type ScanScenario,
  UNKNOWN_SCAN_ID,
} from "./fixtures";
import { expect, test } from "./test";

async function openUploadReview(page: import("@playwright/test").Page): Promise<void> {
  await page.goto("/identify");
  await expect(page.getByLabel("Rice")).toBeChecked();
  await chooseTestImage(page);
}

test("gallery identification sends canonical multipart fields and renders known result", async ({ page }) => {
  let multipartBody: Buffer = Buffer.alloc(0);
  let contentType: string | undefined;
  await authenticate(page);
  await mockApi(page, {
    scanScenario: "identified",
    onScanMultipart: (body, type) => { multipartBody = body; contentType = type; },
  });
  await openUploadReview(page);
  await page.getByRole("button", { name: "Identify", exact: true }).click();

  await expect(page).toHaveURL(new RegExp(`/result/${KNOWN_SCAN_ID}$`));
  await expect(page.getByRole("heading", { name: "Rice leaf roller" })).toBeVisible();
  await expect(page.getByText("Confidence 92%")).toBeVisible();
  await expect(page.getByLabel("Detected insect location")).toBeVisible();
  expect(contentType).toContain("multipart/form-data; boundary=");
  expect(multipartBody.toString("latin1")).toContain(`name="cropId"\r\n\r\n${CROP_ID}`);
  expect(multipartBody.toString("latin1")).toContain('name="image"; filename="capture.jpg"');

  await page.goto("/history");
  await page.getByRole("link", { name: /Rice leaf roller/ }).first().click();
  await expect(page).toHaveURL(new RegExp(`/result/${KNOWN_SCAN_ID}$`));
});

for (const scenario of [
  { name: "unknown", scenario: "unknown" as ScanScenario, scanId: UNKNOWN_SCAN_ID, heading: "Insect not identified" },
  { name: "rejected", scenario: "rejected" as ScanScenario, scanId: REJECTED_SCAN_ID, heading: "Image not suitable" },
]) {
  test(`${scenario.name} scan remains explicit and never guesses a pest`, async ({ page }) => {
    await authenticate(page);
    await mockApi(page, { scanScenario: scenario.scenario });
    await openUploadReview(page);
    await page.getByRole("button", { name: "Identify", exact: true }).click();
    await expect(page).toHaveURL(new RegExp(`/result/${scenario.scanId}$`));
    await expect(page.getByRole("heading", { name: scenario.heading })).toBeVisible();
    await expect(page.getByText("Rice leaf roller")).toHaveCount(0);
    await expect(page.getByRole("link", { name: "View supported pests" })).toHaveAttribute("href", "/pests");
  });
}

test("scan service error keeps review image and exposes retryable message", async ({ page }) => {
  test.info().annotations.push({
    type: "expected-console-issue",
    description: "Failed to load resource: the server responded with a status of 503",
  });
  await authenticate(page);
  await mockApi(page, { scanScenario: "server-error" });
  await openUploadReview(page);
  await page.getByRole("button", { name: "Identify", exact: true }).click();
  await expect(page).toHaveURL(/\/identify$/);
  await expect(page.getByRole("alert")).toHaveText("Identification service is temporarily unavailable.");
  await expect(page.getByRole("button", { name: "Identify", exact: true })).toBeEnabled();
  await expect(page.getByAltText("Captured insect ready for review")).toBeVisible();
});

test("result and pest detail requests keep public UUIDs", async ({ page }) => {
  const paths: string[] = [];
  await authenticate(page);
  await mockApi(page);
  page.on("request", (request) => paths.push(new URL(request.url()).pathname));
  await page.goto(`/result/${KNOWN_SCAN_ID}`);
  await expect(page.getByRole("heading", { name: "Rice leaf roller" })).toBeVisible();
  expect(paths).toContain(`/api/v1/scans/${KNOWN_SCAN_ID}`);
  await page.goto(`/pests/${PEST_ID}`);
  await expect(page.getByText("Cnaphalocrocis medinalis")).toBeVisible();
  expect(paths).toContain(`/api/v1/pests/${PEST_ID}`);
});
