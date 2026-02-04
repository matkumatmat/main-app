# Implementation Plan: User-Focused Features

## Summary

Based on user requirements, implementing 3 user-facing feature areas:
1. **User Profile Management** - Update email/phone (with OTP), change password, update profile info, delete account
2. **Enhanced Session Management** - View active sessions, device info, revoke sessions, session history
3. **Access Logging & Analytics** - Track all API requests, view usage analytics, admin global metrics

**Decisions Made:**
- Gateway-agnostic payment design (deferred implementation)
- RBAC with role system (USER, ADMIN) for admin features
- Registered users get default access level (not Anonym)
- Focus on user features first, no payment/plan system yet

## Current Implementation Status

### ✅ FULLY IMPLEMENTED
- User Registration with OTP verification
- Login with OTP (2FA)
- Session management (basic: logout only)
- JWT token generation/validation

### 🔧 PARTIALLY IMPLEMENTED
- Session management exists but lacks: list sessions, view details, revoke all except current, history
- Domain models exist for access logging but no application layer

---

## Feature 1: User Profile Management

### Capabilities
- Get user profile (authenticated user)
- Update profile info (username, company, region)
- Update email with OTP verification
- Update phone with OTP verification
- Change password (require old password verification)
- Delete account (soft delete with password confirmation)

### Domain Layer Changes
**File**: `app/domain/authentication/User.py`

Add methods:
```python
def update_profile_info(username: str | None, company: str | None, region: str | None, updated_time: datetime) -> None
def confirm_email_update(new_email: str, verified_time: datetime) -> None
def confirm_phone_update(new_phone: str, verified_time: datetime) -> None
def change_password(new_hashed_password: str, updated_time: datetime) -> None
def prepare_for_soft_delete(deletion_time: datetime, reason: str | None) -> None
```

**File**: `app/domain/factory/object/ValueObject.py`

Add OtpPurpose enum values:
- `OtpPurpose.EMAIL_UPDATE`
- `OtpPurpose.PHONE_UPDATE`

### Application Layer

**New Directory**: `app/application/user/profile/`

**Files to Create**:
- `IUserProfileService.py` - Protocol interface
- `UserProfileService.py` - Implementation with business logic
- `ProfileDTO.py` - All request/response DTOs

**DTOs**:
- `UserProfileResponseDTO` - Profile data (excludes password)
- `UpdateProfileInfoRequestDTO` - Update username/company/region
- `UpdateEmailRequestDTO` - Initiate email change
- `VerifyEmailUpdateRequestDTO` - Complete email change with OTP
- `UpdatePhoneRequestDTO` - Initiate phone change
- `VerifyPhoneUpdateRequestDTO` - Complete phone change with OTP
- `ChangePasswordRequestDTO` - Old + new password
- `DeleteAccountRequestDTO` - Password confirmation + optional reason

**Service Methods**:
- `get_profile()` - Fetch and map to DTO
- `update_profile_info()` - Update non-sensitive fields directly
- `initiate_email_update()` - Validate uniqueness, create OTP session, send OTP to NEW email
- `verify_email_update()` - Validate OTP, update user.email
- `initiate_phone_update()` - Same pattern as email
- `verify_phone_update()` - Same pattern as email
- `change_password()` - Verify old password with ISalter, hash new password, update
- `delete_account()` - Verify password, mark_deleted(), revoke all sessions

### Infrastructure Layer

**File**: `app/infrastructure/adapter/http/UserProfileController.py` (NEW)

**Endpoints**:
- `GET /profile/me` - Get current user profile (auth required)
- `PUT /profile/info` - Update profile info
- `POST /profile/email/update` - Initiate email update → returns session_id
- `POST /profile/email/verify` - Verify email update with OTP
- `POST /profile/phone/update` - Initiate phone update → returns session_id
- `POST /profile/phone/verify` - Verify phone update with OTP
- `PUT /profile/password` - Change password
- `DELETE /profile/account` - Delete account (soft delete)

