import { expect, type Page, type Route } from "@playwright/test";

export const CROP_ID = "10000000-0000-0000-0000-000000000001";
export const PEST_ID = "20000000-0000-0000-0000-000000000001";
export const WATER_WEEVIL_ID = "20000000-0000-0000-0000-000000000011";
export const KNOWN_SCAN_ID = "40000000-0000-0000-0000-000000000001";
export const UNKNOWN_SCAN_ID = "40000000-0000-0000-0000-000000000002";
export const REJECTED_SCAN_ID = "40000000-0000-0000-0000-000000000003";
export const GENERAL_SCAN_ID = "40000000-0000-0000-0000-000000000010";
export const OTHER_TENANT_SCAN_ID = "40000000-0000-0000-0000-000000000099";
export const REVIEW_ID = "50000000-0000-0000-0000-000000000010";

export const crop = { id: CROP_ID, slug: "rice", name: "Rice", imageUrl: "/catalog/crops/rice.jpg", identificationSupported: true };
export const cropCatalog = [
  crop,
  { id: "10000000-0000-0000-0000-000000000002", slug: "corn", name: "Corn", imageUrl: null, identificationSupported: false },
  { id: "10000000-0000-0000-0000-000000000003", slug: "wheat", name: "Wheat", imageUrl: null, identificationSupported: false },
  { id: "10000000-0000-0000-0000-000000000004", slug: "beet", name: "Beet", imageUrl: null, identificationSupported: false },
  { id: "10000000-0000-0000-0000-000000000005", slug: "citrus", name: "Citrus", imageUrl: null, identificationSupported: false },
];

export const pest = {
  id: PEST_ID,
  slug: "rice-leaf-roller",
  kind: "CROP_PEST",
  commonName: "Rice leaf roller",
  scientificName: "Cnaphalocrocis medinalis",
  imageUrl: "/catalog/pests/rice-leaf-roller.jpg",
  description: "A rice-feeding moth whose larvae fold leaves and feed within folded tissue.",
  affectedCrops: [crop],
  guidance: {
    damageDescription: "Larvae fold rice leaves and scrape green tissue.",
    prevention: ["Conserve spiders and other natural enemies."],
    basicManagement: ["Inspect folded leaves to confirm larvae are present."],
    expertAdviceNote: "Identification alone does not determine whether pesticide treatment is required.",
    sourceName: "IRRI Rice Knowledge Bank — Insects",
    sourceUrl: "https://www.knowledgebank.irri.org/step-by-step-production/growth/pests-and-diseases/insects",
    lastVerifiedAt: "2026-08-22",
  },
  generalGuidance: null,
};

export const waterWeevil = {
  id: WATER_WEEVIL_ID,
  slug: "rice-water-weevil",
  kind: "CROP_PEST",
  commonName: "Rice water weevil",
  scientificName: "Lissorhoptrus oryzophilus",
  imageUrl: "/catalog/pests/rice-water-weevil.jpg",
  description: "A rice pest whose adults feed on leaves and whose larvae feed on roots in flooded fields.",
  affectedCrops: [crop],
  guidance: {
    damageDescription: "Adults scar rice leaves while larvae feed on roots, which can reduce root function and plant vigor.",
    prevention: ["Inspect young rice for adult leaf scars."],
    basicManagement: ["Confirm adult leaf scars and inspect roots for larvae where feasible."],
    expertAdviceNote: "Identification alone does not determine whether pesticide treatment is required.",
    sourceName: "LSU AgCenter — Rice Water Weevil",
    sourceUrl: "https://www.lsuagcenter.com/topics/crops/rice/insects/presentations/1-rice-water-weevil",
    lastVerifiedAt: "2026-08-22",
  },
  generalGuidance: null,
};

const model = { id: "sids-pest-detector", version: "1.0.0", datasetVersion: "sids-rice-pests-v1" };
const createdAt = "2026-08-22T12:00:00Z";

