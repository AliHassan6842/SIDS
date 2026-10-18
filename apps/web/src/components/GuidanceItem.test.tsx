import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { GuidanceItem } from "./GuidanceItem";

describe("GuidanceItem", () => {
  it("renders Java guidance arrays as separate management steps", () => {
    render(<GuidanceItem title="Prevention" content={["Inspect leaves regularly.", "Remove crop debris."]} />);
    expect(screen.getAllByRole("listitem")).toHaveLength(2);
    expect(screen.getByText("Remove crop debris.")).toBeVisible();
  });
});
