import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { IdentifyPage } from "./IdentifyPage";

const mocks = vi.hoisted(() => ({
  validation: "READY",
  crops: vi.fn(),
  pests: vi.fn(),
}));

vi.mock("../api/client", () => ({
  api: {
    crops: mocks.crops,
    pests: mocks.pests,
    validateFrame: vi.fn(),
    createScan: vi.fn(),
  },
}));

vi.mock("../features/camera/useCamera", () => ({
  useCamera: () => ({
    videoRef: { current: null },
    state: "ready",
    retry: vi.fn(),
    switchCamera: vi.fn(),
  }),
}));

vi.mock("../features/camera/useLiveValidation", () => ({
  useLiveValidation: () => mocks.validation,
}));

describe("IdentifyPage camera guide", () => {
  beforeEach(() => {
    mocks.validation = "READY";
    mocks.crops.mockReset().mockResolvedValue([
      { id: "10000000-0000-0000-0000-000000000001", slug: "rice", name: "Rice", identificationSupported: true },
    ]);
    mocks.pests.mockReset().mockResolvedValue([]);
  });

  it("renders the ROI guide and ready capture control", async () => {
    const { container } = render(<MemoryRouter><IdentifyPage /></MemoryRouter>);
    await screen.findByLabelText("Rice");
    fireEvent.click(screen.getByRole("button", { name: "Open camera" }));
    expect(container.querySelector(".roi-guide")).toBeInTheDocument();
    expect(screen.getByRole("status")).toHaveTextContent("Ready to capture");
    expect(screen.getByRole("button", { name: "Capture image" })).toBeEnabled();
  });

  it("keeps capture disabled and gives the actionable blur message", async () => {
    mocks.validation = "TOO_BLURRY";
    render(<MemoryRouter><IdentifyPage /></MemoryRouter>);
    await screen.findByLabelText("Rice");
    fireEvent.click(screen.getByRole("button", { name: "Open camera" }));
    await waitFor(() => expect(screen.getByRole("status")).toHaveTextContent("Hold the camera steady"));
    expect(screen.getByRole("button", { name: "Capture disabled until image is ready" })).toBeDisabled();
  });

  it("allows general-insect capture without selecting a crop and explains reviewed learning", async () => {
    render(<MemoryRouter initialEntries={["/identify?mode=GENERAL_INSECT"]}><IdentifyPage /></MemoryRouter>);

    expect(await screen.findByRole("radio", { name: /General insect/i })).toBeChecked();
    expect(screen.queryByRole("group", { name: "Select crop" })).not.toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Open camera" })).toBeEnabled();
    expect(screen.getByRole("checkbox", { name: /improve future models after review/i })).not.toBeChecked();
    expect(await screen.findByText(/No general-insect model is promoted yet/i)).toBeInTheDocument();
  });
});
