import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";
import { api } from "../api/client";
import type { ScanResult } from "../api/contracts";
import { ResultPage } from "./ResultPage";

vi.mock("../api/client", () => ({ api: { scan: vi.fn(), pest: vi.fn(), updateTrainingConsent: vi.fn(), submitForReview: vi.fn() } }));

const crop = { id: "10000000-0000-0000-0000-000000000001", slug: "rice", name: "Rice", identificationSupported: true };
const model = { id: "sids-pest-detector", version: "1.0.0", datasetVersion: "sids-rice-pests-v1" };

const known: ScanResult = {
  id: "40000000-0000-0000-0000-000000000001",
  mode: "CROP_PEST",
  crop,
  status: "IDENTIFIED",
  reason: null,
  confidence: 0.92,
  bbox: { x: 0.2, y: 0.3, width: 0.22, height: 0.18 },
  imageUrl: null,
  pest: {
    id: "20000000-0000-0000-0000-000000000001",
    slug: "rice-leaf-roller",
    commonName: "Rice leaf roller",
    scientificName: "Cnaphalocrocis medinalis",
    description: "A supported rice pest.",
    kind: "CROP_PEST",
    affectedCrops: [crop],
    generalGuidance: null,
    guidance: {
      damageDescription: "Larvae fold leaves.",
      prevention: ["Conserve natural enemies."],
      basicManagement: ["Inspect folded leaves."],
      sourceName: "IRRI",
      sourceUrl: "https://example.test/irri",
    },
  },
  model,
  trainingConsent: false,
  consentedAt: null,
  reviewStatus: "NOT_SUBMITTED",
  createdAt: "2026-08-22T12:00:00Z",
};

const unknown: ScanResult = {
  ...known,
  id: "40000000-0000-0000-0000-000000000002",
  status: "UNKNOWN",
  reason: "NO_DETECTION",
  confidence: null,
  bbox: null,
  pest: null,
};

const generalInsect: ScanResult = {
  ...known,
  id: "40000000-0000-0000-0000-000000000003",
  mode: "GENERAL_INSECT",
  crop: null,
  pest: {
    id: "20000000-0000-0000-0000-000000000099",
    slug: "house-mosquito",
    commonName: "House mosquito",
    scientificName: "Culex pipiens",
    description: "A reviewed common mosquito class.",
    kind: "GENERAL_INSECT",
    affectedCrops: [],
    guidance: null,
    generalGuidance: {
      harmSummary: "Some mosquitoes can bite and may transmit disease.",
      safeRemoval: ["Use window screens and remove standing water."],
      seekExpertHelpWhen: ["Seek medical advice after a severe reaction."],
      sourceName: "Reviewed public-health source",
      sourceUrl: "https://example.test/mosquito",
      lastVerifiedAt: "2026-08-23",
    },
  },
};

function renderResult(scan: ScanResult) {
  return render(
    <MemoryRouter initialEntries={[{ pathname: `/result/${scan.id}`, state: { scan } }] }>
      <Routes><Route path="/result/:scanId" element={<ResultPage />} /></Routes>
    </MemoryRouter>,
  );
}

describe("ResultPage", () => {
  it("renders a known pest with bounded evidence and Java guidance", () => {
    renderResult(known);
    expect(screen.getByRole("heading", { name: "Rice leaf roller" })).toBeInTheDocument();
    expect(screen.getByText("Confidence 92%")).toBeInTheDocument();
    expect(screen.getByLabelText("Detected insect location")).toBeInTheDocument();
    expect(screen.getByText("Conserve natural enemies.")).toBeInTheDocument();
    expect(screen.getByText(/Identification alone does not determine/)).toBeInTheDocument();
  });

  it("renders UNKNOWN without leaking a fallback pest", () => {
    renderResult(unknown);
    expect(screen.getByRole("heading", { name: "Insect not identified" })).toBeInTheDocument();
    expect(screen.getByText(/does not guess unsupported insects/)).toBeInTheDocument();
    expect(screen.queryByText("Rice leaf roller")).not.toBeInTheDocument();
  });

  it("renders Java-owned general insect harm and safe-removal guidance", () => {
    renderResult(generalInsect);
    expect(screen.getByRole("heading", { name: "House mosquito" })).toBeInTheDocument();
    expect(screen.getByText("Some mosquitoes can bite and may transmit disease.")).toBeInTheDocument();
    expect(screen.getByText("Use window screens and remove standing water.")).toBeInTheDocument();
    expect(screen.queryByText("Possible crop damage")).not.toBeInTheDocument();
    expect(screen.getByText(/Do not touch or handle an insect/)).toBeInTheDocument();
  });

  it("keeps consent separate from expert review submission", async () => {
    vi.mocked(api.updateTrainingConsent).mockResolvedValue({
      scanId: unknown.id,
      trainingConsent: true,
      consentedAt: "2026-08-23T12:00:00Z",
      reviewStatus: "NOT_SUBMITTED",
    });
    vi.mocked(api.submitForReview).mockResolvedValue({
      id: "50000000-0000-0000-0000-000000000001",
      scanId: unknown.id,
      submittedBy: "30000000-0000-0000-0000-000000000001",
      mode: "CROP_PEST",
      scanStatus: "UNKNOWN",
      proposedLabelSlug: null,
      submissionNotes: null,
      status: "PENDING",
      assignedReviewerId: null,
      reviewerLabelSlug: null,
      reviewerNotes: null,
      claimedAt: null,
      reviewedAt: null,
      createdAt: "2026-08-23T12:01:00Z",
    });
    renderResult(unknown);

    const consent = screen.getByRole("checkbox", { name: /Allow this image/ });
    const submit = screen.getByRole("button", { name: "Submit for expert review" });
    expect(submit).toBeDisabled();
    fireEvent.click(consent);
    await waitFor(() => expect(api.updateTrainingConsent).toHaveBeenCalledWith(unknown.id, true));
    await waitFor(() => expect(submit).toBeEnabled());
    fireEvent.click(submit);
    await waitFor(() => expect(api.submitForReview).toHaveBeenCalledWith(unknown.id, undefined));
    expect(await screen.findByText("Review status: pending")).toBeInTheDocument();
  });
});
