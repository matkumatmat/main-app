# KSysAdmin Implementation Plan: Phases 4-6

## Current State

**Completed (Phases 1-3):**
- Database foundation with 5 monitoring tables (Alembic migrations, repositories)
- Data collection pipeline (nginx logs, Redis violations, health polling)
- Background tasks (collection every 5min, aggregation hourly, security analysis 30min, cleanup daily)
- HTTP API endpoints for querying metrics, health, security data
- Manual trigger endpoints for aggregation/analysis/cleanup

**Architecture Pattern:**
```
KSysAdmin/backend/
├── domain/              # Business logic, SQLModel models, domain services
├── application/         # DTOs (Input/Output schemas), use cases
└── infrastructure/      # HTTP routers, database repos, collectors, tasks
```

**Stack:**
- FastAPI (async), Pydantic v2 (strict mode), SQLModel, PostgreSQL, Redis
- Frontend: React (to be implemented)
- Background: asyncio tasks, structlog logging

---

## Phase 4: Backend API Enhancements

**Goal:** Complete REST API with advanced querying, dashboard endpoints, and export capabilities.

**Critical Rules:**
- Backend is API-only (JSON responses, no HTML)
- All logic in domain services, not controllers
- Use Application DTOs for request/response schemas
- Repositories handle all database access
- No business logic in routers (thin controllers)

### 4.1 Application DTOs

**Location:** `KSysAdmin/backend/application/dto/`

Create request/response schemas (Pydantic models):

**Files to create:**
- `dashboardDTO.py` - Dashboard summary schemas
  - `DashboardSummaryOutput`: Overall system stats (total requests, error rate, uptime, active IPs)
  - `ServiceHealthOutput`: Per-service health summary
  - `TimeRangeInput`: Common input for date filtering

- `metricQueryDTO.py` - Advanced metric query schemas
  - `MetricFilterInput`: Complex filtering (service, status range, IP, time range, user_id)
  - `MetricAggregationOutput`: Custom aggregation results
  - `PaginationInput`: Offset/limit for large result sets
  - `PaginationOutput`: Wrapper with total count, page info

- `exportDTO.py` - Export request schemas
  - `ExportRequestInput`: Export format (csv/json), filters, date range
  - `ExportStatusOutput`: Export job status (for async exports)

**Naming Convention:**
- Input schemas: `*Input`
- Output schemas: `*Output`
- Use camelCase for file names, PascalCase for classes

### 4.2 Domain Services

**Location:** `KSysAdmin/backend/domain/services/`

Create new domain services:

**Files to create:**
- `dashboardService.py`
  - `DashboardService` class
  - Methods:
    - `getSystemSummary(start: datetime, end: datetime) -> dict`
    - `getServiceHealthSummary() -> list[dict]`
    - `getTopIPs(limit: int, metric: str) -> list[dict]` (by requests, errors, rate-limited)
    - `getErrorRateTrend(hours: int) -> list[dict]`
  - Use existing repositories to query data
  - Business logic for calculating summaries

- `metricQueryService.py`
  - `MetricQueryService` class
  - Methods:
    - `queryMetrics(filters: MetricFilterInput, pagination: PaginationInput) -> tuple[list, int]`
    - `aggregateMetrics(filters: MetricFilterInput, group_by: str) -> list[dict]`
    - `searchByIP(ip: str, time_range: tuple[datetime, datetime]) -> dict`
  - Advanced query logic, complex filters
  - Returns structured data for API consumption

- `exportService.py`
  - `ExportService` class
  - Methods:
    - `exportMetricsToCSV(filters: MetricFilterInput) -> str` (returns CSV string)
    - `exportMetricsToJSON(filters: MetricFilterInput) -> list[dict]`
    - `exportAggregationsToCSV(service: str, start: datetime, end: datetime) -> str`
  - Format conversion logic
  - Large dataset handling (streaming for CSV)

**Important:**
- All services use AsyncSession from DI
- Services depend on repositories (inject via constructor)
- No HTTP concerns in domain layer
- Return domain objects or dicts (no Pydantic in domain)

### 4.3 HTTP Routers

**Location:** `KSysAdmin/backend/infrastructure/http/routers/`

Create new router files:

**Files to create:**
- `dashboardRouter.py`
  - Prefix: `/dashboard`
  - Endpoints:
    - `GET /summary?start=X&end=Y` - System summary
    - `GET /services` - All service health summaries
    - `GET /top-ips?metric=X&limit=Y` - Top IPs by metric
    - `GET /error-trend?hours=X` - Error rate trend
  - Uses `DashboardService`
  - Returns `*Output` DTOs

- `advancedMetricsRouter.py`
  - Prefix: `/metrics/advanced`
  - Endpoints:
    - `POST /query` - Complex metric queries (body: MetricFilterInput)
    - `POST /aggregate` - Custom aggregations (body: filters + group_by)
    - `GET /search/ip/{ip}` - Search all metrics for IP
  - Uses `MetricQueryService`
  - Pagination support

- `exportRouter.py`
  - Prefix: `/export`
  - Endpoints:
    - `POST /metrics/csv` - Export metrics to CSV (returns file)
    - `POST /metrics/json` - Export metrics to JSON
    - `POST /aggregations/csv` - Export hourly aggregations to CSV
  - Uses `ExportService`
  - Set proper Content-Type headers for downloads
  - Consider streaming for large exports

**Router Pattern:**
```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from shared.backend.database.engine import getDb
from KSysAdmin.backend.infrastructure.http.dependencies.adminAuth import verifyAdminHashKey
from KSysAdmin.backend.domain.services.dashboardService import DashboardService
from KSysAdmin.backend.application.dto.dashboardDTO import DashboardSummaryOutput

router = APIRouter(prefix='/dashboard', tags=['Dashboard'], dependencies=[Depends(verifyAdminHashKey)])

@router.get('/summary', response_model=DashboardSummaryOutput)
async def getDashboardSummary(
    start: datetime = Query(...),
    end: datetime = Query(...),
    session: AsyncSession = Depends(getDb)
):
    service = DashboardService(session)
    summary = await service.getSystemSummary(start, end)
    return summary
```

### 4.4 Integration

**Update:** `scripts/admin_server.py`
- Import new routers
- Include with `/api/admin` prefix
- Register all endpoints

**Testing:**
- Use curl to test each endpoint
- Verify response schemas match DTOs
- Test filtering, pagination, exports
- Check performance with large datasets

---

## Phase 5: Frontend Dashboard (React)

**Goal:** Build interactive admin dashboard for monitoring system health, metrics, and security.

**Critical Rules:**
- Frontend is client-side rendered (CSR)
- Backend serves API only (JSON), frontend handles routing
- Use React Router for navigation
- Fetch data from backend API endpoints
- No server-side rendering (SSR)

### 5.1 Project Setup

**Location:** `KSysAdmin/frontend/` (already exists with basic structure)

**Dependencies (update package.json):**
```json
{
  "dependencies": {
    "react": "^18.x",
    "react-dom": "^18.x",
    "react-router-dom": "^6.x",
    "axios": "^1.x",
    "recharts": "^2.x",
    "date-fns": "^3.x",
    "@tanstack/react-query": "^5.x"
  },
  "devDependencies": {
    "vite": "^5.x",
    "typescript": "^5.x",
    "@vitejs/plugin-react": "^4.x"
  }
}
```

**File Structure:**
```
KSysAdmin/frontend/
├── src/
│   ├── api/              # API client and hooks
│   ├── components/       # Reusable UI components
│   ├── pages/            # Page components (Dashboard, Metrics, Security)
│   ├── hooks/            # Custom React hooks
│   ├── types/            # TypeScript types (match backend DTOs)
│   ├── utils/            # Helper functions
│   ├── App.tsx           # Root component with routing
│   └── main.tsx          # Entry point
├── public/               # Static assets
├── index.html
├── vite.config.ts
└── tsconfig.json
```

**Naming Convention:**
- Folders: PascalCase (Components/, Pages/)
- Files: camelCase (apiClient.ts, dashboardPage.tsx)
- Components: PascalCase (DashboardSummary.tsx)
- Functions: camelCase (fetchMetrics, formatDate)

### 5.2 API Client Layer

**Location:** `KSysAdmin/frontend/src/api/`

**Files to create:**

