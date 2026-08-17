import API from "./API";
import { buildQuery } from "../lib/query-builder";
import type { IField } from "../types/field/field";

const api = new API();

/**
 * SIDS 2026 - v1 Backend Contracts
 * Mapped to Spring Boot / FastAPI backend architecture.
 */

// --- Auth & Identity ---
export const authMe = () => api.get("/v1/me");
export const authLogin = (credentials: any) => api.post("/v1/auth/login", credentials);

// --- Farm & Field Management ---
export const getFarms = () => api.get("/v1/farms");
export const getFields = (filters?: Record<string, any>) => 
  api.get(`/v1/fields${filters ? `?${buildQuery(filters)}` : ""}`);
export const getFieldById = (id: number) => api.get(`/v1/fields/${id}`);
export const upsertField = (data: Partial<IField>) => api.post("/v1/fields", data);
export const deleteField = (id: number) => api.delete(`/v1/fields/${id}`);

// --- Core Scouting ---
export const submitQuickScan = (data: any) => api.post("/v1/observations", data);
export const submitFieldSurvey = (data: any) => api.post("/v1/surveys", data);
export const getDiagnoses = (filters?: Record<string, any>) => api.get(`/v1/diagnoses`);

// --- Offline & Sync ---
export const pushSyncQueue = (queueData: any[]) => api.post("/v1/sync", queueData);
export const getTasks = () => api.get("/v1/tasks");

// --- Agronomy ---
export const getRecommendations = (diagnosisId: string) => api.get(`/v1/recommendations?diagnosisId=${diagnosisId}`);
export const searchKnowledge = (query: string) => api.get(`/v1/knowledge/search?q=${query}`);

// --- Fallback UI Endpoints (Mocked for compilation until Backend defines them) ---
export const getAlerts = () => api.get("/v1/alerts");
export const markAllAlertsRead = () => api.post("/v1/alerts/read", {});
export const getDetectionHistory = () => api.get("/v1/history");
export const uploadPestImage = (data: any) => api.post("/v1/observations/upload", data);
export const deleteDetection = (id: number) => api.delete(`/v1/observations/${id}`);
export const getReportSummary = () => api.get("/v1/reports/summary");
export const getProfile = () => api.get("/v1/me");
export const updateProfile = (data: any) => api.put("/v1/me", data);
