import apiClient from './apiClient';

export async function triggerHourlyAggregation(
  hour?: string
): Promise<{ status: string; hour: string; services_aggregated: number; details: any }> {
  const params: any = {};
  if (hour) params.hour = hour;

  const response = await apiClient.post('/aggregation/trigger/hourly', null, { params });
  return response.data;
}

export async function triggerSecurityAnalysis(): Promise<{
  status: string;
  suspicious_activities_detected: number;
}> {
  const response = await apiClient.post('/aggregation/trigger/security-analysis');
  return response.data;
}

export async function triggerCleanup(
  retentionDays?: number
): Promise<{ status: string; total_deleted: number; details: any }> {
  const params: any = {};
  if (retentionDays) params.retention_days = retentionDays;

  const response = await apiClient.post('/aggregation/trigger/cleanup', null, { params });
  return response.data;
}
