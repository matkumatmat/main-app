# Factory Setup Implementation Plan

**Date**: 2026-02-03
**Scope**: Complete infrastructure factory setup for k-services platform
**Architecture**: Modular Monolith (User Management Trio) + Independent Services

---

## Overview

Setup shared infrastructure factories and base configurations that will be used across all services. Focus on user management trio (KAuthApp, KSysAdmin, KSysPayment) which share database and run as modular monolith.

**Key Principles**:
- Production parity from day 1 (nginx mandatory)
- No manual boilerplate (Python magic methods, Pydantic, dataclasses)
- Single source of truth (KSysAdmin owns schema)
- Repository pattern for all DB access
- Nginx + Redis for rate limiting
- Rust for crypto operations

---

## Phase 1: Core Configuration (Foundation)

**Priority**: CRITICAL - Everything depends on this
**Estimated Complexity**: Low
**Dependencies**: None

### 1.1 Environment Configuration

**File**: `.env` (root)

**Variables to define**:
```bash
# Database (Shared for user management trio)
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/k_user_management
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10

# Redis (Shared across all services)
REDIS_URL=redis://localhost:6379/0
REDIS_MAX_CONNECTIONS=50

# Crypto (Rust module master key)
CRYPTO_MASTER_KEY=<generate_secure_256bit_key>

# JWT
JWT_SECRET_KEY=<generate_secure_key>
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Environment
ENVIRONMENT=development
DEBUG=true

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Server Ports
PUBLIC_SERVER_PORT=8001
ADMIN_SERVER_PORT=8002

# Nginx
NGINX_PORT=80
```

**Actions**:
- Create `.env.example` template
- Generate secure keys using Python secrets module
- Add `.env` to `.gitignore`

---

### 1.2 Pydantic Settings Factory

**File**: `shared/backend/config/settings.py`

**Purpose**: Centralized configuration management using pydantic-settings

**Features**:
- Auto-load from `.env`
- Type validation for all config values
- Singleton pattern
- Environment-specific overrides

**Structure**:
```python
from __future__ import annotations
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database config
    # Redis config
    # Crypto config
    # JWT config
    # CORS config
    # Environment config
    # Logging config
    # Server ports

settings = Settings()  # Singleton
```

**Validation Rules**:
- DATABASE_URL must be valid asyncpg URL
- CRYPTO_MASTER_KEY minimum 32 bytes
- JWT_SECRET_KEY minimum 32 characters
- CORS_ORIGINS must be valid URLs

---

## Phase 2: Logging Infrastructure

**Priority**: HIGH - Needed for debugging all subsequent setup
**Estimated Complexity**: Medium
**Dependencies**: Phase 1 (settings)

### 2.1 Logging Factory

**File**: `shared/backend/loggingFactory.py`

**Purpose**: Structured logging with JSON output

**Categories**:
1. **UserLog** (category: "user")
   - Audit trail for user actions
   - Login, logout, data mutations
   - Permission changes
   - IMMUTABLE logs for compliance

2. **SystemLog** (category: "system")
   - Security: auth failures, brute force, violations
   - Application: business flow, info, debug
   - Performance: slow queries (>500ms), API response times
   - Error: exceptions with stack traces

**Output Format** (JSON):
```json
{
  "timestamp": "2026-02-03T10:30:45.123Z",
  "category": "system",
  "type": "security",
  "service": "KAuthApp",
  "label": "failed_login_attempt",
  "message": "Invalid credentials provided",
  "context": {
    "email": "user@example.com",
    "ip": "192.168.1.1",
    "request_id": "abc-123-def"
  }
}
```

**Error Log Enhanced**:
```json
{
  "category": "system",
  "type": "error",
  "error_detail": {
    "exception_type": "DatabaseError",
    "exception_message": "Connection timeout",
    "stack_trace": "...",
    "context": {...}
  }
}
```

**Implementation**:
- Use structlog with processors
- Bind context per request (request_id, user_id, service)
- Support both JSON and console output (dev vs prod)

---

### 2.2 UUID7 Utility

**File**: `shared/backend/utils/uuid.py`

**Purpose**: Time-sortable UUIDs for better database indexing

**Why UUID7 over UUID4**:
- Time-ordered (better B-tree index performance)
- Chronologically sortable
- Still globally unique
- Better for distributed systems

