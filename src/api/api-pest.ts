import API from "./API";
import { buildQuery } from "../lib/query-builder";
import type { IDetectionFilters } from "../types/pest/pest";

const api = new API();
const base = "/api/Detection";

export const apiGetDetectionHistory = (filters?: IDetectionFilters) =>
  api.get(`${base}${filters ? `?${buildQuery(filters as Record<string, any>)}` : ""}`);

export const apiUploadPestImage = (formData: FormData) =>
  api.postForm(`${base}/analyze`, formData);

export const apiGetDetectionById = (id: number) =>
  api.get(`${base}/${id}`);

export const apiUpdateDetectionStatus = (id: number, status: string) =>
  api.post(`${base}/status`, { DetectionID: id, Status: status });

export const apiDeleteDetection = (id: number) =>
  api.delete(`${base}?detectionID=${id}`);
