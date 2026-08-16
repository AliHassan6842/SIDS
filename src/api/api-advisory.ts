import API from "./API";
const api = new API();
const base = "/api/Advisory";

export const apiGetAdvisoryByDetection = (detectionId: number) =>
  api.get(`${base}?detectionID=${detectionId}`);

export const apiGetAdvisories = () => api.get(base);
