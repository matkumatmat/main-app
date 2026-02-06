import apiClient from './apiClient';

export interface MetricSnapshot {
  id: string;
  timestamp: string;
  remote_ip: string;
  request_id: string;
  method: string;
  url: string;
  status: number;
  rate_limited: boolean;
  nginx_latency_ms: number | null;
  backend_latency_ms: number | null;
  user_id: string | null;
}

export interface HourlyAggregation {
  id: string;
  hour_start: string;
  service: string;
  total_requests: number;
  successful_requests: number;
  client_errors: number;
  server_errors: number;
  rate_limited_requests: number;
  avg_nginx_latency_ms: number | null;
  avg_backend_latency_ms: number | null;
  p95_nginx_latency_ms: number | null;
  p95_backend_latency_ms: number | null;
  unique_ips: number;
}

export async function fetchMetrics(
  service: string,
  start?: string,
  end?: string,
  limit: number = 1000
): Promise<{ service: string; count: number; metrics: MetricSnapshot[] }> {
  const params: any = { service, limit };
  if (start) params.start = start;
  if (end) params.end = end;

  const response = await apiClient.get('/monitoring/metrics', { params });
  return response.data;
}

export async function fetchHourlyAggregations(
  service: string,
  start?: string,
  end?: string
): Promise<{ service: string; count: number; aggregations: HourlyAggregation[] }> {
  const params: any = { service };
  if (start) params.start = start;
  if (end) params.end = end;

  const response = await apiClient.get('/monitoring/metrics/hourly', { params });
  return response.data;
}

export async function fetchRateLimitedRequests(
  limit: number = 100
): Promise<{ count: number; rate_limited_requests: any[] }> {
  const response = await apiClient.get('/monitoring/metrics/rate-limited', {
    params: { limit }
  });
  return response.data;
}

export async function fetchErrorRequests(
  limit: number = 100
): Promise<{ count: number; error_requests: any[] }> {
  const response = await apiClient.get('/monitoring/metrics/errors', {
    params: { limit }
  });
  return response.data;
}

export async function fetchMetricsByIp(
  remoteIp: string,
  limit: number = 100
): Promise<{ remote_ip: string; count: number; metrics: any[] }> {
  const response = await apiClient.get(`/monitoring/metrics/by-ip/${remoteIp}`, {
    params: { limit }
  });
  return response.data;
}
