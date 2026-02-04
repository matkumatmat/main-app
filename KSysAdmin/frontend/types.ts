
export type ServiceType = 'all' | 'auth' | 'payment' | 'admin';

export interface TimeSeriesPoint {
  timestamp: string;
  totalRequests: number;
  errorCount: number;
  rateLimitedCount: number;
  avgLatency: number;
}

export interface ServiceDistribution {
  name: string;
  value: number;
  color: string;
}

export interface EndpointMetric {
  url: string;
  method: string;
  count: number;
  errorRate: number;
}

export interface SecurityEvent {
  id: string;
  timestamp: string;
  type: 'DOS_ATTEMPT' | 'RATE_LIMIT' | 'SUSPICIOUS_IP';
  severity: 'low' | 'medium' | 'high';
  sourceIp: string;
  details: string;
}

export interface SystemHealth {
  database: { status: 'healthy' | 'degraded' | 'down'; latency: number };
  redis: { status: 'healthy' | 'degraded' | 'down'; latency: number };
  lastUpdated: string;
}

export interface DashboardSummary {
  totalRequests: number;
  errorRate: number;
  avgLatency: number;
  activeViolations: number;
}

export interface User {
  id: string;
  merchantId: string;
  name: string;
  email: string;
  userType: 'User' | 'Anonymous';
  status: 'Active' | 'Suspended' | 'Pending';
  lastLogin: string;
  subscriptionPlan: 'Free' | 'Pro' | 'Enterprise';
}

export interface Invoice {
  id: string;
  userId: string;
  userName: string;
  amount: number;
  currency: string;
  status: 'Paid' | 'Pending' | 'Failed';
  date: string;
  gateway: 'Stripe' | 'PayPal' | 'Bank Transfer';
}

export interface AccessLog {
  timestamp: string;
  category: string;
  type: string;
  service: string;
  request_id: string;
  remote_ip: string;
  x_forwarded_for: string;
  method: string;
  url: string;
  status: number;
  rate_limited: boolean;
  user_agent: string;
  nginx_latency_s: number;
  backend_latency_s: string | number; // Handles potential string format from logs
  user_id: string;
}

export interface Microservice {
  id: string;
  name: string;
  status: 'healthy' | 'degraded' | 'down';
  version: string;
  replicas: number;
  cpuUsage: number;
  memoryUsage: number;
  uptime: string;
  region: string;
  dependencies: string[];
}

export interface Incident {
  id: string;
  title: string;
  description: string;
  status: 'Open' | 'Investigating' | 'Resolved';
  severity: 'Critical' | 'Major' | 'Minor';
  service: string;
  assignee?: string;
  createdAt: string;
  updatedAt: string;
  comments: number;
}

export interface Deployment {
  id: string;
  service: string;
  version: string;
  commitHash: string;
  message: string;
  author: string;
  timestamp: string;
  status: 'success' | 'failed' | 'in_progress' | 'queued';
  duration: string;
}

export interface DbColumn {
  name: string;
  type: string;
  isPrimaryKey?: boolean;
}

export interface DbTable {
  name: string;
  columns: DbColumn[];
  rowCount: number;
  size: string;
  data: any[];
}

export interface RedisKey {
  key: string;
  type: 'string' | 'hash' | 'list' | 'set';
  ttl: number; // seconds, -1 for infinite
  size: string;
  value: any;
}

export interface Job {
  id: string;
  name: string;
  queue: string;
  status: 'active' | 'completed' | 'failed' | 'delayed' | 'waiting';
  args: string;
  result?: string;
  error?: string;
  timestamp: string;
  duration?: string;
  attempts: number;
}

export interface QueueStats {
  name: string;
  active: number;
  waiting: number;
  delayed: number;
  failed: number;
  paused: boolean;
}

export interface Worker {
  id: string;
  host: string;
  pid: number;
  queues: string[];
  status: 'busy' | 'idle';
  startedAt: string;
  cpuUsage: number;
  ramUsage: number;
}