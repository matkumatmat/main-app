import apiClient from './apiClient';

export interface SuspiciousActivity {
  id: string;
  timestamp: string;
  remote_ip: string;
  activity_type: string;
  severity: string;
  details: any;
}

export interface RateLimitViolation {
  id: string;
  timestamp: string;
  service: string;
  remote_ip: string;
  violation_count: number;
  user_id: string | null;
}

export interface ThreatAssessment {
  threat_level: string;
  total_activities: number;
  critical_count: number;
  high_count: number;
  medium_count: number;
  low_count: number;
  high_risk_ips: string[];
  recommendations: string[];
}

export async function fetchRecentSuspiciousActivities(
  limit: number = 50
): Promise<{ count: number; activities: SuspiciousActivity[] }> {
  const response = await apiClient.get('/security/suspicious-activities/recent', {
    params: { limit }
  });
  return response.data;
}

export async function fetchSuspiciousActivitiesByIp(
  remoteIp: string,
  limit: number = 100
): Promise<{ remote_ip: string; count: number; activities: SuspiciousActivity[] }> {
  const response = await apiClient.get(`/security/suspicious-activities/by-ip/${remoteIp}`, {
    params: { limit }
  });
  return response.data;
}

export async function fetchSuspiciousActivitiesBySeverity(
  severity: string,
  limit: number = 100
): Promise<{ severity: string; count: number; activities: SuspiciousActivity[] }> {
  const response = await apiClient.get(`/security/suspicious-activities/by-severity/${severity}`, {
    params: { limit }
  });
  return response.data;
}

export async function fetchThreatAssessment(
  start?: string,
  limit: number = 100
): Promise<{ assessment: ThreatAssessment; analyzed_activities: number }> {
  const params: any = { limit };
  if (start) params.start = start;

  const response = await apiClient.get('/security/suspicious-activities/threat-assessment', {
    params
  });
  return response.data;
}

export async function fetchRecentRateLimitViolations(
  limit: number = 50
): Promise<{ count: number; violations: RateLimitViolation[] }> {
  const response = await apiClient.get('/security/rate-limit-violations/recent', {
    params: { limit }
  });
  return response.data;
}

export async function fetchRateLimitViolationsByIp(
  remoteIp: string,
  limit: number = 100
): Promise<{ remote_ip: string; count: number; violations: RateLimitViolation[] }> {
  const response = await apiClient.get(`/security/rate-limit-violations/by-ip/${remoteIp}`, {
    params: { limit }
  });
  return response.data;
}

export async function fetchRateLimitViolationsByService(
  service: string,
  limit: number = 100
): Promise<{ service: string; count: number; violations: RateLimitViolation[] }> {
  const response = await apiClient.get(`/security/rate-limit-violations/by-service/${service}`, {
    params: { limit }
  });
  return response.data;
}
