import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";
import { AppShell } from "./AppShell";

describe("AppShell", () => {
  it.each([
    ["/home", "0", "Home"],
    ["/identify", "1", "Identify"],
    ["/identify?mode=GENERAL_INSECT", "2", "General"],
    ["/result/scan-id", "1", "Identify"],
    ["/pests/pest-id", "3", "Pests"],
    ["/history", "4", "History"],
    ["/profile", "5", "Profile"],
  ])("positions the menu indicator for %s", (path, activeIndex, activeLabel) => {
    render(<MemoryRouter initialEntries={[path]}><AppShell /></MemoryRouter>);

    expect(screen.getByRole("navigation", { name: "Main navigation" })).toHaveAttribute(
      "data-active-index",
      activeIndex,
    );
    expect(screen.getByRole("link", { name: activeLabel })).toHaveAttribute("aria-current", "page");
  });
});