### Security Considerations
- All endpoints require valid JWT (extract user_id from token "sub" claim)
- Email/phone updates send OTP to NEW contact (prove ownership before persisting)
- Password change requires old password verification
- Account deletion revokes all sessions immediately
- Check email/phone uniqueness before sending OTP (prevent enumeration)

### Integration Points
- Reuse existing `OtpService` for email/phone verification
- Reuse existing `ISalter` (Cryptography) for password hashing
- Reuse existing `UserSessionManagementService` for session revocation
- Store pending email/phone in session payload, not domain (separation of concerns)

---

## Feature 2: Enhanced Session Management

### Capabilities
- List all active sessions for user
- View detailed session info (device, IP, location, last activity)
- Revoke specific session by ID
- Revoke all sessions EXCEPT current one
- View session history (including revoked/expired)
- Session analytics (device distribution, login patterns)

### Domain/ORM Layer Changes

**File**: `app/infrastructure/orm/models/SessionModel.py`

Add columns:
```python
user_agent: str | None
last_activity_at: datetime | None
device_fingerprint: str | None
location_data: dict | None  # {country, city} from IP geolocation
revoked_at: datetime | None
```

**File**: `app/domain/session/SessionDomain.py`

Add corresponding attributes to dataclass.

### Repository Layer Extensions

**File**: `app/application/user/session/ISessionRepository.py`

Add Protocol methods:
```python
async def find_active_sessions_by_user(user_id: UUID) -> list[SessionDomain]
async def find_all_sessions_by_user(user_id: UUID, include_revoked: bool, include_expired: bool, limit: int, offset: int) -> list[SessionDomain]
async def count_active_sessions_by_user(user_id: UUID) -> int
async def get_session_statistics_by_user(user_id: UUID) -> dict  # Aggregations
async def update_last_activity(session_id: UUID, timestamp: datetime) -> None
async def revoke_all_except(user_id: UUID, except_session_id: UUID) -> int
```

**Implementation**: `DatabaseSessionRepository`, `RedisSessionRepository`, `SessionLookupService`

### Application Layer Extensions

**File**: `app/application/user/session_management/IUserSessionManagement.py`

Add methods to Protocol:
```python
async def get_user_sessions(user_id: UUID, active_only: bool) -> list[SessionDetailDTO]
async def get_session_detail(session_id: UUID, user_id: UUID) -> SessionDetailDTO
async def revoke_all_except_current(user_id: UUID, current_session_id: UUID) -> int
async def get_session_history(user_id: UUID, limit: int, offset: int) -> list[SessionHistoryDTO]
async def get_session_analytics(user_id: UUID) -> SessionAnalyticsDTO
```

**File**: `app/application/user/session_management/SessionManagementDTO.py` (NEW)

DTOs:
- `SessionDetailDTO` - Full session info with is_current flag
- `SessionHistoryDTO` - Simplified for history list
- `SessionAnalyticsDTO` - Aggregated metrics (device breakdown, login patterns, top locations)

### Infrastructure Layer

**File**: `app/infrastructure/adapter/http/AuthenticationController.py`

Add endpoints:
- `GET /auth/sessions` - List user sessions (active_only query param)
- `GET /auth/sessions/{session_id}` - Get session details
- `DELETE /auth/sessions/{session_id}` - Revoke specific session
- `POST /auth/sessions/revoke-all-others` - Revoke all except current
- `GET /auth/sessions/history` - View session history (paginated)
- `GET /auth/sessions/analytics` - Session analytics

**File**: `app/infrastructure/middleware/SessionActivityMiddleware.py` (NEW)

- Intercept all authenticated requests
- Extract session_id from JWT ("sid" claim)
- Update `last_activity_at` asynchronously (Redis only, batch to DB later)
- Never block request pipeline

### Current Session Identification
- JWT payload contains `sid` (session_id)
- Controller extracts `current_user_payload["sid"]` from token
- Pass to service: `revoke_all_except_current(user_id, current_session_id)`
- Repository performs: `UPDATE sessions SET status='revoked' WHERE user_id=? AND id != ?`