- `apiClient.ts`
  - Axios instance with base URL configuration
  - Request interceptor for admin hash key (X-Admin-Key header)
  - Response interceptor for error handling
  - Type-safe HTTP methods

```typescript
import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'http://localhost/api/admin',
  headers: {
    'X-Admin-Key': import.meta.env.VITE_ADMIN_HASH_KEY,
  },
});

export default apiClient;
```

- `metricsApi.ts`
  - Functions: `fetchMetrics()`, `fetchHourlyAggregations()`, `fetchRateLimited()`, `fetchErrors()`
  - All return typed promises

- `healthApi.ts`
  - Functions: `fetchHealthSnapshots()`, `fetchHealthAnalysis()`

- `securityApi.ts`
  - Functions: `fetchSuspiciousActivities()`, `fetchRateLimitViolations()`, `fetchThreatAssessment()`

- `dashboardApi.ts`
  - Functions: `fetchDashboardSummary()`, `fetchServiceHealth()`, `fetchTopIPs()`, `fetchErrorTrend()`

- `aggregationApi.ts`
  - Functions: `triggerHourlyAggregation()`, `triggerSecurityAnalysis()`, `triggerCleanup()`

**Pattern:**
```typescript
export async function fetchDashboardSummary(start: Date, end: Date): Promise<DashboardSummary> {
  const response = await apiClient.get('/dashboard/summary', {
    params: { start: start.toISOString(), end: end.toISOString() },
  });
  return response.data;
}
```

### 5.3 Custom Hooks

**Location:** `KSysAdmin/frontend/src/hooks/`

Use `@tanstack/react-query` for data fetching:

**Files to create:**

- `useMetrics.ts`
  - `useMetrics(service, filters)` - Fetch metrics with caching
  - `useHourlyAggregations(service, dateRange)` - Fetch aggregations
  - Auto-refresh every 30 seconds

- `useHealthSnapshots.ts`
  - `useHealthSnapshots(limit)` - Fetch latest health snapshots
  - `useHealthAnalysis(dateRange)` - Fetch health analysis

- `useSecurity.ts`
  - `useSuspiciousActivities(limit)` - Fetch suspicious activities
  - `useThreatAssessment()` - Fetch threat assessment

- `useDashboard.ts`
  - `useDashboardSummary(dateRange)` - Fetch dashboard summary
  - `useServiceHealth()` - Fetch all service health
  - `useTopIPs(metric, limit)` - Fetch top IPs

**Pattern:**
```typescript
import { useQuery } from '@tanstack/react-query';
import { fetchDashboardSummary } from '../api/dashboardApi';

export function useDashboardSummary(start: Date, end: Date) {
  return useQuery({
    queryKey: ['dashboard', 'summary', start, end],
    queryFn: () => fetchDashboardSummary(start, end),
    refetchInterval: 30000, // Auto-refresh every 30s
  });
}
```

### 5.4 UI Components

**Location:** `KSysAdmin/frontend/src/components/`

Create reusable components:

**Chart Components:**
- `MetricChart.tsx` - Line chart for metrics over time (Recharts)
- `LatencyChart.tsx` - Dual-axis chart (nginx/backend latency)
- `ErrorRateChart.tsx` - Area chart for error rates
- `ServiceHealthChart.tsx` - Bar chart comparing services

**Card Components:**
- `StatCard.tsx` - Display single metric with icon (total requests, error rate, etc.)
- `ServiceCard.tsx` - Service health summary card
- `AlertCard.tsx` - Security alert display

**Table Components:**
- `MetricTable.tsx` - Paginated table for metrics
- `SuspiciousActivityTable.tsx` - Table for security incidents
- `TopIPsTable.tsx` - Table for top IPs

**Filter Components:**
- `DateRangePicker.tsx` - Date range selector (using date-fns)
- `ServiceSelector.tsx` - Dropdown for service selection
- `RefreshControl.tsx` - Manual refresh button + auto-refresh toggle

**Common Components:**
- `LoadingSpinner.tsx` - Loading indicator
- `ErrorMessage.tsx` - Error display
- `EmptyState.tsx` - No data message

### 5.5 Page Components

**Location:** `KSysAdmin/frontend/src/pages/`

**Files to create:**

