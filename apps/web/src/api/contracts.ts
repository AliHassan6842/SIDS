export type ScanStatus = "IDENTIFIED" | "UNKNOWN" | "REJECTED_IMAGE" | "FAILED";
export type IdentificationMode = "CROP_PEST" | "GENERAL_INSECT";
export type PestKind = "CROP_PEST" | "GENERAL_INSECT";
export type TrainingReviewStatus = "NOT_SUBMITTED" | "PENDING" | "APPROVED" | "REJECTED";

export type ValidationReason =
  | "TOO_DARK"
  | "TOO_BRIGHT"
  | "TOO_BLURRY"
  | "SUBJECT_TOO_SMALL"
  | "NO_INSECT_CANDIDATE"
  | "INVALID_IMAGE";

export interface BoundingBox {
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface Crop {
  id: string;
  slug: string;
  name: string;
  imageUrl?: string | null;
  supported?: boolean;
  identificationSupported: boolean;
}

export interface PestGuidance {
  damageDescription?: string | null;
  prevention?: string[] | null;
  basicManagement?: string[] | null;
  expertAdviceNote?: string | null;
  sourceName?: string | null;
  sourceUrl?: string | null;
  lastVerifiedAt?: string | null;
}

export interface GeneralInsectGuidance {
  harmSummary: string | null;
  safeRemoval: string[];
  seekExpertHelpWhen: string[];
  sourceName: string;
  sourceUrl: string;
  lastVerifiedAt: string;
}

export interface Pest {
  id: string;
  slug: string;
  commonName: string;
  scientificName: string | null;
  description?: string | null;
  imageUrl?: string | null;
  supported?: boolean;
  kind: PestKind;
  affectedCrops: Crop[];
  guidance?: PestGuidance | null;
  generalGuidance: GeneralInsectGuidance | null;
}

export interface ScanResult {
  id: string;
  mode: IdentificationMode;
  crop: Crop | null;
  status: ScanStatus;
  reason: string | null;
  confidence: number | null;
  bbox: BoundingBox | null;
  imageUrl: string | null;
  pest: Pest | null;
  model: {
    id: string;
    version: string;
    datasetVersion: string;
  } | null;
  trainingConsent: boolean;
  consentedAt: string | null;
  reviewStatus: TrainingReviewStatus;
  createdAt: string;
}

export interface ValidateFrameResponse {
  valid: boolean;
  reason: ValidationReason | null;
  insectCandidate: boolean;
  quality: {
    brightness: "LOW" | "OK" | "HIGH";
    blur: "LOW" | "OK";
    subjectSize: "LOW" | "OK" | "UNKNOWN";
  };
}

export interface TrainingConsentResponse {
  scanId: string;
  trainingConsent: boolean;
  consentedAt: string | null;
  reviewStatus: TrainingReviewStatus;
}

export interface ReviewResponse {
  id: string;
  scanId: string;
  submittedBy: string;
  mode: IdentificationMode;
  scanStatus: ScanStatus;
  proposedLabelSlug: string | null;
  submissionNotes: string | null;
  status: TrainingReviewStatus;
  assignedReviewerId: string | null;
  reviewerLabelSlug: string | null;
  reviewerNotes: string | null;
  claimedAt: string | null;
  reviewedAt: string | null;
  createdAt: string;
}

export interface UserProfile {
  id: string;
  fullName: string;
  email: string;
  language: string;
}

export interface AuthResponse {
  token: string;
  user: UserProfile;
}

export interface ErrorModel {
  code: string;
  message: string;
  retryable: boolean;
  requestId: string;
  details: Record<string, unknown>;
}
