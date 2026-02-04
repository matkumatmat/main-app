import { TimeSeriesPoint, SecurityEvent, ServiceDistribution, EndpointMetric, SystemHealth, DashboardSummary, User, Invoice, AccessLog, Microservice, Incident, Deployment, DbTable, RedisKey, Job, QueueStats, Worker } from '../types';

export const generateTimeSeriesData = (days: number): TimeSeriesPoint[] => {
  const data: TimeSeriesPoint[] = [];
  const now = new Date();
  const points = days * 24; // Hourly points

  for (let i = points; i >= 0; i--) {
    const date = new Date(now.getTime() - i * 60 * 60 * 1000);
    const baseLoad = 500 + Math.random() * 200;
    const hour = date.getHours();
    
    // Simulate traffic patterns (higher during day)
    const timeMultiplier = hour > 8 && hour < 20 ? 1.5 : 0.8;
    const totalRequests = Math.floor(baseLoad * timeMultiplier);
    
    data.push({
      timestamp: date.toISOString(),
      totalRequests,
      errorCount: Math.floor(totalRequests * (0.01 + Math.random() * 0.02)),
      rateLimitedCount: Math.floor(totalRequests * (0.005 + Math.random() * 0.01)),
      avgLatency: 45 + Math.random() * 30, // ms
    });
  }
  return data;
};

export const generateResourceData = () => {
  const data = [];
  const now = new Date();
  for (let i = 24; i >= 0; i--) {
    const date = new Date(now.getTime() - i * 3600 * 1000); // Hourly
    data.push({
      timestamp: date.toISOString(),
      cpu: 30 + Math.random() * 40, // 30-70%
      memory: 45 + Math.random() * 20, // 45-65%
    });
  }
  return data;
};

export const mockServiceData: ServiceDistribution[] = [
  { name: 'Auth Service', value: 45000, color: '#8ACE00' }, // Primary
  { name: 'Payment Service', value: 25000, color: '#22d3ee' }, // Cyan
  { name: 'Admin Service', value: 15000, color: '#f472b6' }, // Pink
];

export const mockStatusCodeData = [
  { name: '2xx Success', value: 142000, color: '#8ACE00' },
  { name: '4xx Client Err', value: 2500, color: '#f472b6' },
  { name: '5xx Server Err', value: 703, color: '#ef4444' },
];

export const mockTopEndpoints: EndpointMetric[] = [
  { url: '/api/v1/login', method: 'POST', count: 12500, errorRate: 0.02 },
  { url: '/api/v1/payments', method: 'POST', count: 8300, errorRate: 0.05 },
  { url: '/api/v1/users', method: 'GET', count: 6200, errorRate: 0.01 },
  { url: '/api/admin/metrics', method: 'GET', count: 4100, errorRate: 0.0 },
  { url: '/api/v1/refresh', method: 'POST', count: 3800, errorRate: 0.03 },
];

export const mockSecurityEvents: SecurityEvent[] = [
  { id: '1', timestamp: new Date().toISOString(), type: 'DOS_ATTEMPT', severity: 'high', sourceIp: '192.168.1.105', details: '> 1000 req/s detected' },
  { id: '2', timestamp: new Date(Date.now() - 1000 * 60 * 15).toISOString(), type: 'RATE_LIMIT', severity: 'medium', sourceIp: '45.33.22.11', details: 'Exceeded 100 req/min' },
  { id: '3', timestamp: new Date(Date.now() - 1000 * 60 * 45).toISOString(), type: 'SUSPICIOUS_IP', severity: 'low', sourceIp: '103.21.44.12', details: 'Known botnet signature' },
  { id: '4', timestamp: new Date(Date.now() - 1000 * 60 * 120).toISOString(), type: 'RATE_LIMIT', severity: 'medium', sourceIp: '88.12.99.10', details: 'Exceeded 100 req/min' },
  { id: '5', timestamp: new Date(Date.now() - 1000 * 60 * 200).toISOString(), type: 'RATE_LIMIT', severity: 'low', sourceIp: '201.12.99.10', details: 'Exceeded 100 req/min' },
  { id: '6', timestamp: new Date(Date.now() - 1000 * 60 * 300).toISOString(), type: 'SUSPICIOUS_IP', severity: 'high', sourceIp: '99.12.33.21', details: 'SQL Injection Attempt' },
];

export const mockHealth: SystemHealth = {
  database: { status: 'healthy', latency: 12 },
  redis: { status: 'healthy', latency: 4 },
  lastUpdated: new Date().toISOString()
};

