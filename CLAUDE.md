# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Multi-microservices platform using Layered Modular Hexagonal pattern architecture. Currently contains three core services: KAuthApp (authentication), KSysAdmin (admin system), and KSysPayment (payment handling). **New service folders will be added over time** following the same architectural pattern. Company provides various services across different niches, not focused on monolithic architecture.

## Deployment & Scaling Strategy

### Development vs Production
- **Development**: Monorepo with single `pyproject.toml` for rapid development
- **Production**: Each service gets its own `pyproject.toml` and deployed independently
- Package management remains Poetry for both environments

**Production Parity Principle**:
- **CRITICAL**: Development setup MUST mirror production architecture
- User management trio (KAuthApp, KSysAdmin, KSysPayment):
  - Development: Single nginx port → 3 backend ports
  - Production: Same setup (minimize deployment adjustments)
- Use nginx from day 1 in development - NOT optional
- Goal: Zero or minimal config changes when moving to production

### Database Architecture
**User Management Bounded Context** (KAuthApp, KSysAdmin, KSysPayment):
- These three services **share a single PostgreSQL database**
- Justified: all handle user management domain, tightly coupled by design
- Database name convention: should reflect user management context

**Other Services**:
- Each service gets **its own dedicated database**
- No cross-database queries - use inter-service communication instead

### Inter-Service Communication
**Within User Management Context** (KAuthApp ↔ KSysAdmin ↔ KSysPayment):
- **Runtime Architecture**:
  - KAuthApp + KSysPayment run in same uvicorn process (port 8001) - direct function calls
  - KSysAdmin runs in separate uvicorn process (port 8002)
  - Communication between Public Server ↔ Admin Server via internal HTTP if needed
- These three services share database and bounded context
- **CRITICAL**: This combined server pattern is ONLY for user management trio

**Between Different Service Domains** (all other services):
- **Development Environment**: REST API calls for inter-service communication
- **Production**: Will migrate to gRPC (implementation TBD)
- **CRITICAL**: Never use modular monolith pattern for services outside the user management trio
- Each service exposes REST endpoints; maintain loose coupling
- Deployed independently with separate domains (unlike user management trio)

### Orchestration (User Management Trio)
**Nginx as Reverse Proxy/API Gateway - MANDATORY from Day 1**:
- **CRITICAL**: Use nginx in BOTH development and production (production parity)
- **Single port exposure** (e.g., 80/443) for all three services
- Backend services run on different internal ports, nginx routes traffic
- **Development setup MUST mirror production** - no adjustment needed when deploying

**Port Architecture**:
```
Development & Production:
Nginx (Port 80/443) - Single Entry Point
    ├─→ Public Server (port 8001) - KAuthApp + KSysPayment combined
    └─→ Admin Server (port 8002) - KSysAdmin

Only 2 uvicorn servers running, not 3!
```

**Request Routing**:
- `/api/auth/*` → Public Server (port 8001) - KAuthApp routes
- `/api/payment/*` → Public Server (port 8001) - KSysPayment routes
- `/api/admin/*` → Admin Server (port 8002) - KSysAdmin routes
- `/auth/*` → KAuthApp frontend (static files)
- `/payment/*` → KSysPayment frontend (static files)
- `/admin/*` → KSysAdmin frontend (static files)

**Server Structure**:
- **Public Server**: Single FastAPI app combining KAuthApp + KSysPayment routers
  - Uses duplicated SQLModel models (synced with KSysAdmin schema)
  - Database access via **Repository Pattern** with SQLModel queries
  - Focuses on read/write operations, business logic, and controllers
  - Services depend on repositories, never direct queries
- **Admin Server**: Separate FastAPI app for KSysAdmin only
  - Owns original database models (SQLModel definitions)
  - Manages Alembic migrations - source of truth for schema
  - Uses Repository Pattern with SQLModel ORM
  - Can configure system settings (CORS, rate limits) stored in database
- Auth and Payment grouped as public-facing services
- Admin isolated for security and separation of concerns

**Benefits**:
- **Reduced server load**: Only 2 uvicorn processes instead of 3
- **Single port exposure**: All traffic through port 80/443
- **Production parity**: Identical setup dev → prod
- **Easy deployment**: Minimal configuration changes
- **Security**: Admin isolated in separate process
- **Efficient rate limiting**: Rejected at nginx layer before hitting backend
- **Model centralization**: Single source of truth (KSysAdmin owns schema)
- SSL termination, rate limiting via Redis, load balancing, caching

