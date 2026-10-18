import { expect, test as base } from "@playwright/test";

interface QaFixtures {
  consoleHealth: void;
}

export const test = base.extend<QaFixtures>({
  consoleHealth: [async ({ page }, use, testInfo) => {
    const issues: string[] = [];
    page.on("console", (message) => {
      if (message.type() === "error" || message.type() === "warning") {
        if (message.type() === "warning" && message.text().includes("React Router Future Flag Warning")) return;
        issues.push(`${message.type()}: ${message.text()}`);
      }
    });
    page.on("pageerror", (error) => issues.push(`pageerror: ${error.message}`));
    await use();
    const allowed = testInfo.annotations
      .filter((annotation) => annotation.type === "expected-console-issue")
      .map((annotation) => annotation.description ?? "");
    const unexpected = issues.filter((issue) => !allowed.some((fragment) => fragment && issue.includes(fragment)));
    expect.soft(unexpected, "rendered flow emitted unexpected browser console warnings/errors").toEqual([]);
  }, { auto: true }],
});

export { expect };