export const mockDetailedHealth = [
  { name: 'Primary Database', type: 'PostgreSQL', status: 'healthy', latency: 12, uptime: '99.99%', version: '15.3' },
  { name: 'Cache Layer', type: 'Redis', status: 'healthy', latency: 4, uptime: '99.95%', version: '7.0' },
  { name: 'Auth Service', type: 'FastAPI', status: 'healthy', latency: 45, uptime: '99.90%', version: '2.1.0' },
  { name: 'Payment Gateway', type: 'External', status: 'degraded', latency: 250, uptime: '98.50%', version: 'v3' },
  { name: 'Admin Worker', type: 'Celery', status: 'healthy', latency: 0, uptime: '99.99%', version: '5.2' },
];

export const mockHealthLogs = [
  { id: 1, time: '10:45:22', level: 'INFO', message: 'Health check passed for all services' },
  { id: 2, time: '10:40:22', level: 'WARN', message: 'Payment Gateway latency spike (250ms)' },
  { id: 3, time: '10:35:22', level: 'INFO', message: 'Health check passed for all services' },
  { id: 4, time: '10:30:22', level: 'INFO', message: 'Database backup completed successfully' },
  { id: 5, time: '10:25:22', level: 'INFO', message: 'Health check passed for all services' },
];

export const mockSummary: DashboardSummary = {
  totalRequests: 145203,
  errorRate: 1.2,
  avgLatency: 54,
  activeViolations: 3
};

// --- New Management Data ---

export const mockUsers: User[] = [
  { id: 'USR-001', merchantId: 'MERCH-8823', name: 'Alice Johnson', email: 'alice@example.com', userType: 'User', status: 'Active', lastLogin: '2 mins ago', subscriptionPlan: 'Enterprise' },
  { id: 'USR-002', merchantId: 'MERCH-9102', name: 'Bob Smith', email: 'bob.smith@company.net', userType: 'User', status: 'Active', lastLogin: '1 hour ago', subscriptionPlan: 'Pro' },
  { id: 'USR-003', merchantId: 'MERCH-1120', name: 'Charlie Brown', email: 'charlie@test.com', userType: 'Anonymous', status: 'Suspended', lastLogin: '5 days ago', subscriptionPlan: 'Free' },
  { id: 'USR-004', merchantId: 'MERCH-3341', name: 'David Lee', email: 'david.lee@tech.io', userType: 'User', status: 'Active', lastLogin: '3 hours ago', subscriptionPlan: 'Pro' },
  { id: 'USR-005', merchantId: 'MERCH-0000', name: 'Eva Green', email: 'eva.green@nature.org', userType: 'Anonymous', status: 'Pending', lastLogin: 'Never', subscriptionPlan: 'Free' },
  { id: 'USR-006', merchantId: 'MERCH-5512', name: 'Frank White', email: 'frank@example.com', userType: 'User', status: 'Active', lastLogin: '1 day ago', subscriptionPlan: 'Pro' },
  { id: 'USR-007', merchantId: 'MERCH-2211', name: 'Grace Hall', email: 'grace@example.com', userType: 'User', status: 'Active', lastLogin: '2 days ago', subscriptionPlan: 'Pro' },
];

export const mockInvoices: Invoice[] = [
  { id: 'INV-2024-001', userId: 'USR-002', userName: 'Bob Smith', amount: 49.00, currency: 'USD', status: 'Paid', date: '2024-03-01', gateway: 'Stripe' },
  { id: 'INV-2024-002', userId: 'USR-001', userName: 'Alice Johnson', amount: 299.00, currency: 'USD', status: 'Paid', date: '2024-03-02', gateway: 'Bank Transfer' },
  { id: 'INV-2024-003', userId: 'USR-004', userName: 'David Lee', amount: 49.00, currency: 'USD', status: 'Pending', date: '2024-03-05', gateway: 'Stripe' },
  { id: 'INV-2024-004', userId: 'USR-003', userName: 'Charlie Brown', amount: 15.00, currency: 'USD', status: 'Failed', date: '2024-02-28', gateway: 'PayPal' },
  { id: 'INV-2024-005', userId: 'USR-006', userName: 'Frank White', amount: 99.00, currency: 'USD', status: 'Paid', date: '2024-03-04', gateway: 'Stripe' },
];