**Other Services** (outside user management trio):
- Each deployed independently with separate domains
- Own nginx instance or different orchestration
- Different ports/domains in production

Configuration in `nginx/nginx.conf`

## Stack

- **Python**: 3.14
- **Backend Framework**: FastAPI (async)
- **Frontend Framework**: React or Astro (per service)
- **ORM**: SQLModel
- **Validation**: Pydantic v2 (strict mode)
- **Package Manager**: Poetry
- **Databases**: PostgreSQL (persistent), Redis (shared - cache/session/pub-sub)
- **Orchestration**: Nginx (reverse proxy/API gateway)
- **Cryptography**: Rust (AES-256-GCM + Argon2id)
- **UUID**: UUID7 (time-sortable, better than UUID4)
- **Logging**: structlog
- **Testing**: pytest
- **Linter**: Ruff
- **Payment Gateway**: BRI Merchant

## Development Commands

### Package Management
```bash
# Install dependencies
poetry install

# Add a new dependency
poetry add <package>

# Update dependencies
poetry update

# Show installed packages
poetry show
```

### Docker & Infrastructure
```bash
# Start infrastructure services (PostgreSQL + Redis)
docker compose up -d

# Stop infrastructure services
docker compose down

# View logs
docker compose logs -f

# Check service status
docker compose ps

# Rebuild containers
docker compose up -d --build
```

### Linting
```bash
# Run linter (when configured)
ruff check .

# Auto-fix issues
ruff check --fix .
```

### Testing
Testing is performed **per-service** with independent test suites.

```bash
# Run all tests (only when instructed)
pytest

# Run tests for specific service backend
pytest KAuthApp/backend/
pytest KSysAdmin/backend/
pytest KSysPayment/backend/

# Run tests for specific service
pytest KAuthApp/
pytest KSysAdmin/
pytest KSysPayment/

# Run specific test file
pytest path/to/test_file.py

# Run with coverage
pytest --cov
```

### Database Migrations (KSysAdmin ONLY)
KSysAdmin owns all schema changes. Never create migrations in KAuthApp or KSysPayment.

```bash
# Create a new migration (from repository root)
cd KSysAdmin/backend/infrastructure/database
alembic revision --autogenerate -m "description of changes"

# Apply migrations (upgrade to latest)
alembic upgrade head

# Downgrade one revision
alembic downgrade -1

# View migration history
alembic history

# View current database version
alembic current
```

**Critical**: After creating migration in KSysAdmin:
1. Update KSysAdmin models first
2. Create Alembic migration
3. Apply migration to database
4. Sync models in KAuthApp and KSysPayment (duplicate the changes)

### Frontend Build (React/Astro)
```bash
# Build frontend for production (from service directory)
cd KAuthApp/frontend && npm run build
cd KSysAdmin/frontend && npm run build

# Development mode (when needed)
cd KAuthApp/frontend && npm run dev

# Install frontend dependencies
cd KAuthApp/frontend && npm install
```

**Important**: Production uses build artifacts only. Backend serves API, frontend handles routing.

### Backend Services (User Management Trio)
```bash
# Start Public Server (KAuthApp + KSysPayment combined)
# Terminal 1
uvicorn public_server:app --port 8001

# Start Admin Server (KSysAdmin)
# Terminal 2
uvicorn admin_server:app --port 8002

# Or use gunicorn for production-like setup
gunicorn public_server:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8001
gunicorn admin_server:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8002
```

**Server Implementation**:
- `public_server.py`: FastAPI app combining KAuthApp + KSysPayment routers
- `admin_server.py`: FastAPI app for KSysAdmin routers
- Both servers access same database (user management bounded context)

### Nginx (Orchestration - REQUIRED)
```bash
# Start nginx with config (MUST run for development)
# Requires OpenResty or lua-nginx-module for Redis integration
nginx -c $(pwd)/nginx/nginx.conf

# Or use OpenResty
openresty -c $(pwd)/nginx/nginx.conf

# Reload nginx config (after changes)
nginx -s reload

# Test nginx config (before reload)
nginx -t

# Stop nginx
nginx -s stop
```