- `DashboardPage.tsx`
  - Overview page with summary stats
  - Grid layout with StatCards
  - Service health comparison chart
  - Recent alerts section
  - Top IPs table

- `MetricsPage.tsx`
  - Detailed metrics view
  - Filters: service, date range, status
  - MetricChart for trends
  - MetricTable with pagination
  - Export button

- `AggregationsPage.tsx`
  - Hourly aggregations view
  - Service selector
  - Aggregation charts (requests, errors, latency)
  - Data table

- `SecurityPage.tsx`
  - Security monitoring view
  - Threat assessment summary
  - SuspiciousActivityTable
  - Rate limit violations table
  - Manual trigger buttons

- `HealthPage.tsx`
  - System health monitoring
  - Latest health snapshots
  - Health trend charts (DB/Redis latency)
  - Availability percentage

- `SettingsPage.tsx`
  - Admin configuration
  - Manual trigger controls (aggregation, analysis, cleanup)
  - System info display

### 5.6 Routing

**Update:** `KSysAdmin/frontend/src/App.tsx`

```typescript
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import DashboardPage from './pages/DashboardPage';
import MetricsPage from './pages/MetricsPage';
// ... other imports

function App() {
  return (
    <BrowserRouter basename="/admin">
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/metrics" element={<MetricsPage />} />
        <Route path="/aggregations" element={<AggregationsPage />} />
        <Route path="/security" element={<SecurityPage />} />
        <Route path="/health" element={<HealthPage />} />
        <Route path="/settings" element={<SettingsPage />} />
      </Routes>
    </BrowserRouter>
  );
}
```

**Nginx Configuration:**
Update `nginx/nginx.conf` to serve frontend:
```nginx
location /admin/ {
    alias /path/to/KSysAdmin/frontend/dist/;
    try_files $uri $uri/ /admin/index.html;
}
```

### 5.7 State Management

Use React Query for server state (already integrated).

For UI state (filters, date ranges):
- Use React Context for global state (optional)
- Or use component local state with props drilling
- Keep it simple - no Redux needed

### 5.8 Styling

**Options:**
1. **Tailwind CSS** (recommended for rapid development)
2. **CSS Modules** (scoped styles per component)
3. **Styled Components** (CSS-in-JS)

Choose based on preference. Tailwind recommended for consistency.

---

## Phase 6: Security & Polish

**Goal:** Production-ready system with proper security, error handling, and UX polish.

### 6.1 JWT Authentication for Admin

**Current State:** Using static hash key (X-Admin-Key header)
**Goal:** Proper JWT-based authentication

**Backend Changes:**

**Location:** `KSysAdmin/backend/domain/services/`

- `authenticationService.py`
  - `AuthenticationService` class
  - Methods:
    - `authenticateAdmin(username: str, password: str) -> str | None` (returns JWT token)
    - `verifyToken(token: str) -> dict | None` (returns claims)
  - Use shared JWT utilities from `shared/backend/utils/` (if exists) or create
  - Store admin credentials in database or .env (hashed with Argon2)

**Location:** `KSysAdmin/backend/infrastructure/http/dependencies/`

- Update `adminAuth.py`
  - Replace hash key check with JWT verification
  - Extract token from `Authorization: Bearer <token>` header
  - Validate token, extract claims
  - Return admin user info for use in endpoints

**New Endpoints:**

- `POST /auth/login` - Admin login (returns JWT token)
  - Body: `{username, password}`
  - Response: `{access_token, token_type, expires_in}`

- `POST /auth/refresh` - Refresh expired token
- `GET /auth/me` - Get current admin user info

**Frontend Changes:**

- Create login page (`LoginPage.tsx`)
- Store token in localStorage or sessionStorage
- Add token to API client headers
- Implement logout functionality
- Redirect to login on 401 responses

**Important:**
- Use refresh tokens for long-lived sessions
- Set short access token expiry (15-30 min)
- Implement token refresh logic
- Clear tokens on logout

### 6.2 Error Handling

**Backend:**

Already has exception handlers in `shared/backend/exceptions/`.

**Improvements:**
- Add custom exception classes for domain errors
- Return proper HTTP status codes
- Include error details in response (error code, message, details)

**Frontend:**

