// services/api.ts — Typed axios client for the Prometheus API

import axios, { AxiosInstance } from "axios";
import type {
  FareListResponse,
  FareObservation,
  FareStats,
  IndexCurrentResponse,
  IndexHistoryResponse,
  RouteListResponse,
  RouteDetail,
  AlertCurrentResponse,
  AlertHistoryResponse,
  Alert,
  Airline,
  Airport,
} from "@/types";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const http: AxiosInstance = axios.create({
  baseURL: BASE_URL,
  headers: { "Content-Type": "application/json" },
  timeout: 10_000,
});

// Global error handler
http.interceptors.response.use(
  (res) => res,
  (err) => {
    console.error("[API Error]", err?.response?.data ?? err.message);
    return Promise.reject(err);
  }
);

// ── Index ──────────────────────────────────────────────────────────────────────

export const indexApi = {
  getCurrent: () =>
    http.get<IndexCurrentResponse>("/api/index/current").then((r) => r.data),

  getHistory: (params?: { start_date?: string; end_date?: string }) =>
    http
      .get<IndexHistoryResponse>("/api/index/history", { params })
      .then((r) => r.data),

  getRouteHistory: (
    routeId: number,
    params?: { start_date?: string; end_date?: string }
  ) =>
    http
      .get<IndexHistoryResponse>(`/api/index/route/${routeId}`, { params })
      .then((r) => r.data),
};

// ── Fares ──────────────────────────────────────────────────────────────────────

export const faresApi = {
  list: (params?: {
    route_id?:   number;
    airline?:    string;
    start_date?: string;
    end_date?:   string;
    advance?:    number;
    page?:       number;
    limit?:      number;
  }) =>
    http.get<FareListResponse>("/api/fares", { params }).then((r) => r.data),

  getById: (id: number) =>
    http.get<FareObservation>(`/api/fares/${id}`).then((r) => r.data),

  getStats: () =>
    http.get<FareStats[]>("/api/fares/stats").then((r) => r.data),
};

// ── Routes ─────────────────────────────────────────────────────────────────────

export const routesApi = {
  list: () =>
    http.get<RouteListResponse>("/api/routes").then((r) => r.data),

  getByOD: (origin: string, destination: string) =>
    http
      .get<RouteDetail>(`/api/routes/${origin}/${destination}`)
      .then((r) => r.data),
};

// ── Alerts ─────────────────────────────────────────────────────────────────────

export const alertsApi = {
  getCurrent: () =>
    http.get<AlertCurrentResponse>("/api/alerts/current").then((r) => r.data),

  getHistory: (params?: {
    severity?:   string;
    start_date?: string;
    end_date?:   string;
  }) =>
    http
      .get<AlertHistoryResponse>("/api/alerts/history", { params })
      .then((r) => r.data),

  getById: (id: number) =>
    http.get<Alert>(`/api/alerts/${id}`).then((r) => r.data),
};

// ── Metadata ───────────────────────────────────────────────────────────────────

export const metadataApi = {
  getAirlines: () =>
    http.get<Airline[]>("/api/airlines").then((r) => r.data),

  getAirports: () =>
    http.get<Airport[]>("/api/airports").then((r) => r.data),
};