**Nginx + Redis Integration**:
- Nginx queries Redis for rate limiting BEFORE forwarding requests
- Checks: `INCR rate_limit:{user_id}:{endpoint}` or `INCR rate_limit:{ip}:{endpoint}`
- If over limit: return 429, never hits backend
- Requires OpenResty or custom Nginx module with Redis support

**Access points**:
- http://localhost (nginx entry point)
- Backend services NOT accessed directly (use nginx routes)

### Development Startup Order
**CRITICAL**: Services must start in this order to avoid connection errors:

1. **Infrastructure** (PostgreSQL + Redis):
   ```bash
   docker compose up -d
   ```

2. **Rust Crypto Module** (if not installed):
   ```bash
   cd shared/rust-crypto && pip install -e . && cd ../..
   ```

3. **Database Migrations** (KSysAdmin owns schema):
   ```bash
   cd KSysAdmin/backend/infrastructure/database
   alembic upgrade head
   cd ../../../..
   ```

4. **Backend Servers** (2 terminals):
   ```bash
   # Terminal 1: Public Server (Auth + Payment)
   uvicorn public_server:app --port 8001 --reload

   # Terminal 2: Admin Server
   uvicorn admin_server:app --port 8002 --reload
   ```

5. **Nginx** (API Gateway - MANDATORY):
   ```bash
   nginx -c $(pwd)/nginx/nginx.conf
   # Or with OpenResty for Redis rate limiting
   openresty -c $(pwd)/nginx/nginx.conf
   ```

6. **Frontend** (optional, per service):
   ```bash
   cd KAuthApp/frontend && npm run dev
   ```

**Access Points**:
- Main entry: http://localhost (via nginx)
- Health checks: http://localhost:8001/health, http://localhost:8002/health
- Public API: http://localhost/api/auth/*, http://localhost/api/payment/*
- Admin API: http://localhost/api/admin/*
- Direct backend access NOT recommended (breaks production parity)

### Project Structure Generation
```bash
# Regenerate ProjectStructures.md and ProjectStructures.json
./scripts/gen_structures.sh
```

## Architecture Principles

### Hexagonal Architecture Flow (Backend)
**Critical**: Follow this exact flow in all service backends:
```
backend/domain → backend/application/dto → backend/application input|output → backend/infrastructure (http|database)
```

### Frontend-Backend Separation
- **Backend**: API-only, serves JSON responses via REST endpoints
- **Frontend**: Client-side rendered application with own routing
- **Communication**: Frontend fetches data from backend API endpoints
- **Routing**:
  - Frontend handles all UI routes (React Router or Astro routing)
  - Backend only defines API routes (e.g., `/api/users`, `/api/payments`)
  - Backend does NOT serve HTML or handle frontend navigation

### Strict OOP Requirements
1. **All business logic MUST be in `domain/`** - never outside
2. **SQLModel usage**: Domain can use SQLModel for models to prevent boilerplate
3. **Use Dependency Injection (DI) strictly** across all layers
4. **Separate logic from schemas/interfaces** with proper file placement

### Layer Responsibilities (Backend)

**Domain Layer** (`backend/domain/`)
- Pure business logic and domain services
- Domain exceptions (create custom exceptions here, not in service/infrastructure)
- **Model Strategy**:
  - **KSysAdmin**: Defines original database models (SQLModel) - source of truth for schema
  - **KAuthApp & KSysPayment**: Duplicate SQLModel models (same structure as KSysAdmin)
  - **Model duplication is INTENTIONAL** - allows SQLModel queries while maintaining separation
  - **Critical**: KAuthApp/KSysPayment models MUST stay synced with KSysAdmin schema
- Contains core business rules and service logic

**Application Layer** (`backend/application/`)
- DTOs (Data Transfer Objects) / Schemas
- Input/Output models for API requests/responses
- **KAuthApp & KSysPayment**: Define schemas here - represent data structure for read/write operations
- **Schemas are NOT models** - pure Pydantic for validation/serialization
- Application services orchestrating domain logic
- Use cases and application-specific logic

**Infrastructure Layer** (`backend/infrastructure/`)
- HTTP endpoints (FastAPI routers)
- **Repository Pattern** (REQUIRED for database access)
- External service integrations
- **Database Access Pattern**:
  - **All services use Repository Pattern** - no direct SQLModel queries in services
  - Repositories encapsulate database operations with SQLModel queries
  - **KSysAdmin**: Repositories with SQLModel, owns migrations
  - **KAuthApp & KSysPayment**: Repositories with SQLModel using duplicated models
  - All database access MUST go through repository layer
