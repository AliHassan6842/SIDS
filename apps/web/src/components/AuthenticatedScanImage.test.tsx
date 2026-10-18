import { render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { api } from "../api/client";
import { AuthenticatedScanImage } from "./AuthenticatedScanImage";

vi.mock("../api/client", () => ({ api: { scanImage: vi.fn() } }));

describe("AuthenticatedScanImage", () => {
  beforeEach(() => {
    vi.mocked(api.scanImage).mockResolvedValue(new Blob(["jpeg"], { type: "image/jpeg" }));
    vi.stubGlobal("URL", {
      ...URL,
      createObjectURL: vi.fn(() => "blob:authorized-scan"),
      revokeObjectURL: vi.fn(),
    });
  });

  it("loads a private scan through the bearer-authenticated API client", async () => {
    const view = render(<AuthenticatedScanImage scanId="scan-123" alt="Captured insect" />);

    expect(await screen.findByRole("img", { name: "Captured insect" })).toHaveAttribute("src", "blob:authorized-scan");
    expect(api.scanImage).toHaveBeenCalledWith("scan-123", expect.any(AbortSignal));

    view.unmount();
    await waitFor(() => expect(URL.revokeObjectURL).toHaveBeenCalledWith("blob:authorized-scan"));
  });
});
