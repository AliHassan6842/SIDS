import { runtimeConfig } from "../config/runtimeConfig";

export const getBasePath = (): string =>
  runtimeConfig.IS_PROXY_REQUIRED
    ? runtimeConfig.GATEWAY_BASE
    : runtimeConfig.API_DIRECT_BASE;