- Create error boundary component (`ErrorBoundary.tsx`)
- Wrap root app with error boundary
- Display user-friendly error messages
- Log errors to backend (optional error reporting endpoint)
- Toast notifications for errors (use toast library)

**Pattern:**
```typescript
try {
  const data = await fetchMetrics(...);
} catch (error) {
  if (axios.isAxiosError(error)) {
    if (error.response?.status === 401) {
      // Redirect to login
    } else if (error.response?.status === 404) {
      // Show "not found" message
    } else {
      // Generic error
      showToast('Failed to fetch metrics');
    }
  }
}
```

### 6.3 Loading States

**Frontend:**

- Show loading spinners during data fetching
- Skeleton screens for better UX
- Disable buttons during async operations
- Progress indicators for long operations (exports)

**Pattern with React Query:**
```typescript
const { data, isLoading, error } = useDashboardSummary(start, end);

if (isLoading) return <LoadingSpinner />;
if (error) return <ErrorMessage error={error} />;
return <DashboardView data={data} />;
```

### 6.4 Responsive Design

**Frontend:**

- Mobile-first approach
- Breakpoints: mobile (<768px), tablet (768-1024px), desktop (>1024px)
- Responsive grid layouts
- Collapsible sidebar for mobile
- Touch-friendly controls
- Test on multiple screen sizes

**Tailwind Example:**
```tsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
  {/* Cards adjust based on screen size */}
</div>
```

### 6.5 Performance Optimization

**Backend:**

- Add database indexes (already added in models)
- Implement query result caching (Redis)
- Paginate large result sets
- Use database connection pooling (already configured)
- Monitor query performance with slow query log

**Frontend:**

- Code splitting (lazy load pages)
- Memoize expensive computations (`useMemo`, `React.memo`)
- Virtualize long lists (react-window)
- Optimize chart rendering (debounce data updates)
- Bundle optimization (Vite already optimizes)

**Pattern:**
```typescript
const MemoizedChart = React.memo(MetricChart);

const expensiveData = useMemo(() => {
  return processLargeDataset(rawData);
}, [rawData]);
```

### 6.6 Testing

**Backend Testing:**

**Location:** `KSysAdmin/backend/tests/`

Structure:
```
tests/
├── unit/
│   ├── domain/
│   │   └── services/
│   │       ├── test_monitoringService.py
│   │       ├── test_aggregationService.py
│   │       └── test_securityAnalysisService.py
│   └── infrastructure/
│       └── collectors/
│           ├── test_nginxLogParser.py
│           └── test_redisViolationReader.py
├── integration/
│   └── test_metricCollection.py
└── conftest.py
```

**Test Setup:**
- Use pytest with pytest-asyncio
- Mock external dependencies (Redis, database)
- Use fixtures for test data
- Test edge cases and error handling

**Example:**
```python
@pytest.mark.asyncio
async def test_aggregation_service_calculates_correctly(session):
    service = AggregationService(session)
    result = await service.aggregateHour('kauth', datetime(2026, 2, 4, 0))
    assert result.total_requests == 180
    assert result.avg_nginx_latency_ms > 0
```

**Frontend Testing:**

**Tools:**
- Vitest for unit tests
- React Testing Library for component tests
- Mock API responses with MSW (Mock Service Worker)

**Example:**
```typescript
test('renders dashboard summary', async () => {
  render(<DashboardPage />);
  await waitFor(() => {
    expect(screen.getByText('Total Requests')).toBeInTheDocument();
  });
});
```

### 6.7 Documentation

**API Documentation:**
- Already have OpenAPI docs at `/docs`
- Add descriptions to all endpoints
- Document request/response schemas
- Include example requests

**Frontend Documentation:**
- Component documentation (JSDoc comments for props)
- README for setup instructions
- Environment variables documentation

**Deployment Documentation:**
- Production deployment guide
- Environment configuration
- Nginx configuration
- Database migration steps
- Backup procedures

### 6.8 Monitoring & Observability

**Already Implemented:**
- Structured logging (structlog)
- Health check endpoint
- Metric collection

**Enhancements:**
- Add performance metrics (request duration, memory usage)
- Database query performance tracking
- Error rate alerts (integrate with alerting system)
- Dashboard for KSysAdmin itself (meta-monitoring)

