// types/index.ts — TypeScript interfaces mirroring all Pydantic schemas

// ── Fare ───────────────────────────────────────────────────────────────────────

export interface FareObservation {
  id:               number;
  airline:          string;
  airline_code:     string;
  source:           string;
  origin:           string;
  destination:      string;
  route_id:         number;
  observation_date: string;   // ISO date
  departure_date:   string;
  advance_days:     number;
  base_fare:        number;
  taxes:            number;
  total_fare:       number;
  currency:         string;
  scraped_at:       string;   // ISO datetime
}

export interface FareStats {
  route_id:    number;
  origin:      string;
  destination: string;
  avg_fare:    number;
  min_fare:    number;
  max_fare:    number;
  count:       number;
}

export interface FareListResponse {
  items: FareObservation[];
  total: number;
  page:  number;
  limit: number;
  pages: number;
}

// ── Index ──────────────────────────────────────────────────────────────────────

export interface IndexValue {
  id:          number;
  date:        string;
  index_value: number;
  index_type:  string;
  route_id:    number | null;
}

export interface IndexCurrentResponse {
  date:        string;
  index_value: number;
  index_type:  string;
  wow_change:  number;
  mom_change:  number;
}

export interface IndexHistoryResponse {
  items:      IndexValue[];
  start_date: string;
  end_date:   string;
  total:      number;
}

// ── Route ──────────────────────────────────────────────────────────────────────

export interface Route {
  id:          number;
  origin:      string;
  destination: string;
  distance_km: number;
  weight:      number;
}

export interface RouteDetail extends Route {
  current_index: number;
  wow_change:    number;
}

export interface RouteListResponse {
  items: RouteDetail[];
  total: number;
}

// ── Alert ──────────────────────────────────────────────────────────────────────

export type AlertSeverity = "NORMAL" | "WATCH" | "ELEVATED" | "HIGH";

export interface Alert {
  id:            number;
  severity:      AlertSeverity;
  score:         number;
  wow_change:    number;
  z_score:       number;
  anomaly_score: number;
  apix_value:    number;
  contributors:  number[];
  created_at:    string;
}

export interface ContributorDetail {
  route: string;
  contribution: number;
}

export interface AlertCurrentResponse {
  severity:      AlertSeverity;
  score:         number;
  wow_change:    number;
  z_score:       number;
  anomaly_score: number;
  forecast_deviation: number;
  apix_value:    number;
  message:       string;
  contributors_detail: ContributorDetail[];
  lead_time_pressure: Record<string, number>;
  created_at:    string;
}

export interface AlertHistoryResponse {
  items: Alert[];
  total: number;
}

// ── Metadata ───────────────────────────────────────────────────────────────────

export interface Airline {
  id:        number;
  code:      string;
  name:      string;
  iata_code: string;
}

export interface Airport {
  id:      number;
  code:    string;
  city:    string;
  country: string;
}