### Implementation Notes
- Use composite indexes: `(user_id, status, _deleted_at)`, `(user_id, last_activity_at)`
- Parse user_agent into human-readable format (e.g., "Chrome on Windows 10")
- Optional: IP geolocation for location_data (free service like ip-api.com)
- Middleware updates last_activity with Redis (fast), periodic batch to DB

---

## Feature 3: Access Logging & Analytics

### Capabilities
- Automatic logging of ALL API requests via middleware
- Store: user_id, service_id, endpoint, method, status_code, response_time_ms, IP, user_agent, quota_used
- Query user's own access logs (filtered by date/service/status)
- User analytics: request count, error rate, avg response time
- Admin analytics: global metrics, top users, service health monitoring
- Privacy: anonymize data for Free/Anonym users per architecture.md

### Architecture Strategy

**High-Volume Write Optimization**:
```
Request → Middleware → Redis Queue (fire-and-forget, non-blocking)
                           ↓
                  Background Worker (batch accumulator)
                           ↓
                  PostgreSQL Bulk Insert (100 logs per batch or 5-second timeout)
```

### Domain Layer

**File**: `app/domain/access/ServiceAccessLog.py`

Add methods:
```python
def anonymize(user_plan: str) -> ServiceAccessLog  # Mask IP, hash user_agent for Free/Anonym users
def to_analytics_point() -> tuple[str, int, float]  # Extract (service_id, status, response_time)
```

### Application Layer

**New Directory**: `app/application/access/`

**Files to Create**:
- `IAccessLogQueue.py` - Queue interface (Protocol)
- `IAccessLogRepository.py` - Repository interface
- `AccessLogService.py` - Query and analytics business logic
- `AccessLogBackgroundWorker.py` - Batch processor
- `AccessLogDTO.py` - All DTOs

**DTOs**:
- `AccessLogEntryDTO` - Single log entry (anonymized if needed)
- `AccessLogFilterDTO` - Filter params (service_id, date range, status codes, endpoint pattern)
- `PaginatedLogsDTO` - Paginated log list
- `UserAnalyticsDTO` - User-specific metrics
- `GlobalAnalyticsDTO` - Admin global metrics
- `ServiceHealthDTO` - Per-service health metrics
- `DateRangeDTO` - Date range for queries

**Service Methods**:
- `get_user_logs()` - Query with filters, enforce user_id, anonymize if needed
- `get_user_analytics()` - Aggregate user's request metrics
- `get_admin_global_analytics()` - Admin-only: global request stats, top users
- `get_service_health()` - Admin-only: per-service error rate, avg response time, peak hours

**Background Worker**:
- Start in `lifespan()` startup
- Async loop: dequeue logs from Redis, accumulate batch (size 100 or 5s timeout)
- Flush batch via `repository.batch_insert()`
- Graceful shutdown: flush remaining logs

### Infrastructure Layer

**File**: `app/infrastructure/middleware/AccessLoggingMiddleware.py` (NEW)

- Starlette `BaseHTTPMiddleware` (not dependency - captures ALL requests)
- Capture request start time
- Extract: user_id (from JWT if exists), endpoint, method, IP, user_agent
- After response: calculate response_time_ms, status_code
- Create `ServiceAccessLog` domain object
- Push to Redis queue (async, fire-and-forget)
- Never crash request pipeline (try/except all logging code)

**File**: `app/infrastructure/adapter/repository/RedisAccessLogQueue.py` (NEW)

- Implements `IAccessLogQueue`
- Use Redis Stream (not simple queue): persistence across restarts
- Stream name: "access_logs_stream"
- Methods: `enqueue(log)`, `dequeue()` (blocking with timeout)

**File**: `app/infrastructure/adapter/repository/DatabaseAccessLogRepository.py` (NEW)

