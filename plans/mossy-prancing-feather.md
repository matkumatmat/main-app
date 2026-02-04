# Admin Monitoring System Implementation Plan

## Overview
Build a comprehensive monitoring system in KSysAdmin service to track security events, system health, and request metrics with 7-day retention. Full-stack implementation: Backend (FastAPI) + Frontend (React dashboard).

## Requirements
- **Security monitoring**: Rate limit violations, DOS attempts, suspicious IPs
- **System health tracking**: Database/Redis latency over time, error rates
- **Historical analytics**: Request trends, error rates, latency charts (7-day retention)
- **Frontend**: Full React dashboard with charts
- **No alerts yet** (future phase)

## Architecture Pattern
**Hexagonal (Layered)**: Domain → Application (DTOs) → Infrastructure (HTTP/Database)

**Data Sources**:
1. Nginx access logs: `/nginx/logs/access.log` (JSON format)
2. Nginx DOS logs: `/nginx/logs/dos_attempts.log`
3. Redis violations: `rate_limit:violations` list
4. Health checks: `/health` endpoint

---

## Database Schema (SQLModel Models)

### 1. **MetricSnapshot** (Raw HTTP metrics)
```python
id: UUID7 (PK)
timestamp: datetime (indexed)
service: str (auth/payment/admin, indexed)
remote_ip: str (indexed)
request_id: str
method: str
url: str
status: int
rate_limited: bool (indexed)
user_agent: str
nginx_latency_ms: float
backend_latency_ms: float | None
user_id: str | None (indexed)
```

### 2. **HourlyMetricAggregation** (Aggregated for fast queries)
```python
id: UUID7 (PK)
hour_start: datetime (unique with service, indexed)
service: str (indexed)
total_requests: int
successful_requests: int
client_errors: int
server_errors: int
rate_limited_requests: int
avg_nginx_latency_ms: float
avg_backend_latency_ms: float
p95_nginx_latency_ms: float
p95_backend_latency_ms: float
unique_ips: int
```

### 3. **RateLimitViolation**
```python
id: UUID7 (PK)
timestamp: datetime (indexed)
service: str (indexed)
remote_ip: str (indexed)
violation_count: int
user_id: str | None
```

### 4. **SystemHealthSnapshot**
```python
id: UUID7 (PK)
timestamp: datetime (indexed)
db_status: str
db_latency_ms: float
redis_status: str
redis_latency_ms: float
crypto_status: str
```

### 5. **SuspiciousActivity**
```python
id: UUID7 (PK)
timestamp: datetime (indexed)
remote_ip: str (indexed)
activity_type: str (dos_attempt/rapid_violations)
severity: str (low/medium/high, indexed)
details: dict (JSONB)
```

**Indexes**: All timestamp fields (DESC), composite indexes on (service, timestamp), (remote_ip, timestamp)

**Retention**: Raw metrics 7 days, hourly aggregations 7 days, auto-cleanup daily at 2 AM

---

## Backend Implementation

### Domain Layer (`backend/domain/`)

**Models** (`models/`):
- `metricSnapshot.py` - HTTP request metrics (SQLModel)
- `hourlyMetricAggregation.py` - Hourly rollups (SQLModel)
- `rateLimitViolation.py` - Rate limit events (SQLModel)
- `systemHealthSnapshot.py` - Health metrics (SQLModel)
- `suspiciousActivity.py` - Security events (SQLModel)

**Domain Services** (`services/`):
- `metricCollectionService.py` - Orchestrates log parsing and storage
- `aggregationService.py` - Computes hourly rollups
- `securityAnalysisService.py` - Detects suspicious patterns (>10 violations in 5min)
- `retentionService.py` - Cleanup old data (>7 days)

**Value Objects** (`valueObjects/`):
- `timeRange.py` - Date range validation
- `latencyAnalyzer.py` - Percentile calculations

**Exceptions** (`exceptions/`):
- `monitoringExceptions.py` - LogParsingException, MetricCollectionException, AggregationException

