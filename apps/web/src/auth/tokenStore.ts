const TOKEN_KEY = "sids.auth.v1";

export const getToken = (): string | null => {
  try {
    return window.localStorage.getItem(TOKEN_KEY);
  } catch {
    return null;
  }
};

export const setToken = (token: string): void => {
  window.localStorage.setItem(TOKEN_KEY, token);
};

export const clearToken = (): void => {
  window.localStorage.removeItem(TOKEN_KEY);
};
