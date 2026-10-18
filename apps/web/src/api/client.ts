import { clearToken, getToken } from "../auth/tokenStore";
import type {
  AuthResponse,
  Crop,
  ErrorModel,
  IdentificationMode,
  Pest,
  PestKind,
  ReviewResponse,
  ScanResult,
  TrainingConsentResponse,
  UserProfile,
  ValidateFrameResponse,
} from "./contracts";

const configuredBase = import.meta.env.VITE_CORE_API_BASE_URL?.trim().replace(/\/$/, "") ?? "";
const API_ROOT = `${configuredBase}/api/v1`;

interface PageEnvelope<T> {
  content?: T[];
  data?: T[];
  items?: T[];
}

export class ApiError extends Error {
  readonly status: number;
  readonly code: string;
  readonly retryable: boolean;
  readonly requestId?: string;

  constructor(status: number, model?: Partial<ErrorModel>) {
    super(model?.message || `Request failed (${status})`);
    this.name = "ApiError";
    this.status = status;
    this.code = model?.code || "REQUEST_FAILED";
    this.retryable = model?.retryable ?? status >= 500;
    this.requestId = model?.requestId;
  }
}

const parseBody = async (response: Response): Promise<unknown> => {
  if (response.status === 204) return undefined;
  const contentType = response.headers.get("content-type") ?? "";
  if (!contentType.includes("application/json")) return undefined;
  return response.json();
};

const request = async <T>(path: string, init: RequestInit = {}): Promise<T> => {
  const headers = new Headers(init.headers);
  const token = getToken();
  if (token) headers.set("Authorization", `Bearer ${token}`);
  if (init.body && !(init.body instanceof FormData)) headers.set("Content-Type", "application/json");

  const response = await fetch(`${API_ROOT}${path}`, {
    ...init,
    headers,
    credentials: "include",
  });
  const body = await parseBody(response);
  if (!response.ok) {
    if (response.status === 401) clearToken();
    throw new ApiError(response.status, body as Partial<ErrorModel> | undefined);
  }
  return body as T;
};

const requestBlob = async (path: string, signal?: AbortSignal): Promise<Blob> => {
  const headers = new Headers();
  const token = getToken();
  if (token) headers.set("Authorization", `Bearer ${token}`);
  const response = await fetch(`${API_ROOT}${path}`, { headers, credentials: "include", signal });
  if (!response.ok) {
    const body = await parseBody(response);
    if (response.status === 401) clearToken();
    throw new ApiError(response.status, body as Partial<ErrorModel> | undefined);
  }
  return response.blob();
};

const list = async <T>(path: string, signal?: AbortSignal): Promise<T[]> => {
  const payload = await request<T[] | PageEnvelope<T>>(path, { signal });
  if (Array.isArray(payload)) return payload;
  return payload.content ?? payload.data ?? payload.items ?? [];
};

const form = (fields: Record<string, string>, image: Blob, filename: string): FormData => {
  const body = new FormData();
  Object.entries(fields).forEach(([key, value]) => body.append(key, value));
  body.append("image", image, filename);
  return body;
};

export const api = {
  login: (email: string, password: string, signal?: AbortSignal) =>
    request<AuthResponse>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
      signal,
    }),
  register: (fullName: string, email: string, password: string, language = "en", signal?: AbortSignal) =>
    request<AuthResponse>("/auth/register", {
      method: "POST",
      body: JSON.stringify({ fullName, email, password, language }),
      signal,
    }),
  crops: (options: { includeUnavailable?: boolean } = {}, signal?: AbortSignal) => {
    const suffix = options.includeUnavailable ? "?includeUnavailable=true" : "";
    return list<Crop>(`/crops${suffix}`, signal);
  },
  pests: (filters: { cropId?: string; kind?: PestKind } = {}, signal?: AbortSignal) => {
    const query = new URLSearchParams();
    if (filters.cropId) query.set("cropId", filters.cropId);
    if (filters.kind) query.set("kind", filters.kind);
    const suffix = query.size ? `?${query.toString()}` : "";
    return list<Pest>(`/pests${suffix}`, signal);
  },
  pest: (pestId: string, signal?: AbortSignal) =>
    request<Pest>(`/pests/${encodeURIComponent(pestId)}`, { signal }),
  scans: (signal?: AbortSignal) => list<ScanResult>("/scans", signal),
  scan: (scanId: string, signal?: AbortSignal) =>
    request<ScanResult>(`/scans/${encodeURIComponent(scanId)}`, { signal }),
  scanImage: (scanId: string, signal?: AbortSignal) =>
    requestBlob(`/scans/${encodeURIComponent(scanId)}/image`, signal),
  validateFrame: (mode: IdentificationMode, cropId: string | undefined, image: Blob, signal?: AbortSignal) =>
    request<ValidateFrameResponse>("/vision/validate-frame", {
      method: "POST",
      body: form({ mode, ...(cropId ? { cropId } : {}) }, image, "frame.jpg"),
      signal,
    }),
  createScan: (
    options: { mode: IdentificationMode; cropId?: string; trainingConsent: boolean },
    image: Blob,
    signal?: AbortSignal,
  ) =>
    request<ScanResult>("/scans", {
      method: "POST",
      body: form({
        mode: options.mode,
        trainingConsent: String(options.trainingConsent),
        ...(options.cropId ? { cropId: options.cropId } : {}),
      }, image, "capture.jpg"),
      signal,
    }),
  updateTrainingConsent: (scanId: string, trainingConsent: boolean, signal?: AbortSignal) =>
    request<TrainingConsentResponse>(`/scans/${encodeURIComponent(scanId)}/training-consent`, {
      method: "PUT",
      body: JSON.stringify({ trainingConsent }),
      signal,
    }),
  submitForReview: (scanId: string, proposedLabelSlug?: string, notes?: string, signal?: AbortSignal) =>
    request<ReviewResponse>(`/scans/${encodeURIComponent(scanId)}/review-submission`, {
      method: "POST",
      body: JSON.stringify({ proposedLabelSlug, notes }),
      signal,
    }),
  me: (signal?: AbortSignal) => request<UserProfile>("/me", { signal }),
  updateMe: (profile: Pick<UserProfile, "fullName" | "language">, signal?: AbortSignal) =>
    request<UserProfile>("/me", {
      method: "PUT",
      body: JSON.stringify(profile),
      signal,
    }),
};