### Application Layer (`backend/application/`)

**DTOs** (`dto/`):
- **Input**: `metricsQueryInput.py`, `securityQueryInput.py`, `healthQueryInput.py`
- **Output**: `metricSnapshotOutput.py`, `hourlyMetricOutput.py`, `securityEventOutput.py`, `timeSeriesOutput.py`, `dashboardSummaryOutput.py`

**Application Services** (`services/`):
- `metricQueryService.py` - Query orchestration (filtering, pagination)
- `dashboardService.py` - Aggregates data for dashboard views

### Infrastructure Layer (`backend/infrastructure/`)

**Database** (`database/`):
- **Alembic**: `alembic/` (initialize with `alembic init`, create first migration)
  - `versions/001_create_monitoring_tables.py` - Initial migration
- **Repositories** (`repositories/`):
  - `metricRepository.py` - Extends BaseRepository, bulk insert, time range queries
  - `aggregationRepository.py` - Hourly metrics storage and queries
  - `violationRepository.py` - Violation queries, top IPs
  - `healthRepository.py` - Health history
  - `securityRepository.py` - Suspicious activities

**HTTP** (`http/routers/`):
- `monitoringRouter.py` - FastAPI endpoints:
  - `GET /api/admin/monitoring/metrics/raw` - Raw metrics (paginated)
  - `GET /api/admin/monitoring/metrics/hourly` - Hourly aggregations
  - `GET /api/admin/monitoring/metrics/timeseries` - Chart data
  - `GET /api/admin/monitoring/security/violations` - Violations list
  - `GET /api/admin/monitoring/security/suspicious` - Suspicious activities
  - `GET /api/admin/monitoring/security/ips` - Top violating IPs
  - `GET /api/admin/monitoring/health/current` - Current health
  - `GET /api/admin/monitoring/health/history` - Health time series
  - `GET /api/admin/monitoring/dashboard/summary` - Dashboard metrics (24h)

**Integrations** (`integrations/`):
- `nginxLogParser.py` - Parse JSON log lines to MetricSnapshot
- `redisViolationReader.py` - Read `rate_limit:violations` Redis list
- `healthCheckPoller.py` - Poll `/health` endpoint

**Background Tasks** (`tasks/`):
- `metricCollectionTask.py` - Every 5 min: parse logs, read Redis, poll health
- `aggregationTask.py` - Hourly: compute aggregations for previous hour
- `retentionCleanupTask.py` - Daily 2 AM: delete data >7 days

**Task Scheduler**:
- Use APScheduler (add to pyproject.toml)
- Start in `admin_server.py` startup event
- Stop in shutdown event

---

## Log Parsing Strategy

**Incremental File Reading**:
1. Store last processed position in Redis: `ksysadmin:log_parser:access_log_position`
2. On each run (every 5 min):
   - Open `/nginx/logs/access.log`
   - Seek to last position
   - Read new lines (one per iteration)
   - Parse JSON with `json.loads()`
   - Convert to `MetricSnapshot` domain model
   - Bulk insert (batch 100)
   - Update position in Redis
3. Handle log rotation: If file size < last position, reset to 0
4. Handle malformed JSON: Log error, skip line, continue

**Redis Violations**:
- `LRANGE rate_limit:violations 0 -1`
- Parse format: `service:ip:count` (e.g., `auth:127.0.0.1:6`)
- Store as `RateLimitViolation`
- After processing: Keep last 100 for debugging (`LTRIM`)

**Health Polling**:
- HTTP GET to `http://localhost:8002/health`
- Parse response to `SystemHealthSnapshot`
- Store every 5 minutes

---

## Frontend Implementation

### Structure (`frontend/src/`)

**Pages** (`pages/`):
- `DashboardPage.tsx` - Main dashboard (summary cards + charts)
- `MetricsPage.tsx` - Detailed metrics view with filtering
- `SecurityPage.tsx` - Security events and violations
- `HealthPage.tsx` - System health monitoring

