import axios, { AxiosError, AxiosRequestConfig, InternalAxiosRequestConfig } from "axios";
import { UUID } from "crypto";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Extend the config type so TS knows about our custom flag
interface RetryableRequestConfig extends InternalAxiosRequestConfig {
  _retry?: boolean;
}

const API = axios.create({
  baseURL: BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 15000, // don't let requests hang forever
});

// Separate, bare instance with NO interceptors — used only for the refresh call
// so it can never recursively trigger the 401 handler or get an Authorization
// header attached to it.
const refreshClient = axios.create({
  baseURL: BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 15000,
});

const REFRESH_URL = "/accounts/refresh";

function getAccessToken() {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("access_token");
}

function getRefreshToken() {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("refresh_token");
}

function setAccessToken(token: string) {
  localStorage.setItem("access_token", token);
}

function setAccount(accountId: string) {
  localStorage.setItem("account_id", accountId);
}

function getAccountId() {
  return localStorage.getItem("account_id");
}

function forceLogout() {
  localStorage.clear();
  if (typeof window !== "undefined") {
    // Avoid redirect loop if we're already on /login
    if (window.location.pathname !== "/login") {
      window.location.href = "/login";
    }
  }
}

// --- request interceptor: attach access token ---
API.interceptors.request.use((config) => {
  const token = getAccessToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// --- refresh queueing state ---
// While a refresh is in flight, every other 401'd request awaits this
// same promise instead of firing its own refresh call.
let refreshPromise: Promise<string> | null = null;

function refreshAccessToken(): Promise<string> {
  if (refreshPromise) {
    return refreshPromise;
  }

  const refreshToken = getRefreshToken();
  if (!refreshToken) {
    forceLogout();
    return Promise.reject(new Error("No refresh token available"));
  }

  refreshPromise = refreshClient
    .post(REFRESH_URL, { refresh_token: refreshToken })
    .then((res) => {
        const { access_token, account_id } = res.data;
        console.log("refresh token theke bolchi",res.data);

        if (!access_token) {
            throw new Error("Refresh response missing access_token");
        }

        setAccessToken(access_token);

        if (account_id) {
            setAccount(account_id);
        }

        return access_token;
    })
    .catch((err) => {
      forceLogout();
      throw err;
    })
    .finally(() => {
      // Clear so the *next* 401 (after this token also expires) can refresh again
      refreshPromise = null;
    });

  return refreshPromise;
}

// --- response interceptor: handle 401 → refresh → retry once ---
API.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as RetryableRequestConfig | undefined;

    if (!originalRequest) {
      return Promise.reject(error);
    }

    // Don't try to "refresh" the refresh call itself, and don't retry
    // a request more than once.
    const isRefreshCall = originalRequest.url?.includes(REFRESH_URL);

    if (error.response?.status === 401 && !originalRequest._retry && !isRefreshCall) {
      originalRequest._retry = true;

      try {
        const newAccessToken = await refreshAccessToken();
        originalRequest.headers = originalRequest.headers ?? {};
        originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
        return API(originalRequest);
      } catch (refreshError) {
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default API;