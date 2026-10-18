import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { LiveValidationStatus } from "./LiveValidationStatus";

describe("LiveValidationStatus", () => {
  it("announces the ready state", () => {
    render(<LiveValidationStatus state="READY" />);
    expect(screen.getByRole("status")).toHaveTextContent("Ready to capture");
  });

  it("gives an actionable blur message", () => {
    render(<LiveValidationStatus state="TOO_BLURRY" />);
    expect(screen.getByRole("status")).toHaveTextContent("Hold the camera steady");
  });
});