export const generateAccessLogs = (count: number): AccessLog[] => {
  const methods = ['GET', 'POST', 'PUT', 'DELETE'];
  const paths = [
    '/api/auth/health', '/api/v1/login', '/api/v1/users', 
    '/api/v1/payments/create', '/api/admin/metrics', '/api/v1/invoices'
  ];
  const services = ['nginx_gateway', 'auth_service', 'payment_service'];
  const userAgents = [
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
    'Mozilla/5.0 (X11; Linux x86_64; rv:109.0)',
    'PostmanRuntime/7.29.0',
    'axios/1.3.4'
  ];

  return Array.from({ length: count }).map((_, i) => {
    const isError = Math.random() > 0.9;
    const status = isError ? (Math.random() > 0.5 ? 500 : 400) : 200;
    const nginxLatency = 0.001 + Math.random() * 0.010;
    const backendLatency = isError ? 0.005 : (Math.random() * 0.200);
    
    return {
      timestamp: new Date(Date.now() - i * 10000).toISOString(),
      category: 'system',
      type: 'http_access',
      service: services[Math.floor(Math.random() * services.length)],
      request_id: Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15),
      remote_ip: `192.168.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}`,
      x_forwarded_for: '',
      method: methods[Math.floor(Math.random() * methods.length)],
      url: paths[Math.floor(Math.random() * paths.length)],
      status: status,
      rate_limited: Math.random() > 0.95,
      user_agent: userAgents[Math.floor(Math.random() * userAgents.length)],
      nginx_latency_s: Number(nginxLatency.toFixed(4)),
      backend_latency_s: backendLatency.toFixed(3), // Keeping as string to match schema behavior
      user_id: Math.random() > 0.5 ? `USR-${Math.floor(Math.random() * 1000)}` : ''
    };
  });
};

export const mockMicroservices: Microservice[] = [
  {
    id: 'nginx_gateway',
    name: 'API Gateway',
    status: 'healthy',
    version: 'v1.12.0',
    replicas: 4,
    cpuUsage: 45,
    memoryUsage: 60,
    uptime: '14d 2h',
    region: 'us-east-1a',
    dependencies: ['auth_service', 'payment_service', 'admin_service']
  },
  {
    id: 'auth_service',
    name: 'Auth Service',
    status: 'healthy',
    version: 'v2.1.0',
    replicas: 3,
    cpuUsage: 25,
    memoryUsage: 30,
    uptime: '5d 12h',
    region: 'us-east-1a',
    dependencies: ['redis_cache', 'postgres_db']
  },
  {
    id: 'payment_service',
    name: 'Payment Service',
    status: 'degraded',
    version: 'v1.4.2',
    replicas: 2,
    cpuUsage: 78,
    memoryUsage: 85,
    uptime: '1d 4h',
    region: 'us-east-1b',
    dependencies: ['postgres_db', 'stripe_api']
  },
  {
    id: 'admin_service',
    name: 'Admin Service',
    status: 'healthy',
    version: 'v1.0.9',
    replicas: 1,
    cpuUsage: 12,
    memoryUsage: 20,
    uptime: '30d 1h',
    region: 'us-east-1c',
    dependencies: ['postgres_db']
  },
  {
    id: 'redis_cache',
    name: 'Redis Cluster',
    status: 'healthy',
    version: '7.0.12',
    replicas: 3,
    cpuUsage: 15,
    memoryUsage: 40,
    uptime: '60d',
    region: 'us-east-1',
    dependencies: []
  },
  {
    id: 'postgres_db',
    name: 'PostgreSQL Primary',
    status: 'healthy',
    version: '15.3',
    replicas: 2,
    cpuUsage: 55,
    memoryUsage: 72,
    uptime: '60d',
    region: 'us-east-1',
    dependencies: []
  }
];

export const mockIncidents: Incident[] = [
  {
    id: 'INC-2041',
    title: 'High Latency on Payment Service',
    description: 'P99 latency exceeding 2s. Potential database lock contention on transaction table.',
    status: 'Investigating',
    severity: 'Major',
    service: 'payment_service',
    assignee: 'Alice J.',
    createdAt: new Date(Date.now() - 1000 * 60 * 45).toISOString(), // 45 mins ago
    updatedAt: new Date(Date.now() - 1000 * 60 * 10).toISOString(),
    comments: 4
  },
  {
    id: 'INC-2040',
    title: 'API Gateway 502 Errors',
    description: 'Intermittent 502s from Gateway. Logs show connection refused from upstream Auth Service.',
    status: 'Resolved',
    severity: 'Critical',
    service: 'nginx_gateway',
    assignee: 'Bob S.',
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 4).toISOString(), // 4 hours ago
    updatedAt: new Date(Date.now() - 1000 * 60 * 60 * 3).toISOString(),
    comments: 12
  },
  {
    id: 'INC-2042',
    title: 'Redis Memory Usage High',
    description: 'Cache node 2 approaching 90% memory usage. Eviction rate increasing.',
    status: 'Open',
    severity: 'Minor',
    service: 'redis_cache',
    assignee: undefined,
    createdAt: new Date(Date.now() - 1000 * 60 * 15).toISOString(), // 15 mins ago
    updatedAt: new Date(Date.now() - 1000 * 60 * 15).toISOString(),
    comments: 0
  },
  {
    id: 'INC-2039',
    title: 'Scheduled Maintenance',
    description: 'Routine database version upgrade. No downtime expected.',
    status: 'Resolved',
    severity: 'Minor',
    service: 'postgres_db',
    assignee: 'System',
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString(),
    updatedAt: new Date(Date.now() - 1000 * 60 * 60 * 23).toISOString(),
    comments: 2
  }
];

