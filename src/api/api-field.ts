import API from "./API";
import { buildQuery } from "../lib/query-builder";
import type { IField } from "../types/field/field";

const api = new API();
const base = "/api/Field";

export const apiGetFields = (filters?: Record<string, any>) =>
  api.get(`${base}${filters ? `?${buildQuery(filters)}` : ""}`);

export const apiGetFieldById = (id: number) => api.get(`${base}/${id}`);
export const apiUpsertField = (data: Partial<IField>) => api.post(base, data);
export const apiDeleteField = (id: number) => api.delete(`${base}?fieldID=${id}`);