**Implementation**:
```python
from __future__ import annotations
from uuid_utils import uuid7
import uuid

def generateId() -> uuid.UUID:
    """Generate time-sortable UUID7"""
    return uuid7()
```

**Usage**:
```python
class User(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=generateId, primary_key=True)
```

---

## Phase 3: Data Layer Factories

**Priority**: CRITICAL
**Estimated Complexity**: Medium
**Dependencies**: Phase 1, Phase 2

### 3.1 Database Engine & Session Factory

**File**: `shared/backend/database/engine.py`

**Purpose**: SQLAlchemy async engine with connection pooling

**Features**:
- Async engine with asyncpg driver
- Connection pooling (configurable size)
- Pool pre-ping (connection health checks)
- Pool recycling (1 hour)
- Session factory with FastAPI dependency

**Connection Pool Strategy**:
- Pool size: 20 (per worker)
- Max overflow: 10 (burst capacity)
- Pre-ping: True (validate connections)
- Recycle: 3600s (prevent stale connections)

**Lifecycle**:
- `init_db()`: Called on app startup
- `get_db()`: FastAPI dependency for sessions
- `close_db()`: Called on app shutdown

**Session Management**:
- Auto-commit on success
- Auto-rollback on exception
- Always close sessions
- Log all DB errors

---

### 3.2 Redis Client Factory

**File**: `shared/backend/redis/client.py`

**Purpose**: Async Redis client with connection pooling

**Use Cases**:
- Session storage (user sessions)
- Caching (API responses, computed data)
- Pub/Sub (config updates, real-time events)
- Rate limiting metadata (written by FastAPI, read by nginx)

**Key Naming Convention**:
```
{service}:{type}:{identifier}

Examples:
kauth:session:abc-123-def
kauth:cache:user:email:user@example.com
ksysadmin:config:cors_origins
rate_limit:login:192.168.1.1
rate_limit:payment:user_abc
```

**Features**:
- Connection pool (max 50 connections)
- Decode responses (UTF-8 strings)
- FastAPI dependency pattern
- Lifecycle management (init/close)

---

### 3.3 Base Repository Pattern

**File**: `shared/backend/database/baseRepository.py`

**Purpose**: Generic CRUD operations for SQLModel models

