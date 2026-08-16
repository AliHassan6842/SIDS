import API from "./API";
import { buildQuery } from "../lib/query-builder";
const api = new API();
const base = "/api/Report";

export const apiGetReportSummary = (filters?: Record<string, any>) =>
  api.get(`${base}/summary${filters ? `?${buildQuery(filters)}` : ""}`);

export const apiExportReportPDF = (filters?: Record<string, any>) =>
  api.get(`${base}/export/pdf${filters ? `?${buildQuery(filters)}` : ""}`);

export const apiExportReportExcel = (filters?: Record<string, any>) =>
  api.get(`${base}/export/excel${filters ? `?${buildQuery(filters)}` : ""}`);
