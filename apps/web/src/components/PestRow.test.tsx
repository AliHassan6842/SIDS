import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";
import type { Pest } from "../api/contracts";
import { PestRow } from "./PestRow";

describe("PestRow", () => {
  it("uses the public UUID identifier in the pest details route", () => {
    const pest: Pest = {
      id: "20000000-0000-0000-0000-000000000001",
      slug: "rice-leaf-roller",
      commonName: "Rice leaf roller",
      scientificName: "Cnaphalocrocis medinalis",
      kind: "CROP_PEST",
      affectedCrops: [],
      generalGuidance: null,
    };

    const { container } = render(<MemoryRouter><PestRow pest={pest} /></MemoryRouter>);

    expect(screen.getByRole("link", { name: /rice leaf roller/i })).toHaveAttribute(
      "href",
      "/pests/20000000-0000-0000-0000-000000000001",
    );
    expect(container.querySelector("img")).toBeNull();
  });

  it("renders the catalog image reference returned by the API", () => {
    const pest: Pest = {
      id: "20000000-0000-0000-0000-000000000001",
      slug: "rice-leaf-roller",
      commonName: "Rice leaf roller",
      scientificName: "Cnaphalocrocis medinalis",
      imageUrl: "/catalog/pests/rice-leaf-roller.jpg",
      kind: "CROP_PEST",
      affectedCrops: [],
      generalGuidance: null,
    };

    const { container } = render(<MemoryRouter><PestRow pest={pest} /></MemoryRouter>);

    expect(container.querySelector("img")).toHaveAttribute(
      "src",
      "/catalog/pests/rice-leaf-roller.jpg",
    );
  });
});
