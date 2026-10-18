import {
  authenticate,
  chooseTestImage,
  installFakeCamera,
  KNOWN_SCAN_ID,
  mockApi,
  UNKNOWN_SCAN_ID,
} from "./fixtures";
import type { Page } from "@playwright/test";
import { expect, test } from "./test";

async function expectActiveNavigation(page: Page, index: number, label: string) {
  const navigation = page.getByRole("navigation", { name: "Main navigation" });
  await expect(navigation).toHaveAttribute("data-active-index", String(index));
  await expect(navigation.getByRole("link", { name: label, exact: true })).toHaveAttribute("aria-current", "page");
}

test("login visual baseline", async ({ page }) => {
  await mockApi(page);
  await page.goto("/login");
  await expect(page.getByRole("heading", { name: "Welcome back" })).toBeVisible();
  await expect(page).toHaveScreenshot("login.png", { fullPage: false });
});

test("authenticated home visual baseline", async ({ page }) => {
  await authenticate(page);
  await mockApi(page);
  await page.goto("/home");
  await expect(page.getByText("Rice leaf roller").first()).toBeVisible();
  await expectActiveNavigation(page, 0, "Home");
  await expect(page).toHaveScreenshot("home.png", { fullPage: false });
});

test.describe("Pixel 5 workflow visual baselines", () => {
  test.beforeEach(async ({ page }, testInfo) => {
    test.skip(
      testInfo.project.name !== "mobile-chromium",
      "Workflow baselines are intentionally frozen at the Pixel 5 viewport.",
    );
    await authenticate(page);
  });

  test("identify camera entry visual baseline", async ({ page }) => {
    await mockApi(page);
    await page.goto("/identify");
    await expect(page.getByRole("heading", { name: "What are you scanning?" })).toBeVisible();
    await expectActiveNavigation(page, 1, "Identify");
    await expect(page).toHaveScreenshot("identify-camera.png");
  });

  test("identify general insect selection visual baseline", async ({ page }) => {
    await mockApi(page);
    await page.goto("/identify");
    await page.getByText("General insect").click();
    await expect(page.getByText("Currently supported groups")).toBeVisible();
    await expect(page).toHaveScreenshot("identify-general-insect-selection.png");
  });

  test("camera ready visual baseline", async ({ page }) => {
    await installFakeCamera(page);
    await mockApi(page);
    await page.goto("/identify");
    await page.getByRole("button", { name: "Open camera" }).click();
    await expect(page.getByText("Ready to capture")).toBeVisible({ timeout: 12_000 });
    await expectActiveNavigation(page, 1, "Identify");
    await expect(page).toHaveScreenshot("camera-ready.png");
  });

  test("camera too blurry visual baseline", async ({ page }) => {
    await installFakeCamera(page);
    await mockApi(page, { validationValid: false });
    await page.goto("/identify");
    await page.getByRole("button", { name: "Open camera" }).click();
    await expect(page.getByText("Hold the camera steady")).toBeVisible({ timeout: 12_000 });
    await expectActiveNavigation(page, 1, "Identify");
    await expect(page).toHaveScreenshot("camera-too-blurry.png");
  });

  test("image review visual baseline", async ({ page }) => {
    await mockApi(page);
    await page.goto("/identify");
    await chooseTestImage(page);
    await expectActiveNavigation(page, 1, "Identify");
    await expect(page).toHaveScreenshot("image-review.png");
  });

  test("known pest result visual baseline", async ({ page }) => {
    await mockApi(page);
    await page.goto(`/result/${KNOWN_SCAN_ID}`);
    await expect(page.getByRole("heading", { name: "Rice leaf roller" })).toBeVisible();
    await expectActiveNavigation(page, 1, "Identify");
    await expect(page).toHaveScreenshot("result-known-pest.png");
  });

  test("unknown result visual baseline", async ({ page }) => {
    await mockApi(page);
    await page.goto(`/result/${UNKNOWN_SCAN_ID}`);
    await expect(page.getByRole("heading", { name: "Insect not identified" })).toBeVisible();
    await expectActiveNavigation(page, 1, "Identify");
    await expect(page).toHaveScreenshot("result-unknown.png");
  });

  test("pest library visual baseline", async ({ page }) => {
    await mockApi(page);
    await page.goto("/pests");
    await expect(page.getByRole("heading", { name: "Insect library" })).toBeVisible();
    await expect(page.getByText("Rice leaf roller")).toBeVisible();
    await expectActiveNavigation(page, 2, "Pests");
    await expect(page).toHaveScreenshot("pest-library.png");
  });

  test("history visual baseline", async ({ page }) => {
    await mockApi(page);
    await page.goto("/history");
    await expect(page.getByRole("heading", { name: "Scan history" })).toBeVisible();
    await expect(page.getByText("Unsupported or uncertain insect")).toBeVisible();
    await expectActiveNavigation(page, 3, "History");
    await expect(page).toHaveScreenshot("history.png");
  });
});
