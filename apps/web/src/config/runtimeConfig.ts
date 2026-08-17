export const runtimeConfig = {
  IS_PROXY_REQUIRED: false,
  IS_SSO_REQUIRED: false,
  GATEWAY_BASE: import.meta.env.VITE_API_BASE_URL ?? "https://localhost:7012",
  API_DIRECT_BASE: "https://localhost:7220",
  AI_MODEL_BASE: import.meta.env.VITE_AI_MODEL_URL ?? "https://localhost:8000",
};
