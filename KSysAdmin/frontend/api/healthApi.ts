import apiClient from './apiClient';

export interface SystemHealthSnapshot {
  id: string;
  timestamp: string;
  db_status: string;
  db_latency_ms: number | null;
  redis_status: string;
  redis_latency_ms: number | null;
  crypto_status: string;
}

export interface HealthAnalysis {
  total_snapshots: number;
  db_uptime_percentage: number;
  redis_uptime_percentage: number;
  crypto_uptime_percentage: number;
  avg_db_latency_ms: number;
  avg_redis_latency_ms: number;
  max_db_latency_ms: number;
  max_redis_latency_ms: number;
}

export async function fetchLatestHealthSnapshots(
  limit: number = 10
): Promise<{ count: number; snapshots: SystemHealthSnapshot[] }> {
  const response = await apiClient.get('/health-monitoring/snapshots/latest', {
    params: { limit }
  });
  return response.data;
}

export async function fetchHealthHistory(
  start: string,
  end: string,
  limit: number = 1000
): Promise<{ start: string; end: string; count: number; snapshots: SystemHealthSnapshot[] }> {
  const response = await apiClient.get('/health-monitoring/snapshots/history', {
    params: { start, end, limit }
  });
  return response.data;
}

export async function fetchHealthAnalysis(
  start: string,
  end: string
): Promise<{ time_range: { start: string; end: string }; analysis: HealthAnalysis }> {
  const response = await apiClient.get('/health-monitoring/analysis', {
    params: { start, end }
  });
  return response.data;
}