export const identifiedScan = {
  id: KNOWN_SCAN_ID,
  mode: "CROP_PEST",
  crop,
  status: "IDENTIFIED",
  reason: null,
  confidence: 0.92,
  bbox: { x: 0.2, y: 0.3, width: 0.22, height: 0.18 },
  imageUrl: `/api/v1/scans/${KNOWN_SCAN_ID}/image`,
  pest,
  model,
  trainingConsent: false,
  consentedAt: null,
  reviewStatus: "NOT_SUBMITTED",
  createdAt,
};

export const unknownScan = {
  id: UNKNOWN_SCAN_ID,
  mode: "CROP_PEST",
  crop,
  status: "UNKNOWN",
  reason: "NO_DETECTION",
  confidence: null,
  bbox: null,
  imageUrl: `/api/v1/scans/${UNKNOWN_SCAN_ID}/image`,
  pest: null,
  model,
  trainingConsent: false,
  consentedAt: null,
  reviewStatus: "NOT_SUBMITTED",
  createdAt,
};

export const rejectedScan = {
  id: REJECTED_SCAN_ID,
  mode: "CROP_PEST",
  crop,
  status: "REJECTED_IMAGE",
  reason: "TOO_BLURRY",
  confidence: null,
  bbox: null,
  imageUrl: `/api/v1/scans/${REJECTED_SCAN_ID}/image`,
  pest: null,
  model,
  trainingConsent: false,
  consentedAt: null,
  reviewStatus: "NOT_SUBMITTED",
  createdAt,
};

export const generalUnknownScan = {
  id: GENERAL_SCAN_ID,
  mode: "GENERAL_INSECT",
  crop: null,
  status: "UNKNOWN",
  reason: "MODEL_UNAVAILABLE",
  confidence: null,
  bbox: null,
  imageUrl: `/api/v1/scans/${GENERAL_SCAN_ID}/image`,
  pest: null,
  model: null,
  trainingConsent: false,
  consentedAt: null,
  reviewStatus: "NOT_SUBMITTED",
  createdAt,
};

export type ScanScenario = "identified" | "unknown" | "rejected" | "general-unknown" | "server-error";

interface MockOptions {
  scanScenario?: ScanScenario;
  validationValid?: boolean;
  onAuthorizedRequest?: (authorization: string | undefined) => void;
  onScanMultipart?: (body: Buffer, contentType: string | undefined) => void;
}

const pixelPng = Buffer.from(
  "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII=",
  "base64",
);

const json = (route: Route, body: unknown, status = 200) =>
  route.fulfill({ status, contentType: "application/json", body: JSON.stringify(body) });

