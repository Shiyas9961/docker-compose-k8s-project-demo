const runtimeConfig = window.__APP_CONFIG__ ?? {};

export const config = {
  apiUrl: runtimeConfig.API_URL || "http://localhost:8000",
  appName: runtimeConfig.APP_NAME || "React App",
  appEnv: runtimeConfig.APP_ENV || "development",
};