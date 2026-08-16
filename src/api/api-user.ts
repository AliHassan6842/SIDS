import API from "./API";
import type { IUserProfile } from "../types/user/user";
const api = new API();
const base = "/api/User";

export const apiGetProfile = () => api.get(`${base}/profile`);
export const apiUpdateProfile = (data: Partial<IUserProfile>) => api.put(`${base}/profile`, data);
export const apiChangePassword = (data: { CurrentPassword: string; NewPassword: string }) =>
  api.post(`${base}/change-password`, data);
export const apiGetAllUsers = () => api.get(`${base}/all`);