- Implements `IAccessLogRepository`
- `batch_insert()`: SQLAlchemy `bulk_insert_mappings()` for performance
- Query methods with SQLAlchemy filters, GROUP BY for aggregations
- Composite indexes: `(user_id, accessed_at)`, `(service_id, accessed_at)`, `(service_id, status_code)`

**File**: `app/infrastructure/orm/models/ServiceAccessLogModel.py` (NEW)

Columns:
- `id`, `user_id`, `service_id`, `endpoint`, `method`, `status_code`, `response_time_ms`
- `ip_address`, `user_agent`, `quota_used`, `error_message`, `request_id`, `accessed_at`

Indexes:
- `ix_user_accessed (user_id, accessed_at)`
- `ix_service_accessed (service_id, accessed_at)`
- `ix_service_status (service_id, status_code)`

**File**: `app/infrastructure/adapter/http/AccessLogController.py` (NEW)

Endpoints:
- `GET /access-logs/me` - User's own logs (paginated, filtered)
- `GET /access-logs/me/analytics` - User analytics
- `GET /access-logs/admin/global` - Admin: global analytics (requires RBAC)
- `GET /access-logs/admin/service/{service_id}/health` - Admin: service health

### Privacy Implementation

**Anonymization Strategy** (in AccessLogService):
- For Free/Anonym users:
  - IP: `192.168.1.1` → `192.168.*.*` (mask last 2 octets)
  - User-agent: Hash to category ("Chrome", "Mobile", etc.)
  - Error messages: Redact details, keep generic status
- Store raw data, anonymize at read time (allows policy changes)

### Performance Expectations
- Middleware overhead: <1ms per request
- Redis queue push: ~1ms async
- Batch insert (100 logs): ~50ms (2000 logs/sec sustained)
- Query with indexes: <100ms for 1M+ rows with date range filter

### Configuration
Environment variables:
- `ACCESS_LOG_BATCH_SIZE=100`
- `ACCESS_LOG_BATCH_TIMEOUT=5`
- `ACCESS_LOG_REDIS_STREAM=access_logs_stream`

---

## Implementation Sequence

### Phase 1: Database Migrations (Alembic)
1. Add columns to `sessions` table (user_agent, last_activity_at, device_fingerprint, location_data, revoked_at)
2. Create `service_access_logs` table with all columns and composite indexes
3. Run migration: `poetry run alembic upgrade head`

### Phase 2: User Profile Management
1. Update `User.py` domain methods
2. Add `OtpPurpose.EMAIL_UPDATE`, `PHONE_UPDATE` to ValueObject
3. Create `app/application/user/profile/` with service, DTOs, interface
4. Create `UserProfileController.py` with 8 endpoints
5. Update `Dependencies.py` to inject `UserProfileService`
6. Test profile operations

### Phase 3: Enhanced Session Management
1. Update `SessionModel.py` ORM and `SessionDomain.py` dataclass
2. Add repository methods to `ISessionRepository` Protocol
3. Implement in `DatabaseSessionRepository`, `RedisSessionRepository`, `SessionLookupService`
4. Create `SessionManagementDTO.py` with DTOs
5. Extend `UserSessionManagementService` with new methods
6. Add 6 endpoints to `AuthenticationController.py`
7. Create `SessionActivityMiddleware.py` and register in `main.py`
8. Test session management

### Phase 4: Access Logging & Analytics
1. Create `ServiceAccessLogModel.py` ORM (run Alembic migration if not done)
2. Add domain methods to `ServiceAccessLog.py`
3. Create `app/application/access/` directory structure
4. Implement `RedisAccessLogQueue.py` (Redis Stream)
5. Implement `DatabaseAccessLogRepository.py` with batch insert
6. Implement `AccessLogService.py` with privacy enforcement
7. Implement `AccessLogBackgroundWorker.py`
8. Create `AccessLoggingMiddleware.py` and register in `main.py`
9. Update `lifespan()` to start/stop background worker
10. Create `AccessLogController.py` with 4 endpoints
11. Test logging and analytics