export const mockDeployments: Deployment[] = [
  {
    id: 'deploy-8821',
    service: 'auth_service',
    version: 'v2.1.1',
    commitHash: 'a1b2c3d',
    message: 'Fix: JWT token validation edge case',
    author: 'Alice Johnson',
    timestamp: new Date().toISOString(),
    status: 'in_progress',
    duration: '0:45'
  },
  {
    id: 'deploy-8820',
    service: 'payment_service',
    version: 'v1.4.2',
    commitHash: 'e4f5g6h',
    message: 'Feat: Add support for Apple Pay',
    author: 'Bob Smith',
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(),
    status: 'success',
    duration: '2:30'
  },
  {
    id: 'deploy-8819',
    service: 'admin_service',
    version: 'v1.0.9',
    commitHash: 'i7j8k9l',
    message: 'Chore: Update dependency versions',
    author: 'Charlie Brown',
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 5).toISOString(),
    status: 'success',
    duration: '1:15'
  },
  {
    id: 'deploy-8818',
    service: 'nginx_gateway',
    version: 'v1.12.0',
    commitHash: 'm0n1o2p',
    message: 'Config: Increase rate limits for pro users',
    author: 'David Lee',
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString(),
    status: 'success',
    duration: '0:30'
  },
  {
    id: 'deploy-8817',
    service: 'payment_service',
    version: 'v1.4.1',
    commitHash: 'q3r4s5t',
    message: 'Fix: Database timeout on high load',
    author: 'Alice Johnson',
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 26).toISOString(),
    status: 'failed',
    duration: '3:10'
  }
];

export const mockDbTables: DbTable[] = [
  {
    name: 'users',
    rowCount: 14205,
    size: '4.2 MB',
    columns: [
      { name: 'id', type: 'uuid', isPrimaryKey: true },
      { name: 'email', type: 'varchar(255)' },
      { name: 'full_name', type: 'varchar(100)' },
      { name: 'created_at', type: 'timestamp' },
      { name: 'status', type: 'varchar(20)' },
    ],
    data: [
      { id: '123e4567-e89b-12d3-a456-426614174000', email: 'alice@example.com', full_name: 'Alice Johnson', created_at: '2023-01-15T08:30:00Z', status: 'active' },
      { id: '123e4567-e89b-12d3-a456-426614174001', email: 'bob@example.com', full_name: 'Bob Smith', created_at: '2023-02-20T14:15:00Z', status: 'active' },
      { id: '123e4567-e89b-12d3-a456-426614174002', email: 'charlie@test.com', full_name: 'Charlie Brown', created_at: '2023-03-05T09:45:00Z', status: 'suspended' },
      { id: '123e4567-e89b-12d3-a456-426614174003', email: 'david@tech.io', full_name: 'David Lee', created_at: '2023-03-10T11:20:00Z', status: 'active' },
      { id: '123e4567-e89b-12d3-a456-426614174004', email: 'eva@nature.org', full_name: 'Eva Green', created_at: '2023-03-12T16:00:00Z', status: 'pending' },
    ]
  },
  {
    name: 'transactions',
    rowCount: 89002,
    size: '22 MB',
    columns: [
      { name: 'id', type: 'uuid', isPrimaryKey: true },
      { name: 'user_id', type: 'uuid' },
      { name: 'amount', type: 'decimal(10,2)' },
      { name: 'currency', type: 'varchar(3)' },
      { name: 'status', type: 'varchar(20)' },
      { name: 'processed_at', type: 'timestamp' },
    ],
    data: [
      { id: 'tx_99812', user_id: '...4000', amount: 49.99, currency: 'USD', status: 'completed', processed_at: '2023-03-25T10:00:00Z' },
      { id: 'tx_99813', user_id: '...4001', amount: 12.50, currency: 'EUR', status: 'completed', processed_at: '2023-03-25T10:05:00Z' },
      { id: 'tx_99814', user_id: '...4002', amount: 199.00, currency: 'USD', status: 'failed', processed_at: '2023-03-25T10:12:00Z' },
    ]
  },
  {
    name: 'audit_logs',
    rowCount: 450120,
    size: '156 MB',
    columns: [
      { name: 'id', type: 'bigint', isPrimaryKey: true },
      { name: 'actor_id', type: 'uuid' },
      { name: 'action', type: 'varchar(50)' },
      { name: 'resource', type: 'varchar(100)' },
      { name: 'timestamp', type: 'timestamp' },
    ],
    data: [
       { id: 44001, actor_id: 'admin_1', action: 'delete_user', resource: 'user:8812', timestamp: '2024-01-01T00:00:00Z'},
       { id: 44002, actor_id: 'system', action: 'rotate_key', resource: 'api_key:primary', timestamp: '2024-01-01T01:00:00Z'},
    ]
  }
];