**Why Repository Pattern**:
- Separation of concerns (services don't query directly)
- Testability (mock repositories)
- Consistent data access layer
- Encapsulates SQLModel query logic

**Generic CRUD Methods**:
```python
class BaseRepository(Generic[ModelType]):
    - get_by_id(id: UUID) -> ModelType | None
    - get_all(skip: int, limit: int) -> list[ModelType]
    - create(obj: ModelType) -> ModelType
    - update(obj: ModelType) -> ModelType
    - delete(id: UUID) -> bool
```

**Service-Specific Repositories** (extend base):
```python
# KAuthApp/backend/infrastructure/database/repositories/userRepository.py
class UserRepository(BaseRepository[User]):
    async def get_by_email(self, email: str) -> User | None:
        # Custom query

    async def get_active_users(self) -> list[User]:
        # Custom query
```

**Benefits**:
- No direct SQLModel queries in services
- Centralized query logic
- Easy to add indexes, caching
- Service layer stays clean (business logic only)

---

## Phase 4: Rust Crypto Module

**Priority**: HIGH
**Estimated Complexity**: High
**Dependencies**: Phase 1 (CRYPTO_MASTER_KEY)

### 4.1 Rust Project Structure

**Location**: `shared/rust-crypto/`

**Structure**:
```
shared/rust-crypto/
├── Cargo.toml
├── src/
│   ├── lib.rs           # PyO3 exports
│   ├── cipher.rs        # AES-256-GCM implementation
│   └── key_derivation.rs # Argon2id key derivation
├── tests/
│   └── crypto_tests.rs
└── python/
    └── cryptoBindings.py  # Python wrapper
```

**Dependencies** (Cargo.toml):
```toml
[dependencies]
aes-gcm = "0.10"
argon2 = "0.5"
rand = "0.8"
pyo3 = { version = "0.20", features = ["extension-module"] }
```

---

### 4.2 Encryption Implementation

**Algorithm**: AES-256-GCM (Authenticated Encryption with Associated Data)

**Key Derivation**: Argon2id (password-based KDF)

**Security Features**:
1. **Random salt per encryption** (32 bytes)
2. **Random nonce per encryption** (12 bytes)
3. **Context binding via AAD** (Additional Authenticated Data)
4. **Master key from .env** (never hardcoded)

**Context-Binding Encryption**:
```rust
// Encrypt with user_id + device_fingerprint
encrypt_with_context(
    plaintext: &[u8],
    master_key: &str,
    aad: &[u8]  // "user_id:device_fingerprint"
)

// Returns: ciphertext, salt, nonce
```

**Use Cases**:
- Bind license keys to specific device
- One-time tokens bound to session
- Sensitive data that can't be reused across contexts
- Prevent replay attacks

**Decrypt Requirements**:
- Must provide SAME aad used during encryption
- Different user/device = decrypt FAILS
- Prevents unauthorized access and file sharing

---

### 4.3 Python FFI Bindings

**File**: `shared/backend/cryptoFactory.py`

**Purpose**: Python wrapper around Rust crypto module

**API**:
```python
class CryptoFactory:
    def encryptSensitive(self, data: str) -> dict:
        """Basic encryption"""
        # Returns: {ciphertext, salt, nonce}

    def decryptSensitive(self, encrypted_data: dict) -> str:
        """Basic decryption"""

    def encryptWithBinding(
        self,
        data: str,
        user_id: str,
        device_fingerprint: str
    ) -> dict:
        """Context-bound encryption"""
        # AAD = user_id:device_fingerprint

    def decryptWithBinding(
        self,
        encrypted_data: dict,
        user_id: str,
        device_fingerprint: str
    ) -> str:
        """Context-bound decryption"""
        # Must match original AAD
```

**Build Process**:
```bash
cd shared/rust-crypto
cargo build --release
maturin develop  # Install to Python virtualenv
```

---

## Phase 5: Middleware & Utilities

**Priority**: MEDIUM
**Estimated Complexity**: Low-Medium
**Dependencies**: Phase 2 (logging)

### 5.1 Request ID Middleware

**File**: `shared/backend/middleware/requestIdMiddleware.py`

**Purpose**: Trace requests across services

**Flow**:
1. Extract `X-Request-ID` header (or generate new UUID)
2. Bind to structlog context
3. Add to request.state
4. Include in response headers
5. Clear context after request

**Benefits**:
- Track request flow across logs
- Debug distributed issues
- Correlate frontend/backend errors

**Example Log Output**:
```json
{"request_id": "abc-123", "service": "public_server", "msg": "user login"}
{"request_id": "abc-123", "service": "admin_server", "msg": "fetch roles"}
```

---

### 5.2 CORS Middleware Factory

**File**: `shared/backend/middleware/corsMiddleware.py`

**Purpose**: Dynamic CORS configuration

**Features**:
- Load origins from settings (or database)
- Support credentials
- Method whitelisting
- Max age caching

**Config Source Priority**:
1. Database (KSysAdmin config table) - highest
2. Environment variables (.env)
3. Hardcoded defaults - lowest

**Dynamic Reload**:
- Listen to Redis pub/sub for config updates
- Hot reload without server restart

---

### 5.3 Exception Handlers & Error Response Factory

**File**: `shared/backend/exceptions/errorResponse.py`

**Purpose**: Standardized error responses

**Structure**:
```python
class ErrorDetail(BaseModel):
    code: str           # "USER_NOT_FOUND"
    message: str        # Human-readable
    field: str | None   # For validation errors
    details: dict | None

class ErrorResponse(BaseModel):
    error: ErrorDetail
    request_id: str
    timestamp: datetime
```

**HTTP Exception Mapping**:
```python
404 -> USER_NOT_FOUND
401 -> UNAUTHORIZED
403 -> FORBIDDEN
422 -> VALIDATION_ERROR
429 -> RATE_LIMIT_EXCEEDED
500 -> INTERNAL_SERVER_ERROR
```

**Benefits**:
- Consistent error format
- Frontend knows what to expect
- Easy to parse errors by code
- Includes request_id for debugging

---

## Phase 6: Nginx Configuration

**Priority**: CRITICAL (Production Parity)
**Estimated Complexity**: High
**Dependencies**: Phase 3 (Redis), Phase 1 (settings)

### 6.1 Nginx with OpenResty/Lua

**File**: `nginx/nginx.conf`

**Why OpenResty**:
- Lua scripting in nginx
- Direct Redis access from nginx
- Rate limiting BEFORE hitting backend
- Dynamic configuration

**Installation**:
```bash
# macOS
brew install openresty

# Ubuntu
apt-get install openresty

# Or use OpenResty Docker image
```

---

### 6.2 Rate Limiting Strategy

**Implementation**: Nginx Lua + Redis

**Rate Limit Types**:

1. **Per IP (anonymous users)**:
   - Key: `rate_limit:login:{ip_address}`
   - Limit: 5 requests/minute
   - Endpoints: /api/auth/login, /api/auth/register

2. **Per User (authenticated)**:
   - Key: `rate_limit:payment:{user_id}`
   - Limit: 100 requests/minute
   - Endpoints: /api/payment/*

3. **Admin (very strict)**:
   - Key: `rate_limit:admin:{ip_address}`
   - Limit: 2 requests/second
   - Endpoints: /api/admin/*

**Flow**:
```
1. Request hits nginx
2. Lua script reads Redis: INCR rate_limit:login:{ip}
3. If count == 1: SET EXPIRE 60 seconds
4. If count > limit: Return 429 (no backend hit!)
5. If OK: Forward to FastAPI backend
6. FastAPI writes session metadata to Redis
```

**Benefits**:
- Block at edge (save backend resources)
- No application-level rate limiting needed
- Centralized rate limit logic
- Easy to adjust limits via Redis

---

### 6.3 Nginx Routing Configuration

**Upstream Servers**:
```nginx
upstream public_server {
    server 127.0.0.1:8001 max_fails=3 fail_timeout=30s;
    keepalive 32;
}

upstream admin_server {
    server 127.0.0.1:8002 max_fails=3 fail_timeout=30s;
    keepalive 32;
}
```

**Path-Based Routing**:
```
/api/auth/*     → public_server (port 8001)
/api/payment/*  → public_server (port 8001)
/api/admin/*    → admin_server (port 8002)

/auth/*         → KAuthApp frontend static files
/payment/*      → KSysPayment frontend static files
/admin/*        → KSysAdmin frontend static files
```

**Health Checks**:
```
GET /health → nginx returns 200 (no upstream)
GET /api/auth/health → public_server health
GET /api/admin/health → admin_server health
```

**Headers Added**:
- X-Real-IP
- X-Forwarded-For
- X-Request-ID (if not present)

---

## Phase 7: Service Structure Setup

**Priority**: HIGH
**Estimated Complexity**: High
**Dependencies**: All previous phases

### 7.1 KSysAdmin (Schema Owner)

**Responsibility**:
- Define ALL database models (SQLModel)
- Manage Alembic migrations
- Expose admin APIs
- Store system configuration in database

**Models to Create**:
```python
# models/user.py
class User(SQLModel, table=True):
    id: UUID (UUID7)
    email: str (unique, indexed)
    password_hash: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

# models/role.py
class Role(SQLModel, table=True):
    id: UUID
    name: str (unique)
    description: str
    created_at: datetime

# models/permission.py
class Permission(SQLModel, table=True):
    id: UUID
    resource: str
    action: str (create, read, update, delete)
    role_id: UUID (foreign key)

# models/systemConfig.py
class SystemConfig(SQLModel, table=True):
    key: str (primary key)
    value: str
    category: str (cors, rate_limit, feature_flag)
    service: str (kauth, ksyspayment, global)
    updated_at: datetime
```

**Alembic Setup**:
```bash
cd KSysAdmin/backend/infrastructure/database
alembic init alembic
alembic revision -m "create users table"
alembic upgrade head
```

---

### 7.2 KAuthApp (Public Service)

**Responsibility**:
- Authentication logic (login, register, logout)
- JWT token generation/validation
- Session management (write to Redis)
- Password hashing (Argon2id)

**Models** (duplicate from KSysAdmin):
```python
# domain/models/user.py
# COPY structure from KSysAdmin
# NO migrations here!
class User(SQLModel, table=True):
    # Same structure as KSysAdmin.User
```

**Repositories**:
```python
# infrastructure/database/repositories/userRepository.py
class UserRepository(BaseRepository[User]):
    async def getByEmail(self, email: str) -> User | None
    async def createUser(self, user_data: dict) -> User
    async def updateLastLogin(self, user_id: UUID) -> None
```

**Services**:
```python
# domain/services/authService.py
class AuthService:
    def __init__(self, user_repo: UserRepository, redis: Redis):
        self.user_repo = user_repo
        self.redis = redis

    async def login(self, credentials: LoginInput) -> LoginOutput:
        # 1. Validate credentials
        # 2. Generate JWT token
        # 3. Create session in Redis
        # 4. Log audit event
        # 5. Return token + user info

    async def register(self, data: RegisterInput) -> User:
        # 1. Validate input
        # 2. Hash password (Argon2id)
        # 3. Create user via repository
        # 4. Log audit event
        # 5. Return user
```

---

### 7.3 KSysPayment (Public Service)

**Responsibility**:
- Payment processing (BRI Merchant integration)
- Transaction management
- Payment status tracking

**Models** (duplicate from KSysAdmin):
```python
# domain/models/user.py (if needed)
# domain/models/payment.py (own model)
class Payment(SQLModel, table=True):
    id: UUID (UUID7)
    user_id: UUID (foreign key)
    amount: Decimal
    currency: str
    status: str (pending, completed, failed)
    gateway_transaction_id: str
    created_at: datetime
    updated_at: datetime
```

**Note**: Payment model owned by KSysPayment, migration in KSysAdmin

---

### 7.4 Server Entry Points

**File**: `public_server.py` (root)

**Purpose**: Combined FastAPI app for KAuthApp + KSysPayment

```python
from __future__ import annotations
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from shared.backend.config.settings import settings
from shared.backend.middleware.requestIdMiddleware import RequestIdMiddleware
from shared.backend.database.engine import init_db, close_db
from shared.backend.redis.client import init_redis, close_redis
from KAuthApp.backend.infrastructure.http import authRouter
from KSysPayment.backend.infrastructure.http import paymentRouter

app = FastAPI(title="Public Server", version="1.0.0")

# Middleware
app.add_middleware(RequestIdMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(authRouter, prefix="/api/auth", tags=["auth"])
app.include_router(paymentRouter, prefix="/api/payment", tags=["payment"])

@app.on_event("startup")
async def startup():
    await init_db()
    await init_redis()

@app.on_event("shutdown")
async def shutdown():
    await close_db()
    await close_redis()

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "public_server"}
```

**File**: `admin_server.py` (root)

**Purpose**: Isolated FastAPI app for KSysAdmin

```python
# Similar structure to public_server.py
# Include only admin routers
# Stricter rate limits
# Separate from public-facing services
```

---

## Phase 8: Testing & Validation

**Priority**: CRITICAL
**Estimated Complexity**: Medium
**Dependencies**: All previous phases

### 8.1 Factory Unit Tests

**Test Coverage**:
- Settings loading and validation
- Logging output format
- UUID7 generation
- Database session lifecycle
- Redis connection pooling
- Repository CRUD operations
- Crypto encrypt/decrypt (basic + context-binding)

**Test Framework**: pytest with pytest-asyncio

---

### 8.2 Integration Tests

**Scenarios**:
1. **Full Request Flow**:
   - User request → nginx → rate limit check (Redis) → FastAPI → DB query → response
   - Verify request_id propagation
   - Verify logging at each step

2. **Rate Limiting**:
   - Send 10 requests rapidly
   - Verify 6th request gets 429
   - Verify backend NOT hit for rate-limited requests

3. **Crypto Operations**:
   - Encrypt with context (user_id + device)
   - Attempt decrypt with wrong context (should fail)
   - Verify context binding works

4. **Database Operations**:
   - Create user via KSysAdmin (migration)
   - Query user from KAuthApp (duplicate model)
   - Verify data consistency

---

### 8.3 Development Workflow Verification

**Start Services**:
```bash
# Terminal 1
uvicorn public_server:app --port 8001 --reload

# Terminal 2
uvicorn admin_server:app --port 8002 --reload

# Terminal 3
openresty -p $(pwd)/nginx -c nginx.conf

# Terminal 4
# Watch logs
tail -f logs/*.log
```

**Test Endpoints**:
```bash
# Health checks
curl http://localhost/health
curl http://localhost/api/auth/health
curl http://localhost/api/admin/health

# Register user
curl -X POST http://localhost/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test1234!"}'

# Login
curl -X POST http://localhost/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test1234!"}'

# Test rate limiting (run 6 times rapidly)
for i in {1..6}; do
  curl http://localhost/api/auth/login -X POST
done
```

---

## Implementation Order & Timeline

### Week 1: Foundation
- Day 1-2: Phase 1 (Config) + Phase 2 (Logging, UUID)
- Day 3-4: Phase 3 (Database, Redis, Repository)
- Day 5: Phase 5 (Middleware)

### Week 2: Advanced Features
- Day 1-3: Phase 4 (Rust Crypto Module) - most complex
- Day 4-5: Phase 6 (Nginx + Rate Limiting)

### Week 3: Service Implementation
- Day 1-2: Phase 7.1 (KSysAdmin models + migrations)
- Day 3: Phase 7.2 (KAuthApp structure)
- Day 4: Phase 7.3 (KSysPayment structure)
- Day 5: Phase 7.4 (Server entry points)

### Week 4: Testing & Refinement
- Day 1-2: Phase 8.1 (Unit tests)
- Day 3-4: Phase 8.2 (Integration tests)
- Day 5: Phase 8.3 (Workflow verification) + Documentation

---

## Risk Assessment

### High Risk
1. **Rust Crypto Module** - Complex FFI bindings, build process
   - Mitigation: Start with pure Python prototype, migrate to Rust later

2. **Nginx + Lua Rate Limiting** - Requires OpenResty setup
   - Mitigation: Use Docker OpenResty image for consistency

### Medium Risk
3. **Model Synchronization** - KAuthApp/KSysPayment models must match KSysAdmin
   - Mitigation: Script to copy models, validation tests

4. **Database Connection Pooling** - Tuning for production load
   - Mitigation: Monitor connections, adjust pool size based on testing

### Low Risk
5. **Logging Configuration** - structlog setup
6. **Middleware Implementation** - Standard FastAPI patterns

---

## Success Criteria

- [ ] All factories initialized successfully on startup
- [ ] Logs output in correct JSON format
- [ ] Database queries go through repository pattern only
- [ ] Rate limiting blocks requests at nginx level
- [ ] Crypto encrypt/decrypt with context binding works
- [ ] Models synced between KSysAdmin and public services
- [ ] 2 uvicorn servers running (not 3)
- [ ] Nginx routes requests correctly
- [ ] Request IDs propagate across services
- [ ] Zero crashes under normal operation
- [ ] Development setup identical to production architecture

---

## Next Steps After Factory Setup

1. **Authentication Flow Implementation**
   - Login/logout/register endpoints
   - JWT token generation/validation
   - Session management

2. **Admin Dashboard APIs**
   - User management CRUD
   - Role/permission management
   - System config UI

3. **Payment Integration**
   - BRI Merchant API integration
   - Payment webhook handling
   - Transaction status tracking

4. **Frontend Setup**
   - React/Astro project initialization
   - API client generation
   - Build process integration with nginx

---

## Dependencies & Prerequisites

**System Requirements**:
- Python 3.14
- PostgreSQL 15+
- Redis 7+
- OpenResty (nginx with Lua)
- Rust toolchain (cargo, rustc)
- maturin (Python-Rust build tool)

**Python Packages** (key ones):
```toml
fastapi = "^0.110.0"
uvicorn = {extras = ["standard"], version = "^0.27.0"}
sqlmodel = "^0.0.16"
sqlalchemy = {extras = ["asyncio"], version = "^2.0.27"}
asyncpg = "^0.29.0"
redis = {extras = ["hiredis"], version = "^5.0.1"}
pydantic-settings = "^2.2.1"
structlog = "^24.1.0"
python-jose = {extras = ["cryptography"], version = "^3.3.0"}
argon2-cffi = "^23.1.0"
uuid-utils = "^0.9.0"
```

**Rust Dependencies**:
```toml
[dependencies]
aes-gcm = "0.10"
argon2 = "0.5"
rand = "0.8"
pyo3 = "0.20"
```

---

## Questions to Resolve Before Implementation

1. **Database name**: `k_user_management` or something else?
2. **JWT token expiry**: 30 minutes access + 7 days refresh OK?
3. **Rate limit values**: Current suggestions reasonable?
4. **Nginx port**: 80 for dev, or different port (avoid sudo)?
5. **Docker**: Use Docker Compose or native installs for dev?
6. **Frontend ports**: 3000 (React), 5173 (Astro) - confirm?
7. **Monitoring**: Add Prometheus/Grafana now or later?

---

**END OF PLAN**

Ready untuk review dan adjustment sebelum mulai implementasi!