export async function mockApi(page: Page, options: MockOptions = {}): Promise<void> {
  let trainingConsent = false;
  let consentedAt: string | null = null;
  let reviewStatus = "NOT_SUBMITTED";
  await page.route("**/api/v1/**", async (route) => {
    const request = route.request();
    const url = new URL(request.url());
    const path = url.pathname;
    const method = request.method();
    const authorization = request.headers()["authorization"];
    if (!path.startsWith("/api/v1/auth/")) options.onAuthorizedRequest?.(authorization);

    if (path === "/api/v1/auth/login" && method === "POST") {
      return json(route, {
        token: "e2e-test-token",
        user: { id: "30000000-0000-0000-0000-000000000001", email: "farmer@example.com", fullName: "Example Farmer", language: "en" },
      });
    }
    if (path === "/api/v1/auth/register" && method === "POST") {
      return json(route, {
        token: "e2e-test-token",
        user: { id: "30000000-0000-0000-0000-000000000002", email: "new@example.com", fullName: "New Farmer", language: "en" },
      }, 201);
    }
    if (path === "/api/v1/crops" && method === "GET") {
      return json(route, url.searchParams.get("includeUnavailable") === "true" ? cropCatalog : [crop]);
    }
    if (path === "/api/v1/pests" && method === "GET") {
      if (url.searchParams.get("kind") === "GENERAL_INSECT") {
        return json(route, [
          {
            id: "20000000-0000-0000-0000-000000000021",
            slug: "beetle",
            kind: "GENERAL_INSECT",
            commonName: "Beetle",
            scientificName: "Coleoptera",
            imageUrl: null,
            description: "General beetle group.",
            affectedCrops: [],
            guidance: null,
            generalGuidance: {
              harmSummary: "Most beetles are harmless.",
              safeRemoval: ["Sweep outside."],
              seekExpertHelpWhen: ["If structural damage occurs."],
              sourceName: "University",
              sourceUrl: "https://example.edu",
              lastVerifiedAt: "2026-08-26",
            },
          }
        ]);
      }
      return json(route, [pest, waterWeevil]);
    }
    if (path === `/api/v1/crops/${CROP_ID}/pests` && method === "GET") return json(route, [pest, waterWeevil]);
    if (path === `/api/v1/pests/${PEST_ID}` && method === "GET") return json(route, pest);
    if (path === `/api/v1/pests/${WATER_WEEVIL_ID}` && method === "GET") return json(route, waterWeevil);
    if (path === "/api/v1/scans" && method === "GET") return json(route, [identifiedScan, unknownScan, rejectedScan]);
    if (path === `/api/v1/scans/${KNOWN_SCAN_ID}` && method === "GET") return json(route, identifiedScan);
    if (path === `/api/v1/scans/${UNKNOWN_SCAN_ID}` && method === "GET") return json(route, unknownScan);
    if (path === `/api/v1/scans/${REJECTED_SCAN_ID}` && method === "GET") return json(route, rejectedScan);
    if (path === `/api/v1/scans/${GENERAL_SCAN_ID}` && method === "GET") return json(route, generalUnknownScan);
    if (path === `/api/v1/scans/${OTHER_TENANT_SCAN_ID}` && method === "GET") {
      return json(route, { code: "SCAN_NOT_FOUND", message: "Scan was not found.", retryable: false, requestId: "e2e", details: {} }, 404);
    }
    if (path === `/api/v1/scans/${GENERAL_SCAN_ID}/training-consent` && method === "PUT") {
      const body = request.postDataJSON() as { trainingConsent?: boolean };
      trainingConsent = body.trainingConsent === true;
      consentedAt = trainingConsent ? "2026-08-23T12:10:00Z" : null;
      if (!trainingConsent && reviewStatus === "PENDING") reviewStatus = "REJECTED";
      return json(route, { scanId: GENERAL_SCAN_ID, trainingConsent, consentedAt, reviewStatus });
    }
    if (path === `/api/v1/scans/${GENERAL_SCAN_ID}/review-submission` && method === "POST") {
      if (!trainingConsent) {
        return json(route, { code: "TRAINING_CONSENT_REQUIRED", message: "Training consent is required.", retryable: false, requestId: "e2e", details: {} }, 409);
      }
      reviewStatus = "PENDING";
      return json(route, {
        id: REVIEW_ID,
        scanId: GENERAL_SCAN_ID,
        submittedBy: "30000000-0000-0000-0000-000000000001",
        mode: "GENERAL_INSECT",
        scanStatus: "UNKNOWN",
        proposedLabelSlug: null,
        submissionNotes: "Please review this unknown insect.",
        status: reviewStatus,
        assignedReviewerId: null,
        reviewerLabelSlug: null,
        reviewerNotes: null,
        claimedAt: null,
        reviewedAt: null,
        createdAt: "2026-08-23T12:11:00Z",
      }, 201);
    }
    if (path.startsWith("/api/v1/reviews") && authorization !== "Bearer reviewer-e2e-token") {
      return json(route, { code: "STAFF_ACCESS_REQUIRED", message: "Reviewer access is required.", retryable: false, requestId: "e2e", details: {} }, 403);
    }
    if (path === "/api/v1/reviews" && method === "GET") {
      return json(route, []);
    }
    if (path.endsWith("/image") && method === "GET") {
      return route.fulfill({ status: 200, contentType: "image/png", body: pixelPng });
    }
    if (path === "/api/v1/vision/validate-frame" && method === "POST") {
      return json(route, options.validationValid === false
        ? { valid: false, reason: "TOO_BLURRY", insectCandidate: true, quality: { brightness: "OK", blur: "LOW", subjectSize: "OK" } }
        : { valid: true, reason: null, insectCandidate: true, quality: { brightness: "OK", blur: "OK", subjectSize: "OK" } });
    }
    if (path === "/api/v1/scans" && method === "POST") {
      const body = request.postDataBuffer() ?? Buffer.alloc(0);
      options.onScanMultipart?.(body, request.headers()["content-type"]);
      const multipart = body.toString("latin1");
      const generalMode = multipart.includes('name="mode"\r\n\r\nGENERAL_INSECT');
      const cropMode = multipart.includes('name="mode"\r\n\r\nCROP_PEST') || !multipart.includes('name="mode"');
      const hasCrop = multipart.includes('name="cropId"');
      if ((generalMode && hasCrop) || (cropMode && !hasCrop)) {
        return json(route, {
          code: generalMode ? "CROP_NOT_ALLOWED" : "CROP_REQUIRED",
          message: generalMode ? "cropId must be omitted for GENERAL_INSECT." : "cropId is required for CROP_PEST.",
          retryable: false,
          requestId: "e2e",
          details: {},
        }, 400);
      }
      if (options.scanScenario === "server-error") {
        return json(route, {
          code: "AI_SERVICE_UNAVAILABLE",
          message: "Identification service is temporarily unavailable.",
          retryable: true,
          requestId: "550e8400-e29b-41d4-a716-446655440000",
          details: {},
        }, 503);
      }
      return json(route,
        options.scanScenario === "unknown" ? unknownScan
          : options.scanScenario === "rejected" ? rejectedScan
            : options.scanScenario === "general-unknown" ? generalUnknownScan
              : identifiedScan,
        201,
      );
    }
    if (path === "/api/v1/me" && method === "GET") {
      return json(route, { id: "30000000-0000-0000-0000-000000000001", email: "farmer@example.com", fullName: "Example Farmer", language: "en" });
    }
    return json(route, { code: "NOT_MOCKED", message: `${method} ${path} was not mocked`, retryable: false, requestId: "e2e", details: {} }, 500);
  });
}