- **Database Migrations** (KSysAdmin ONLY):
  - KSysAdmin owns all Alembic migrations
  - Located in `KSysAdmin/backend/infrastructure/database/alembic/`
  - When schema changes: update KSysAdmin model → create migration → sync KAuthApp/KSysPayment models
  - KAuthApp & KSysPayment have NO migration folders
- Use Application schemas/DTOs for HTTP request/response
- Write session/token metadata to Redis for rate limiting

**Frontend Layer** (`frontend/`)
- Service-specific frontend application
- **Stack**: React or Astro (chosen per service based on requirements)
- **Deployment**: Production build files only (no dev server in production)
- **Routing**: Client-side routing handled by frontend framework (React Router / Astro routing)
- Backend does NOT handle frontend routes - only serves API endpoints
- Consumes backend API from same service via REST/fetch
- Follows same naming conventions (PascalCase folders, camelCase files/functions)

### Shared Modules
Located in `shared/` at repository root. **Scope is intentionally minimal**:

**CRITICAL: ALWAYS CHECK shared/ BEFORE CREATING NEW UTILITIES!**
Before implementing any utility, database connection, logging, crypto, or common functionality, CHECK if it already exists in `shared/`. Many infrastructure components are already implemented.

**What's Already Available in shared/**:

1. **Configuration** (`shared/backend/config/settings.py`)
   - Pydantic settings with .env validation
   - Database, Redis, JWT, CORS, Crypto config
   - Singleton pattern ready to import

2. **Logging** (`shared/backend/loggingFactory.py`)
   - Enhanced structured logging with SystemLogger & UserLogger
   - Categories: Security, Application, Performance, Error, Audit
   - Request context binding for distributed tracing
   - JSON output for production, console for development

3. **Database** (`shared/backend/database/`)
   - `engine.py`: Async SQLAlchemy engine with connection pooling
   - Functions: `initDb()`, `closeDb()`, `getDb()` (FastAPI dependency), `checkConnection()`
   - `baseRepository.py`: Generic CRUD repository pattern (extend this for service repos)

4. **Redis** (`shared/backend/redis/client.py`)
   - Async Redis client with connection pooling
   - Functions: `initRedis()`, `closeRedis()`, `getRedis()` (FastAPI dependency), `checkConnection()`
   - Key naming: `{service}:{type}:{identifier}`

5. **UUID Utilities** (`shared/backend/utils/uuid.py`)
   - `generateId()`: Time-sortable UUID7 generation
   - `parseId()`, `isValidId()`: UUID validation helpers
   - Use UUID7 for better database indexing performance

6. **Cryptography** (`shared/backend/cryptoFactory.py` + `shared/rust-crypto/`)
   - **Rust module** for high-performance encryption (AES-256-GCM + Argon2id)
   - Context-binding encryption via Additional Authenticated Data (AAD)
   - Python wrapper: `CryptoFactory` with `encryptSensitive()`, `decryptSensitive()`

7. **Middleware** (`shared/backend/middleware/`)
   - `corsMiddleware.py`: CORS configuration helper
   - `requestIdMiddleware.py`: Request ID generation and tracing

8. **Exception Handlers** (`shared/backend/exceptions/`)
   - `baseException.py`: Custom exception hierarchy
   - `errorResponse.py`: Standardized error response factory
   - `exceptionHandlers.py`: FastAPI exception handlers
   - Automatically wired to both servers

9. **Health Check** (`shared/backend/health/`)
   - `healthCheck.py`: Component health monitoring
   - Checks: Database, Redis, Crypto with latency measurements
   - Endpoint: `/health` (available on both servers)

**Rust Encryption Module Details**:
- **NOT a server** - pure crypto library module only
- Location: `shared/rust-crypto/`
- Algorithm: **AES-256-GCM** with **Argon2id** key derivation
- Supports **context-binding encryption** via AAD (bind to user_id + device_fingerprint)
- Use cases: prevent replay attacks, bind encrypted data to specific contexts
- Master key stored in `.env` (CRYPTO_MASTER_KEY), salts generated per-record

