import API from "./API";
import type { IAlertSettings } from "../types/alert/alert";
const api = new API();
const base = "/api/Alert";

export const apiGetAlerts = () => api.get(base);
export const apiMarkAlertRead = (id: number) => api.post(`${base}/read`, { AlertID: id });
export const apiMarkAllAlertsRead = () => api.post(`${base}/read-all`, {});
export const apiGetAlertSettings = () => api.get(`${base}/settings`);
export const apiUpdateAlertSettings = (settings: IAlertSettings) =>
  api.post(`${base}/settings`, settings);