**Components** (`components/`):
- **Charts** (`charts/`):
  - `TimeSeriesChart.tsx` - Requests over time (Recharts line chart)
  - `BarChart.tsx` - Errors by endpoint
  - `PieChart.tsx` - Service distribution
  - `LatencyHeatmap.tsx` - Latency patterns
- **Metrics** (`metrics/`):
  - `MetricCard.tsx` - Summary cards (total requests, errors)
  - `MetricTable.tsx` - Paginated table for raw logs
  - `MetricFilter.tsx` - Date range picker + service filter
- **Security** (`security/`):
  - `ViolationList.tsx` - Rate limit violations table
  - `SuspiciousIPList.tsx` - Suspicious IPs table
  - `SecurityAlert.tsx` - Alert banner for critical events
- **Health** (`health/`):
  - `HealthStatus.tsx` - Current health badges
  - `LatencyChart.tsx` - DB/Redis latency trends
  - `ComponentStatus.tsx` - Individual component status

**Hooks** (`hooks/`):
- `useMetrics.ts` - Fetch metrics with filters
- `useSecurity.ts` - Fetch security data
- `useHealth.ts` - Fetch health data
- `usePolling.ts` - Auto-refresh (30s interval, pause when tab hidden)

**Services** (`services/`):
- `apiClient.ts` - Axios instance with base URL
- `endpoints.ts` - API endpoint constants

**Utils** (`utils/`):
- `dateFormatter.ts` - Format dates for display
- `chartHelpers.ts` - Transform API data to chart format

### Dashboard Layout
```
+--------------------------------------------------+
| Dashboard Header          Last updated: 5s ago   |
+--------------------------------------------------+
| [24h Summary Cards]                              |
| Total Req | Error Rate | Rate Limited | Avg Latency |
+--------------------------------------------------+
| [Time Series Chart] - Requests Over Time         |
|   Stacked: Success / Error / Rate Limited        |
+--------------------------------------------------+
| [Latency Chart] - Nginx vs Backend Latency       |
|   Line chart with dual Y-axis                    |
+--------------------------------------------------+
| [Service Dist] (Pie)  | [Top Endpoints] (Bar)    |
+--------------------------------------------------+
| [Security Alerts]                                |
| - Suspicious IPs | Rate limit violations         |
+--------------------------------------------------+
```

**Charts Library**: Recharts (React-first, TypeScript support)

**Features**:
- Auto-refresh every 30 seconds
- Date range filters: 1h, 6h, 24h, 7d, custom
- Service filter: All, Auth, Payment, Admin
- Loading states during fetch
- Error handling with toast notifications

---

## Implementation Sequence

### Phase 1: Database Foundation
1. Initialize Alembic in `KSysAdmin/backend/infrastructure/database/`
   - Run: `alembic init alembic` from that directory
   - Configure `alembic.ini` with database URL
   - Update `env.py` to import SQLModel models
2. Create all domain models in `backend/domain/models/`
3. Create Alembic migration: `alembic revision --autogenerate -m "create monitoring tables"`
4. Apply migration: `alembic upgrade head`
5. Create repositories extending BaseRepository

### Phase 2: Data Collection
1. Implement `nginxLogParser.py` - parse JSON, handle errors
2. Implement `redisViolationReader.py` - read Redis list
3. Implement `healthCheckPoller.py` - poll health endpoint
4. Implement `metricCollectionService.py` - orchestrate collection
5. Implement `metricCollectionTask.py` - scheduled task (APScheduler)
6. Add scheduler to `admin_server.py` startup/shutdown
7. Test: Run for 10 minutes, verify metrics in database

### Phase 3: Aggregation & Analysis
1. Implement `aggregationService.py` - compute hourly aggregations (use PostgreSQL percentile functions)
2. Implement `aggregationTask.py` - scheduled hourly
3. Implement `securityAnalysisService.py` - detect patterns (>10 violations in 5min = DOS)
4. Implement `retentionService.py` + `retentionCleanupTask.py` - delete old data
5. Test: Verify aggregations computed correctly

