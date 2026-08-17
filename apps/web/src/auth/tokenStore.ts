const KEY = "agrosense_token";
export const setToken = (token: string) => localStorage.setItem(KEY, token);
export const getToken = (): string | null => localStorage.getItem(KEY);
export const clearToken = () => localStorage.removeItem(KEY);
