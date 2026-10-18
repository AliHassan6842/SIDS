import { authenticate, installCameraFailure, installFakeCamera, mockApi } from "./fixtures";
import { expect, test } from "./test";

test("permission denied shows actionable camera fallback", async ({ page }) => {
  await authenticate(page);
  await installCameraFailure(page, "NotAllowedError");
  await mockApi(page);
  await page.goto("/identify");
  await page.getByRole("button", { name: "Open camera" }).click();
  await expect(page.getByRole("heading", { name: "Camera permission denied" })).toBeVisible();
  await expect(page.getByText("Allow camera access in your browser settings")).toBeVisible();
  await expect(page.getByRole("button", { name: "Try camera again" })).toBeVisible();
  await expect(page.getByText("Gallery")).toBeVisible();
});

test("missing device shows no-camera fallback", async ({ page }) => {
  await authenticate(page);
  await installCameraFailure(page, "NotFoundError");
  await mockApi(page);
  await page.goto("/identify");
  await page.getByRole("button", { name: "Open camera" }).click();
  await expect(page.getByRole("heading", { name: "No camera available" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Try camera again" })).toBeVisible();
});

test("camera reaches ready, captures, retakes, and captures again", async ({ page }) => {
  await authenticate(page);
  await installFakeCamera(page);
  await mockApi(page);
  await page.goto("/identify");
  await page.getByRole("button", { name: "Open camera" }).click();
  await expect(page.getByText("Ready to capture")).toBeVisible({ timeout: 12_000 });
  await page.getByRole("button", { name: "Capture image" }).click();
  await expect(page.getByText("Review image", { exact: true })).toBeVisible();
  await expect(page.getByAltText("Captured insect ready for review")).toBeVisible();

  await page.getByRole("button", { name: "Retake" }).click();
  await expect(page.getByText("Ready to capture")).toBeVisible({ timeout: 12_000 });
  await page.getByRole("button", { name: "Capture image" }).click();
  await expect(page.getByText("Review image", { exact: true })).toBeVisible();
});