**Installation Steps** (if not already installed):
```bash
# Simple method using pip (RECOMMENDED)
cd shared/rust-crypto
pip install -e .
cd ../..

# Verify installation
poetry run python -c "import k_services_crypto; print('✓ Rust crypto installed')"

# Test encryption/decryption works
poetry run python -c "
from shared.backend.cryptoFactory import crypto
enc = crypto.encryptSensitive('test data', 'user:123')
dec = crypto.decryptSensitive(enc, 'user:123')
print(f'✓ Crypto works: {dec}')
"
```

**What `pip install -e .` does**:
- Builds Rust code using `cargo build --release`
- Installs Python module in editable mode
- Module becomes available as `k_services_crypto` in virtualenv
- No need for maturin installation

**Usage**:
```python
from shared.backend.cryptoFactory import crypto

# Basic encryption
encrypted = crypto.encryptSensitive("sensitive data", context="user:123")
# Returns: CryptoOutput(ciphertext, salt, nonce)

# Decryption (requires same context)
decrypted = crypto.decryptSensitive(encrypted, context="user:123")
```

**Logging Factory** (`shared/backend/loggingFactory.py`):
- **UserLog**: Audit logs for user actions (login, data mutations, permission changes)
- **SystemLog**: Security, Application, Performance, Error logs (differentiated by type label)
- **JSON output format** with timestamp_ms, category, type, label, message
- Error logs include detailed error information (exception type, message, stack trace)
- Built on structlog for structured logging

**Rate Limiting via Nginx + Redis**:
- **FastAPI writes** session metadata (user_id, token, rate limit counters) to Redis
- **Nginx reads** Redis to check rate limits BEFORE forwarding to backend
- Request rejected at nginx level if rate limit exceeded (429 status)
- No backend processing for rate-limited requests (saves resources)
- Requires nginx with Lua module (OpenResty) or custom Redis integration

**Redis Strategy**:
- **Shared Redis instance** across all services
- Use cases: caching, session management, pub/sub messaging
- Key naming: prefix with service name (e.g., `kauth:session:{id}`, `ksysadmin:cache:{key}`)

**Critical Rules**:
- No business logic in shared
- No domain models in shared
- Keep it minimal - prefer duplication over wrong abstractions
- Used for cross-cutting infrastructure concerns only

Before creating new utilities, check if truly needed across multiple services. If used by only one service, keep it in that service.

## Code Standards

### Naming Conventions
**Universal for Frontend & Backend**:
- **Folders**: PascalCase (e.g., `Domain/`, `Infrastructure/`)
- **Files**: camelCase (e.g., `paymentGateway.py`, `userService.tsx`)
- **Functions/Methods**: camelCase (e.g., `paymentUser()`, `getUserData()`)
- **Classes**: PascalCase (e.g., `PaymentGateway`, `UserService`)

**File Suffix Conventions**:
- Interfaces: `*Interface.py` or `*Interface.tsx` (e.g., `UserInterface.py`)
- Services: `*Service.py` (e.g., `paymentService.py`)
- Repositories: `*Repository.py` (e.g., `userRepository.py`)
- DTOs: `*DTO.py` or `*Input.py`/`*Output.py`

### Type Hints & Python Magic
- **Use `from __future__ import annotations`** at top of every file for forward references
- Use modern Python syntax: `dict`, `list`, `|` (NOT `Dict`, `List`, `Optional`)
- Strict typing everywhere - NO `Any` types
- Maximize Pydantic usage for validation instead of manual checks

**Leverage Python Magic Methods** (avoid manual boilerplate):
- `__repr__`: Auto-generate with dataclasses or Pydantic
- `__str__`: For human-readable output
- `__eq__`, `__hash__`: For comparison and set/dict keys
- `__post_init__`: For post-initialization logic (dataclasses)
- `model_post_init`: For Pydantic models
- Use `@dataclass` or Pydantic BaseModel - never write manual `__init__` with 10+ params
- Use `@property` for computed attributes instead of getter methods
- Use context managers (`__enter__`, `__exit__`) for resource management
- Many AI skip these and write boilerplate - DON'T do that

### Code Quality
- **No docstrings** - code should be self-explanatory
- **No emojis** in code or documentation
- **No nested if statements** - use Pydantic validation instead
- **Clean, modular code** - prefer composition over complexity
- Avoid premature abstractions - three similar lines is better than unnecessary abstraction
- **No manual boilerplate** - use Python magic methods, dataclasses, Pydantic models
- If writing repetitive code (manual __init__, getters/setters), you're doing it wrong