### Phase 4: Backend API
1. Create all Application DTOs (Input/Output)
2. Implement `metricQueryService.py` - complex queries
3. Implement `dashboardService.py` - dashboard aggregations
4. Create `monitoringRouter.py` - all endpoints
5. Register router in `admin_server.py`: `app.include_router(monitoring_router, prefix='/api/admin/monitoring')`
6. Test: curl/Postman all endpoints

### Phase 5: Frontend Dashboard
1. Install dependencies: `npm install recharts axios date-fns`
2. Create folder structure (`pages/`, `components/`, `hooks/`, `services/`, `utils/`)
3. Implement `apiClient.ts` - axios with base URL `http://localhost:8080/api/admin`
4. Implement data fetching hooks with polling
5. Create chart components (Recharts)
6. Create dashboard page layout
7. Implement filtering (date range, service)
8. Add auto-refresh (30s polling)
9. Test: Verify dashboard displays real data

### Phase 6: Polish & Testing
1. Add loading states and error handling
2. Responsive design (mobile-friendly)
3. Performance optimization (if needed)
4. End-to-end testing
5. Documentation (README in frontend/)

---

## Critical Files to Create/Modify

**Backend (Create)**:
- `KSysAdmin/backend/domain/models/*.py` (5 models)
- `KSysAdmin/backend/domain/services/*.py` (4 services)
- `KSysAdmin/backend/application/dto/*.py` (7 DTOs)
- `KSysAdmin/backend/application/services/*.py` (2 services)
- `KSysAdmin/backend/infrastructure/database/repositories/*.py` (5 repos)
- `KSysAdmin/backend/infrastructure/integrations/*.py` (3 integrations)
- `KSysAdmin/backend/infrastructure/tasks/*.py` (3 tasks)
- `KSysAdmin/backend/infrastructure/http/routers/monitoringRouter.py`
- `KSysAdmin/backend/infrastructure/database/alembic/` (initialize)

**Backend (Modify)**:
- `/admin_server.py` - Add scheduler startup/shutdown, register monitoring router
- `pyproject.toml` - Add APScheduler dependency

**Frontend (Create)**:
- `KSysAdmin/frontend/src/pages/*.tsx` (4 pages)
- `KSysAdmin/frontend/src/components/**/*.tsx` (15+ components)
- `KSysAdmin/frontend/src/hooks/*.ts` (4 hooks)
- `KSysAdmin/frontend/src/services/*.ts` (2 services)
- `KSysAdmin/frontend/src/utils/*.ts` (2 utils)

**Frontend (Modify)**:
- `KSysAdmin/frontend/package.json` - Add recharts, axios, date-fns

**Config (Modify)**:
- `.env` - Add monitoring settings:
  - `MONITORING_COLLECTION_INTERVAL=300` (seconds)
  - `MONITORING_RETENTION_DAYS=7`
  - `NGINX_ACCESS_LOG_PATH=nginx/logs/access.log`

---

## Key Implementation Notes

1. **Alembic Setup**:
   - Run from `KSysAdmin/backend/infrastructure/database/`
   - Update `env.py` to import all SQLModel models for autogenerate
   - Set `sqlalchemy.url` in `alembic.ini` from settings

2. **Log Position Tracking**:
   - Redis key: `ksysadmin:log_parser:access_log_position` (integer)
   - Handle log rotation: Reset position if file size < last position
   - Atomic updates to prevent race conditions

3. **Bulk Insert Performance**:
   - Batch 100 MetricSnapshot objects per insert
   - Use `session.bulk_insert_mappings()` for speed
   - Commit after each batch

4. **Percentile Calculations**:
   - Use PostgreSQL `percentile_cont(0.95)` within `ARRAY_AGG` for p95
   - Compute during aggregation task, not on-demand
   - Store in HourlyMetricAggregation table

5. **APScheduler Configuration**:
   ```python
   scheduler = AsyncIOScheduler()
   scheduler.add_job(metric_collection_task, 'interval', minutes=5)
   scheduler.add_job(aggregation_task, 'cron', hour='*', minute=5)
   scheduler.add_job(retention_task, 'cron', hour=2, minute=0)
   ```