### Phase 5: RBAC Implementation (for Admin Endpoints)
1. Add `role` column to `users` table (enum: USER, ADMIN)
2. Create `app/infrastructure/adapter/http/dependencies/RbacDependency.py`
3. Implement `require_admin_role()` dependency
4. Apply to admin endpoints in `AccessLogController`
5. Test role-based access control

### Phase 6: Integration & Testing
1. Update `Dependencies.py` with all new service factories
2. Integration tests for profile workflows (update email with OTP, change password, delete account)
3. Integration tests for session management (revoke all, view history)
4. Load test access logging (1000 requests/sec, verify batch processing)
5. End-to-end test: user journey from registration → profile update → session management → view analytics

---

## Critical Files Summary

### Domain Layer
- `app/domain/authentication/User.py` - Add profile management methods
- `app/domain/session/SessionDomain.py` - Add session metadata attributes
- `app/domain/access/ServiceAccessLog.py` - Add anonymization methods
- `app/domain/factory/object/ValueObject.py` - Add OTP purposes, role enum

### Application Layer (NEW)
- `app/application/user/profile/` - Complete profile service, DTOs, interface
- `app/application/access/` - Complete access logging service, worker, DTOs, interfaces

### Application Layer (EXTEND)
- `app/application/user/session_management/UserSessionManagementService.py` - Add methods
- `app/application/user/session_management/SessionManagementDTO.py` - NEW DTOs
- `app/application/user/session/ISessionRepository.py` - Extend Protocol

### Infrastructure Layer (NEW)
- `app/infrastructure/adapter/http/UserProfileController.py` - 8 endpoints
- `app/infrastructure/adapter/http/AccessLogController.py` - 4 endpoints
- `app/infrastructure/middleware/AccessLoggingMiddleware.py` - Request logger
- `app/infrastructure/middleware/SessionActivityMiddleware.py` - Activity tracker
- `app/infrastructure/adapter/repository/RedisAccessLogQueue.py` - Redis Stream
- `app/infrastructure/adapter/repository/DatabaseAccessLogRepository.py` - Batch insert
- `app/infrastructure/orm/models/ServiceAccessLogModel.py` - ORM model

### Infrastructure Layer (EXTEND)
- `app/infrastructure/adapter/http/AuthenticationController.py` - Add 6 session endpoints
- `app/infrastructure/adapter/repository/DatabaseSessionRepository.py` - Implement new methods
- `app/infrastructure/orm/models/SessionModel.py` - Add columns
- `app/infrastructure/dependencies/Dependencies.py` - Add service factories
- `app/main.py` - Register middlewares, update lifespan for background worker

---

## Verification Strategy

### Manual Testing
1. **Profile Management**: Use `/docs` (FastAPI OpenAPI) to test all profile endpoints
2. **Session Management**: Login multiple times (different browsers), list sessions, revoke specific, revoke all others
3. **Access Logging**: Make requests, wait 5 seconds (batch timeout), query logs, verify stored correctly

### Automated Testing
1. Unit tests for domain methods (User profile methods, SessionDomain)
2. Unit tests for services (ProfileService, SessionManagementService, AccessLogService)
3. Integration tests for full workflows (update email with OTP, revoke sessions, log requests)
4. Load test: 1000 concurrent requests, verify logging doesn't degrade performance

### Database Verification
```sql
-- Verify session columns added
SELECT user_agent, last_activity_at FROM sessions LIMIT 5;

-- Verify access logs table created and indexed
SELECT * FROM service_access_logs ORDER BY accessed_at DESC LIMIT 10;

-- Check batch processing (logs should accumulate in batches)
SELECT COUNT(*), DATE_TRUNC('second', accessed_at) FROM service_access_logs GROUP BY DATE_TRUNC('second', accessed_at);
```

### Performance Verification
- Middleware overhead: <1ms (check response times before/after middleware)
- Background worker: 2000 logs/sec sustained write capacity
- Query performance: <100ms for 1M rows with date range filter