### Configuration
- **Always use environment variables** via `.env` files
- Never hardcode configuration values
- **Maximize `pydantic-settings`** - use BaseSettings for all config classes
- **Maximize FastAPI features**:
  - Use `CORSMiddleware` from `fastapi.middleware.cors` (not manual CORS)
  - Use FastAPI middleware classes (not raw ASGI middleware)
  - Use FastAPI dependency injection (not manual instantiation)
  - Use Pydantic models for request/response validation (not manual checks)
- **No native/manual configuration** - leverage framework features

### Documentation
- Place architectural docs and plans in root or appropriate directories
- NOT in service directories (`KAuthApp/`, etc.)
- Use `.md` format for documentation

### Custom Exceptions & Logging
- Create custom exceptions in `domain/exceptions/`
- Never create exceptions in services or infrastructure
- Use shared logging utilities from `shared/`

## Service Structure

Each service follows identical structure. Current services (KAuthApp, KSysAdmin, KSysPayment) and **any future services** must use this pattern:
```
ServiceName/
├── backend/
│   ├── application/     # DTOs, input/output models, application services
│   ├── domain/          # Business logic, SQLModel domain models, domain exceptions
│   └── infrastructure/  # HTTP routers, database repos, external integrations
└── frontend/            # Frontend application (framework TBD per service)
```

**Structure Notes**:
- Each service is a **full-stack module** with its own backend and frontend
- Backend follows hexagonal architecture (domain → application → infrastructure)
- Frontend is isolated per service, allowing different frameworks if needed
- Folder names follow PascalCase convention

When creating new services, replicate this exact structure. All architectural principles and code standards apply uniformly to all services.

## Important Don'ts

1. **Never create utilities without checking `shared/` first** - Database, Redis, Logging, Crypto, UUID, Repository are already implemented
2. **Never use deprecated Python types** (`Dict`, `List`, `Optional`)
3. **Never write business logic outside `backend/domain/`**
4. **Never create custom interfaces in random files** - follow structure and use `*Interface.py` suffix
5. **Never inject external libs into domain except SQLModel** - SQLModel is allowed for models
6. **Never create exceptions in service/infrastructure** - use `domain/exceptions/`
7. **Never run tests unless explicitly instructed** - testing happens at final stage
8. **Never create docstrings** - maintain clean code without documentation noise
9. **Never use modular monolith pattern outside KAuthApp/KSysAdmin/KSysPayment trio**
10. **Never handle frontend routing in backend** - backend is API-only, frontend handles own routes
11. **Never serve HTML from FastAPI** - frontend build files served separately (nginx/static server)
12. **Never use manual/native config** - maximize pydantic-settings, FastAPI middleware, CORS
13. **Never implement custom crypto algorithms** - use Rust module with proven algorithms (AES-256-GCM)
14. **Never run user management services without nginx** - MUST use nginx from development onwards
15. **Never access backend services directly** - always through nginx (production parity)
16. **Never import models from KSysAdmin into KAuthApp/KSysPayment** - duplicate models instead
17. **Never create Alembic migrations outside KSysAdmin** - KSysAdmin owns all schema changes
18. **Never implement rate limiting in FastAPI** - handled by nginx reading Redis
19. **Never access database directly in services** - use Repository Pattern exclusively
20. **Never let KAuthApp/KSysPayment models drift from schema** - sync after KSysAdmin migrations
21. **Never use UUID4** - use UUID7 for time-sortable, better-indexing IDs
22. **Never write manual boilerplate** - leverage Python magic methods, dataclasses, Pydantic
23. **Never skip `from __future__ import annotations`** - enables forward references and cleaner types
24. **Never assume utilities don't exist** - Check `shared/backend/` for database, redis, logging, crypto, uuid helpers
25. **Never start backend servers before infrastructure** - PostgreSQL and Redis must be running first
26. **Never skip database migrations** - Run `alembic upgrade head` before starting servers

## Reference Materials

If unclear about Pydantic or FastAPI patterns or sqlmodel/sqlalchemy, check `/framework-reference/llms-*.md` files for official documentation references.

## Environment Configuration

Each service has its own `.env` file. Root `.env.example` provides template for required variables.
