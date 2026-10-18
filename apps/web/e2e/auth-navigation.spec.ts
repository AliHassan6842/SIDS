import { authenticate, CROP_ID, mockApi, PEST_ID } from "./fixtures";
import { expect, test } from "./test";

test("protected routes redirect to login, login restores authenticated access", async ({ page }) => {
  const authorizationHeaders: Array<string | undefined> = [];
  await mockApi(page, { onAuthorizedRequest: (header) => authorizationHeaders.push(header) });
  await page.goto("/history");
  await expect(page).toHaveURL(/\/login$/);
  await expect(page.getByRole("heading", { name: "Welcome back" })).toBeVisible();

  await page.getByLabel("Email address").fill("farmer@example.com");
  await page.getByLabel("Password").fill("valid-password-10");
  await page.getByRole("button", { name: "Sign in" }).click();

  await expect(page).toHaveURL(/\/home$/);
  await expect(page.getByRole("heading", { name: "Identify an insect" })).toBeVisible();
  expect(authorizationHeaders.some((header) => header === "Bearer e2e-test-token")).toBeTruthy();
});

test("registration creates a session and opens home", async ({ page }) => {
  await mockApi(page);
  await page.goto("/register");
  await page.getByLabel("Full name").fill("New Farmer");
  await page.getByLabel("Email address").fill("new@example.com");
  await page.getByLabel("Password", { exact: true }).fill("new-password-10");
  await page.getByLabel("Confirm password").fill("new-password-10");
  await page.getByRole("button", { name: "Create account" }).click();
  await expect(page).toHaveURL(/\/home$/);
  await expect(page.getByText("Rice leaf roller").first()).toBeVisible();
});

test("home navigation opens UUID-backed pest details and history", async ({ page }) => {
  await authenticate(page);
  await mockApi(page);
  await page.goto("/home");
  await expect(page.getByText("Rice", { exact: true }).last()).toBeVisible();

  await page.getByRole("link", { name: "Pests" }).click();
  await expect(page).toHaveURL(/\/pests$/);
  await page.getByRole("combobox", { name: "Crop" }).selectOption(CROP_ID);
  await expect(page.getByRole("link", { name: /Rice leaf roller/ })).toHaveAttribute("href", `/pests/${PEST_ID}`);
  await page.getByRole("link", { name: /Rice leaf roller/ }).click();
  await expect(page).toHaveURL(new RegExp(`/pests/${PEST_ID}$`));
  await expect(page.getByRole("heading", { name: "Possible crop damage" })).toBeVisible();

  await page.getByRole("link", { name: "History" }).click();
  await expect(page).toHaveURL(/\/history$/);
  await expect(page.getByText("Unsupported or uncertain insect")).toBeVisible();
  await expect(page.getByText("Image not suitable")).toBeVisible();
});