### 6.9 Security Hardening

**Backend:**
- Rate limiting on authentication endpoints
- CORS configuration (already in shared)
- Input validation (Pydantic already validates)
- SQL injection prevention (SQLModel/SQLAlchemy handles)
- Secrets management (use .env, never commit secrets)

**Frontend:**
- XSS prevention (React escapes by default)
- CSRF protection (JWT in header, not cookie)
- Content Security Policy headers
- HTTPS only in production

**Nginx:**
- SSL/TLS configuration
- Security headers (X-Frame-Options, etc.)
- Rate limiting (already configured with Redis)

### 6.10 Final Checklist

**Before Production:**

Backend:
- [ ] All endpoints tested with curl/Postman
- [ ] Database migrations applied
- [ ] Environment variables configured
- [ ] Logging configured for production
- [ ] Error handling complete
- [ ] Performance tested with large datasets
- [ ] Security review completed

Frontend:
- [ ] All pages functional
- [ ] Responsive design tested
- [ ] Error boundaries in place
- [ ] Loading states implemented
- [ ] Authentication flow working
- [ ] Production build tested
- [ ] Browser compatibility checked

Infrastructure:
- [ ] Nginx configured for production
- [ ] SSL certificates installed
- [ ] Database backups configured
- [ ] Redis persistence configured
- [ ] Monitoring alerts configured
- [ ] Log rotation configured

---

## Implementation Order Recommendation

**Phase 4 (Backend API):**
1. Create Application DTOs (1-2 hours)
2. Implement DashboardService (2-3 hours)
3. Implement MetricQueryService (2-3 hours)
4. Implement ExportService (2-3 hours)
5. Create HTTP routers (2-3 hours)
6. Test all endpoints (1-2 hours)

**Phase 5 (Frontend):**
1. Setup project dependencies (30 min)
2. Create API client layer (1-2 hours)
3. Create custom hooks with React Query (2-3 hours)
4. Build reusable components (4-6 hours)
5. Create page components (6-8 hours)
6. Implement routing (1 hour)
7. Add styling (2-4 hours)
8. Test in browser (2-3 hours)

**Phase 6 (Security & Polish):**
1. Implement JWT authentication (3-4 hours)
2. Add error handling (2-3 hours)
3. Implement loading states (1-2 hours)
4. Make responsive (2-3 hours)
5. Performance optimization (2-3 hours)
6. Write tests (4-6 hours)
7. Security hardening (2-3 hours)
8. Final testing & deployment (3-4 hours)

---

## Critical Reminders

**Architectural Rules:**
- Domain layer: Pure business logic, no HTTP/DB concerns
- Application layer: DTOs for API contracts
- Infrastructure layer: HTTP, DB, external integrations
- Always use DI (dependency injection)
- Repositories encapsulate all database access
- Services orchestrate business logic

**Code Style:**
- No docstrings
- No emojis
- No nested if statements (use Pydantic validation)
- Use Python magic methods (avoid boilerplate)
- Strict typing, no `Any`
- camelCase functions, PascalCase classes
- `from __future__ import annotations` in every file

**Frontend-Backend Separation:**
- Backend: API-only (JSON responses)
- Frontend: Client-side rendering, handles own routing
- Communication: REST API with fetch/axios
- No SSR, no HTML from backend

**Database:**
- KSysAdmin owns Alembic migrations (source of truth)
- Use Repository Pattern for all DB access
- Async operations (asyncpg, SQLAlchemy async)
- UUID7 for IDs (time-sortable)

**Background Tasks:**
- Use asyncio.create_task for background loops
- Graceful shutdown (cancel tasks on server stop)
- Error handling with retry logic
- Structured logging for debugging

**Deployment:**
- Nginx as reverse proxy/API gateway
- Admin server on port 8002
- Production parity (dev setup mirrors prod)
- Environment variables for all config

---

## Next Steps for Implementation

1. Review this plan thoroughly
2. Start with Phase 4.1 (Application DTOs)
3. Work sequentially through each phase
4. Test each component before moving to next
5. Commit work regularly (per phase or feature)
6. Deploy incrementally (backend first, then frontend)

Good luck with implementation!