6. **Security Analysis Triggers**:
   - DOS attempt: >10 violations in 5 minutes from same IP
   - Rapid violations: >50 violations in 1 hour
   - Store in SuspiciousActivity table with severity (low/medium/high)

7. **Frontend Polling**:
   - Use `setInterval` in `usePolling` hook
   - Pause when `document.hidden` (tab not visible)
   - Resume when tab becomes visible
   - Clear interval on component unmount

8. **Error Handling**:
   - Log parsing errors: Log and skip line, don't crash
   - Redis unavailable: Log warning, continue
   - Database errors: Log and retry (exponential backoff)

9. **Frontend Chart Data**:
   - Transform API response to Recharts format in `chartHelpers.ts`
   - Handle empty data gracefully (show "No data" message)
   - Loading spinner during fetch

10. **Testing Strategy**:
    - Backend: pytest for repositories and services
    - API: curl/Postman for endpoint validation
    - Frontend: Manual testing (automated tests in future phase)
    - End-to-end: Generate traffic, verify dashboard updates

---

## Verification Checklist

**Backend**:
- [ ] Alembic migrations created and applied
- [ ] All 5 tables created with indexes
- [ ] Repositories extend BaseRepository
- [ ] Metric collection task runs every 5 minutes
- [ ] Nginx logs parsed correctly
- [ ] Redis violations read correctly
- [ ] Health checks polled and stored
- [ ] Hourly aggregations computed correctly
- [ ] Retention cleanup deletes old data
- [ ] All API endpoints return correct data
- [ ] Scheduler starts/stops with admin server

**Frontend**:
- [ ] Dashboard displays 24h summary cards
- [ ] Time series chart shows requests over time
- [ ] Latency chart shows nginx vs backend latency
- [ ] Service distribution pie chart renders
- [ ] Top endpoints bar chart renders
- [ ] Security alerts display violations
- [ ] Date range filter works
- [ ] Service filter works
- [ ] Auto-refresh updates every 30s
- [ ] Loading states show during fetch
- [ ] Error handling shows toasts
- [ ] Responsive on mobile

**End-to-End**:
- [ ] Generate traffic via curl to `/api/auth/health` (trigger rate limits)
- [ ] Wait 5 minutes for collection task
- [ ] Verify metrics appear in database
- [ ] Wait 1 hour for aggregation task
- [ ] Verify hourly aggregations computed
- [ ] Open dashboard, verify data displays
- [ ] Verify auto-refresh updates
- [ ] Test filtering and date range selection

---

## Trade-offs & Decisions

1. **File Reading vs Syslog**: Chose file reading (simpler, sufficient for current scale)
2. **Raw + Aggregates vs Aggregates Only**: Store both (debugging vs query speed)
3. **Recharts vs Chart.js**: Recharts (React-first, better TypeScript)
4. **APScheduler vs Celery**: APScheduler (simpler, in-process, sufficient)
5. **Hourly vs Real-time Aggregation**: Hourly (reduces write load)
6. **Polling vs WebSocket**: Polling (simpler, 30s sufficient for monitoring)

---

## Next Steps After Implementation

1. Add authentication to monitoring endpoints (JWT validation)
2. Implement export functionality (CSV/JSON download)
3. Add anomaly detection (ML-based pattern recognition)
4. Add alert system (webhooks, email notifications)
5. Implement WebSocket for real-time updates (<1s latency)
6. Add more advanced security analysis (IP reputation, geolocation)
7. Implement request replay (reproduce issues from logs)
8. Add performance profiling (track slow queries, N+1 problems)

---

## Dependencies to Add

**Backend** (`pyproject.toml`):
```toml
apscheduler = "^3.10.4"
```

**Frontend** (`package.json`):
```json
"dependencies": {
  "recharts": "^2.10.0",
  "axios": "^1.6.0",
  "date-fns": "^3.0.0"
}
```