export async function authenticate(page: Page): Promise<void> {
  await page.addInitScript(() => window.localStorage.setItem("sids.auth.v1", "e2e-test-token"));
}

export async function chooseTestImage(page: Page): Promise<void> {
  await page.getByLabel("Choose an insect photo from your device").setInputFiles({
    name: "rice-insect.png",
    mimeType: "image/png",
    buffer: pixelPng,
  });
  await expect(page.getByText("Review image", { exact: true })).toBeVisible();
}

export async function installCameraFailure(page: Page, name: "NotAllowedError" | "NotFoundError"): Promise<void> {
  await page.addInitScript((errorName) => {
    Object.defineProperty(navigator, "mediaDevices", {
      configurable: true,
      value: { getUserMedia: async () => { throw new DOMException("E2E camera failure", errorName); } },
    });
  }, name);
}

export async function installFakeCamera(page: Page): Promise<void> {
  await page.addInitScript(() => {
    const tracks = [{ stop: () => undefined }];
    Object.defineProperty(navigator, "mediaDevices", {
      configurable: true,
      value: { getUserMedia: async () => ({ getTracks: () => tracks }) },
    });
    Object.defineProperty(HTMLMediaElement.prototype, "srcObject", {
      configurable: true,
      get() { return (this as HTMLMediaElement & { __e2eStream?: unknown }).__e2eStream ?? null; },
      set(value) { (this as HTMLMediaElement & { __e2eStream?: unknown }).__e2eStream = value; },
    });
    HTMLMediaElement.prototype.play = async () => undefined;
    Object.defineProperty(HTMLVideoElement.prototype, "videoWidth", { configurable: true, get: () => 1280 });
    Object.defineProperty(HTMLVideoElement.prototype, "videoHeight", { configurable: true, get: () => 720 });
    CanvasRenderingContext2D.prototype.drawImage = () => undefined;
    CanvasRenderingContext2D.prototype.getImageData = function getImageData(_sx, _sy, width, height) {
      const data = new Uint8ClampedArray(width * height * 4);
      for (let y = 0; y < height; y += 1) {
        for (let x = 0; x < width; x += 1) {
          const offset = (y * width + x) * 4;
          const value = x % 2 === 0 ? 70 : 180;
          data[offset] = value;
          data[offset + 1] = value;
          data[offset + 2] = value;
          data[offset + 3] = 255;
        }
      }
      return new ImageData(data, width, height);
    };
  });
}
