import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { PestLibraryPage } from "./PestLibraryPage";

const mocks = vi.hoisted(() => ({ crops: vi.fn(), pests: vi.fn() }));

vi.mock("../api/client", () => ({ api: { crops: mocks.crops, pests: mocks.pests } }));

const cropId = "10000000-0000-0000-0000-000000000001";

describe("PestLibraryPage crop filtering", () => {
  beforeEach(() => {
    mocks.crops.mockReset().mockResolvedValue([{ id: cropId, slug: "rice", name: "Rice", identificationSupported: true }]);
    mocks.pests.mockReset().mockImplementation(async (filters: { cropId?: string }) => filters.cropId === cropId
      ? [{ id: "20000000-0000-0000-0000-000000000001", slug: "rice-leaf-roller", commonName: "Rice leaf roller", scientificName: "Cnaphalocrocis medinalis", kind: "CROP_PEST", affectedCrops: [], generalGuidance: null }]
      : []);
  });

  it("queries the canonical crop UUID and renders only returned supported pests", async () => {
    const user = userEvent.setup();
    render(<MemoryRouter><PestLibraryPage /></MemoryRouter>);
    const select = await screen.findByRole("combobox", { name: "Crop" });
    await user.selectOptions(select, cropId);
    await waitFor(() => expect(mocks.pests).toHaveBeenCalledWith({ kind: "CROP_PEST", cropId }, expect.anything()));
    expect(await screen.findByText("Rice leaf roller")).toBeInTheDocument();
    expect(screen.queryByText("Unsupported research pest")).not.toBeInTheDocument();
  });

  it("requests the general catalog without a crop and renders the honest empty state", async () => {
    const user = userEvent.setup();
    render(<MemoryRouter><PestLibraryPage /></MemoryRouter>);

    await user.click(screen.getByRole("tab", { name: "General insects" }));
    await waitFor(() => expect(mocks.pests).toHaveBeenCalledWith({ kind: "GENERAL_INSECT", cropId: undefined }, expect.anything()));
    expect(await screen.findByRole("heading", { name: "General insect catalog in review" })).toBeInTheDocument();
    expect(screen.queryByRole("combobox", { name: "Crop" })).not.toBeInTheDocument();
  });
});