export const mockRedisKeys: RedisKey[] = [
  { key: 'session:user:123', type: 'string', ttl: 3400, size: '248 B', value: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' },
  { key: 'cache:products:featured', type: 'string', ttl: 120, size: '4 KB', value: '[{"id":1,"name":"Pro Plan"},{"id":2,"name":"Enterprise"}]' },
  { key: 'rate_limit:ip:192.168.1.5', type: 'string', ttl: 58, size: '2 B', value: '42' },
  { key: 'queue:email_notifications', type: 'list', ttl: -1, size: '15 items', value: ['email_1', 'email_2', 'email_3'] },
  { key: 'config:feature_flags', type: 'hash', ttl: -1, size: '4 fields', value: { beta_ui: 'true', maintenance: 'false' } },
];

// Jobs and Queues Mock Data
export const mockQueues: QueueStats[] = [
  { name: 'email_sending', active: 12, waiting: 45, delayed: 2, failed: 5, paused: false },
  { name: 'image_processing', active: 4, waiting: 120, delayed: 0, failed: 1, paused: false },
  { name: 'report_generation', active: 1, waiting: 2, delayed: 0, failed: 0, paused: true },
  { name: 'webhooks', active: 25, waiting: 890, delayed: 50, failed: 12, paused: false },
];

export const mockWorkers: Worker[] = [
  { id: 'worker-01', host: 'worker-pool-a', pid: 1044, queues: ['email_sending', 'webhooks'], status: 'busy', startedAt: '2d ago', cpuUsage: 45, ramUsage: 60 },
  { id: 'worker-02', host: 'worker-pool-a', pid: 1045, queues: ['email_sending', 'webhooks'], status: 'busy', startedAt: '2d ago', cpuUsage: 52, ramUsage: 65 },
  { id: 'worker-03', host: 'worker-pool-b', pid: 2102, queues: ['image_processing'], status: 'idle', startedAt: '5h ago', cpuUsage: 5, ramUsage: 20 },
  { id: 'worker-04', host: 'worker-pool-c', pid: 3321, queues: ['report_generation'], status: 'idle', startedAt: '1d ago', cpuUsage: 2, ramUsage: 40 },
];

export const mockJobs: Job[] = [
  { id: 'job-9912', name: 'send_welcome_email', queue: 'email_sending', status: 'active', args: '{"user_id": 4412}', timestamp: new Date().toISOString(), attempts: 1 },
  { id: 'job-9911', name: 'process_avatar', queue: 'image_processing', status: 'completed', args: '{"file": "s3://..."}', result: 'Done', timestamp: new Date(Date.now() - 1000 * 30).toISOString(), duration: '2.4s', attempts: 1 },
  { id: 'job-9910', name: 'webhook_dispatch', queue: 'webhooks', status: 'failed', args: '{"url": "https://api.partner.com"}', error: 'Connection Timeout', timestamp: new Date(Date.now() - 1000 * 60).toISOString(), duration: '30s', attempts: 3 },
  { id: 'job-9909', name: 'generate_pdf', queue: 'report_generation', status: 'waiting', args: '{"report_id": 881}', timestamp: new Date(Date.now() - 1000 * 120).toISOString(), attempts: 0 },
  { id: 'job-9908', name: 'send_invoice', queue: 'email_sending', status: 'completed', args: '{"invoice_id": "INV-001"}', result: 'Sent', timestamp: new Date(Date.now() - 1000 * 300).toISOString(), duration: '0.8s', attempts: 1 },
];