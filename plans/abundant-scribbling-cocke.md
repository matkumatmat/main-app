# Authentication Services - Full Initialization Plan

## Executive Summary

Initialize production-ready authentication microservice following strict hexagonal architecture. The codebase has complete domain layer and port interfaces but requires:
1. **Critical fixes** to port interfaces (architectural violations)
2. **Application services** implementing all use cases
3. **Infrastructure adapters** (HTTP routes, database repositories)
4. **FastAPI application** setup with middleware and DI
5. **Configuration** layer (database, Redis, environment)

**Current Status:** Architecture complete (52+ domain files), implementation missing
**Target:** Full working authentication service with registration, login, session management

---

## Phase 1: Critical Fixes (MUST DO FIRST)

### Issue 1: Port Interface Type Violations ⚠️ CRITICAL
**File:** `app/application/port/output/IUserRepository.py`

**Problem:** All methods use `LoginUserRequestDTO` instead of domain `User` entity
- Lines 3, 10, 17, 24, 30, 37

**Fix:** Change all occurrences:
```python
# WRONG (current)
from app.application.dto.AuthenticationDTO import LoginUserRequestDTO
async def find_by_id(self, user_id: UUID) -> LoginUserRequestDTO | None

# CORRECT (required)
from app.domain.authentication.User import User
async def find_by_id(self, user_id: UUID) -> User | None
```

**Rationale:** Output ports define domain-level contracts. Using DTOs violates hexagonal architecture. Infrastructure adapters handle DTO ↔ domain conversion.

**Also check:** Other output port interfaces for similar issues

### Issue 2: Missing DTO Import
**File:** `app/application/utils/SessionFactory.py` line 4

**Problem:** Imports non-existent `AuthenticationResult`

**Fix:** Change to:
```python
from app.application.dto.AuthenticationDTO import AuthenticationResponseDTO
# Update line 34, 75 return type and line 75 constructor
```

### Issue 3: Exception Import Paths
**File:** `app/shared/TokenGenerator.py` and others

**Problem:** Import from `app.domain.exceptions.*` (incorrect path)

**Fix:** Change to `app.domain.factory.exception.*`

---

## Phase 2: Configuration Layer

### 2.1 Environment Settings
**File:** `app/env/Settings.py` (NEW)

Create nested Pydantic v2 settings with strict validation:
```python
class DatabaseSettings(BaseSettings):
    database_url: PostgresDsn
    pool_size: int = 10
    max_overflow: int = 20
    echo: bool = False

class RedisSettings(BaseSettings):
    redis_url: RedisDsn
    max_connections: int = 50

class JWTSettings(BaseSettings):
    secret_key: SecretStr
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30

class CryptoSettings(BaseSettings):
    password_salt: SecretStr
    encryption_key: SecretStr

class ServerSettings(BaseSettings):
    environment: EnvironmentType
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    allowed_origins: list[str]

class Settings(BaseSettings):
    database: DatabaseSettings
    redis: RedisSettings
    jwt: JWTSettings
    crypto: CryptoSettings
    server: ServerSettings

    model_config = SettingsConfigDict(
        env_file=".env",
        env_nested_delimiter="__"
    )
```

**Environment variables:** Use double underscore for nesting
- `DATABASE__URL=postgresql+asyncpg://...`
- `JWT__SECRET_KEY=...`

### 2.2 Database Connection
**File:** `app/config/database/DatabaseConnection.py` (NEW)

```python
class DatabaseConnection(ABC):
    @abstractmethod
    async def get_session() -> AsyncGenerator[AsyncSession, None]
    @abstractmethod
    async def close()

class AsyncPostgresConnection(DatabaseConnection):
    def __init__(self, settings: DatabaseSettings):
        self._engine: AsyncEngine
        self._session_factory: async_sessionmaker

    async def initialize():
        # Create async engine with asyncpg
        # Create session factory

    async def get_session():
        # Yield session, auto-commit/rollback
```

**Key:** Use `create_async_engine` with `asyncpg` driver

### 2.3 Unit of Work
**File:** `app/config/database/UnitOfWork.py` (NEW)

```python
class IUnitOfWork(ABC):
    @abstractmethod
    async def commit()
    @abstractmethod
    async def rollback()
    # Context manager protocol

class SQLAlchemyUnitOfWork(IUnitOfWork):
    def __init__(self, session: AsyncSession):
        self._session = session
    # Implement transaction boundary management
```

**Key:** UnitOfWork manages transactions, injected per request

### 2.4 Redis Connection
**File:** `app/config/server/RedisConnection.py` (NEW)

```python
class RedisConnection:
    def __init__(self, settings: RedisSettings):
        self._client: redis.asyncio.Redis

    async def initialize()
    async def get_client() -> redis.asyncio.Redis
    async def close()
```

---

## Phase 3: Infrastructure - Database Layer

### 3.1 SQLAlchemy Models
**Location:** `app/infrastructure/adapter/output/database/model/`

**Create files:**
1. `BaseModel.py` - Declarative base + TimestampMixin
2. `UserModel.py` - Users table
3. `SessionModel.py` - Sessions table
4. `AuthProviderModel.py` - Auth providers table
5. `OtpCodeModel.py` - OTP codes table
6. `ApiKeyModel.py` - API keys table
7. `ServiceModel.py` - Services table
8. `PlanModel.py` - Plans table
9. `UserPlanModel.py` - User subscriptions table

**BaseModel structure:**
```python
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class BaseModel(DeclarativeBase):
    pass

class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(nullable=False)
    updated_at: Mapped[datetime] = mapped_column(nullable=False)
```

**UserModel example:**
```python
class UserModel(BaseModel, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    email: Mapped[str | None] = mapped_column(String(255), unique=True, index=True)
    phone: Mapped[str | None] = mapped_column(String(20), unique=True, index=True)
    password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(default=False)
    is_verified: Mapped[bool] = mapped_column(default=False)
    is_deleted: Mapped[bool] = mapped_column(default=False)
    # ... other fields from domain User entity
```

**Important:** SQLAlchemy models are pure data structures with NO business logic. Use `Mapped[]` with type annotations (modern SQLAlchemy 2.0 style).

### 3.2 Domain Mappers
**Location:** `app/infrastructure/adapter/output/database/mapper/`

**Create files:**
1. `UserMapper.py`
2. `SessionMapper.py`
3. `AuthProviderMapper.py`
4. `OtpCodeMapper.py`
5. `ApiKeyMapper.py`
6. `ServiceMapper.py`
7. `PlanMapper.py`
8. `UserPlanMapper.py`

**Mapper pattern:**
```python
class UserMapper:
    @staticmethod
    def to_domain(model: UserModel) -> User:
        return User(
            id=model.id,
            username=model.username,
            email=model.email,
            # ... all fields
        )

    @staticmethod
    def to_model(entity: User) -> UserModel:
        return UserModel(
            id=entity.id,
            username=entity.username,
            # ... all fields
        )
```

**Key:** Mappers are stateless. Bidirectional conversion between SQLAlchemy ↔ domain entities.

### 3.3 Repository Implementations
**Location:** `app/infrastructure/adapter/output/database/repository/`

**Create files:**
1. `UserRepository.py` - Implements `IUserRepository`
2. `SessionRepository.py` - Implements `ISessionRepository`
3. `AuthProviderRepository.py` - Implements `IAuthProviderRepository`
4. `OtpCodeRepository.py` - Implements `IOtpCodeRepository`
5. `ApiKeyRepository.py` - Implements `IApiKeyRepository`
6. `ServiceRepository.py` - Implements `IServiceRepository`

**Repository pattern:**
```python
class UserRepository(IUserRepository):
    def __init__(self, session: AsyncSession, mapper: UserMapper):
        self._session = session
        self._mapper = mapper

    async def find_by_id(self, user_id: UUID) -> User | None:
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._mapper.to_domain(model) if model else None

    async def save(self, user: User) -> None:
        model = self._mapper.to_model(user)
        self._session.add(model)
        # NO commit here - UnitOfWork handles it
```

**Key:** Repositories receive `AsyncSession` via DI, never manage transactions. Return domain entities, not models.

### 3.4 External Service Adapters
**Location:** `app/infrastructure/adapter/output/external/`

**Create files:**
1. `JwtService.py` - Implements `IJwtService` using `JwtTokenGenerator` from shared
2. `TransactionLogger.py` - Implements `ITransactionLogger` using structlog

**JwtService structure:**
```python
class JwtService(IJwtService):
    def __init__(
        self,
        token_generator: JwtTokenGenerator,
        jwt_settings: JWTSettings,
        datetime_converter: DateTimeProtocol
    ):
        # Store dependencies

    def create_access_token(self, user_id: UUID, session_id: UUID, scopes: list[str]) -> str:
        payload = {"user_id": str(user_id), "session_id": str(session_id), "type": "access"}
        expires_delta = timedelta(minutes=self._settings.access_token_expire_minutes)
        return self._generator.generate(payload, expires_delta)

    def create_refresh_token(self, session_id: UUID) -> str:
        # Similar pattern
```

---

## Phase 4: Application Services

### 4.1 Service Structure
**Location:** `app/application/service/`

**Create files:**
1. `RegisterUserService.py` - Implements `IRegisterUser`
2. `AuthenticateUserService.py` - Implements `IAuthenticateUser`
3. `RegisterUserSessionService.py` - Implements `IRegisterUserSession`
4. `RevokeUserSessionService.py` - Implements `IRevokeUserSession`
5. `LinkProviderUserService.py` - Implements `ILinkProviderUser`

**Pattern:** One service per input port (Single Responsibility Principle)

### 4.2 RegisterUserService
**Dependencies:**
- `IUserRepository`, `IOtpCodeRepository`, `IAuthProviderRepository` (output ports)
- `Salter`, `UuidGeneratorProtocol`, `DateTimeProtocol` (shared utilities)
- `OtpCodeFactory` (application utils)
- `IUnitOfWork` (transaction management)

**Key methods:**
```python
class RegisterUserService(IRegisterUser):
    def __init__(
        self,
        user_repo: IUserRepository,
        otp_repo: IOtpCodeRepository,
        auth_provider_repo: IAuthProviderRepository,
        salter: Salter,
        uuid_gen: UuidGeneratorProtocol,
        datetime_conv: DateTimeProtocol,
        otp_factory: OtpCodeFactory,
        uow: IUnitOfWork
    ):
        # Store dependencies

    async def execute(self, request: RegisterUserRequestDTO) -> UUID:
        # 1. Check existing user by email/phone
        # 2. Hash password using Salter
        # 3. Create User domain entity
        # 4. Generate OTP if contact provided
        # 5. Save user via repository
        # 6. Save OTP if generated
        # 7. Commit via UnitOfWork
        # 8. Return user_id

    async def verify_email(self, user_id: UUID, otp_code: str) -> None:
        # 1. Find user and OTP
        # 2. Validate OTP (not expired, code matches)
        # 3. Mark user as verified
        # 4. Mark OTP as used
        # 5. Commit

    async def verify_phone(self, user_id: UUID, otp_code: str) -> None:
        # Similar to verify_email

    async def resend_verification_otp(self, user_id: UUID, via: str) -> None:
        # 1. Find user
        # 2. Generate new OTP
        # 3. Save OTP
        # 4. Commit
```

**Key:** Services orchestrate domain logic by calling domain methods and coordinating repositories. Raise domain exceptions (UserAlreadyExistsException, etc.).

### 4.3 AuthenticateUserService
**Dependencies:**
- `IUserRepository`, `ISessionRepository`, `IOtpCodeRepository`, `IAuthProviderRepository`
- `IJwtService`
- `Salter`, `SessionFactory`
- `IUnitOfWork`

**Key methods:**
```python
class AuthenticateUserService(IAuthenticateUser):
    async def auth_email(
        self,
        email: str,
        password: str,
        otp_code: str | None = None,
        device_info: str | None = None,
        ip_address: str | None = None
    ) -> AuthenticationResponseDTO:
        # 1. Find user by email
        # 2. Call user.can_authenticate() (domain method)
        # 3. Verify password using Salter
        # 4. Validate OTP if required
        # 5. Create session using SessionFactory
        # 6. Save session
        # 7. Commit
        # 8. Return AuthenticationResponseDTO with tokens

    async def auth_phone(self, phone: str, password: str, ...) -> AuthenticationResponseDTO:
        # Similar pattern

    async def auth_oauth2(
        self,
        provider_code: str,
        oauth_token: str,
        device_info: str | None = None,
        ip_address: str | None = None
    ) -> AuthenticationResponseDTO:
        # OAuth authentication flow
```

### 4.4 RevokeUserSessionService
```python
class RevokeUserSessionService(IRevokeUserSession):
    async def revoke_session(self, user_id: UUID, session_id: UUID) -> None:
        # 1. Find session
        # 2. Verify ownership
        # 3. Call session domain method to revoke
        # 4. Update via repository
        # 5. Commit

    async def revoke_all_user_sessions(self, user_id: UUID) -> None:
        # Revoke all active sessions for user
```

### 4.5 LinkProviderUserService
```python
class LinkProviderUserService(ILinkProviderUser):
    async def link_provider(self, user_id: UUID, provider_code: str, oauth_token: str) -> None:
        # 1. Find user
        # 2. Verify OAuth token with external provider
        # 3. Create AuthProvider domain entity
        # 4. Save
        # 5. Commit
```

---

## Phase 5: HTTP Layer (FastAPI Routes)

### 5.1 Router Structure
**Location:** `app/infrastructure/adapter/input/http/`

**Create files:**
1. `AuthenticationRouter.py` - `/auth/*` endpoints
2. `SessionRouter.py` - `/sessions/*` endpoints
3. `UserRouter.py` - `/users/*` endpoints
4. `ServiceRouter.py` - `/services/*` endpoints
5. `PlanRouter.py` - `/plans/*` endpoints

### 5.2 AuthenticationRouter
**Key endpoints:**
```python
router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/register", response_model=RegisterResponseDTO, status_code=201)
async def register_user(
    request: RegisterUserRequestDTO,
    service: IRegisterUser = Depends(get_register_service)
) -> RegisterResponseDTO:
    user_id = await service.execute(request)
    return RegisterResponseDTO(user_id=user_id, message="Registration initiated")

@router.post("/verify/email", status_code=200)
async def verify_email(
    request: VerifyEmailRequestDTO,
    service: IRegisterUser = Depends(get_register_service)
):
    await service.verify_email(request.user_id, request.otp_code)
    return {"message": "Email verified"}

@router.post("/login/email", response_model=AuthenticationResponseDTO)
async def login_email(
    request: LoginEmailRequestDTO,
    service: IAuthenticateUser = Depends(get_auth_service)
) -> AuthenticationResponseDTO:
    return await service.auth_email(
        email=request.email,
        password=request.password,
        otp_code=request.otp_code,
        device_info=request.device_info,
        ip_address=request.ip_address
    )

@router.post("/login/phone", response_model=AuthenticationResponseDTO)
async def login_phone(...)

@router.post("/oauth/{provider}", response_model=AuthenticationResponseDTO)
async def oauth_login(...)

@router.post("/refresh", response_model=RefreshTokenResponseDTO)
async def refresh_token(...)
```

### 5.3 SessionRouter
```python
router = APIRouter(prefix="/sessions", tags=["sessions"])

@router.get("/active", response_model=list[SessionResponseDTO])
async def get_active_sessions(
    current_user: User = Depends(get_current_user),
    session_repo: ISessionRepository = Depends(get_session_repository)
):
    sessions = await session_repo.find_active_by_user(current_user.id)
    return [SessionResponseDTO.from_domain(s) for s in sessions]

@router.delete("/{session_id}", status_code=204)
async def revoke_session(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    service: IRevokeUserSession = Depends(get_revoke_service)
):
    await service.revoke_session(current_user.id, session_id)
```

### 5.4 HTTP DTOs (Optional - if needed separate from application DTOs)
**Location:** `app/infrastructure/adapter/input/http/dto/`

Create HTTP-specific request/response DTOs if API contracts differ from application DTOs.

---

## Phase 6: Middleware

### 6.1 Exception Handler
**File:** `app/infrastructure/adapter/input/middleware/ExceptionHandler.py` (NEW)

```python
def register_exception_handlers(app: FastAPI):
    @app.exception_handler(DomainException)
    async def domain_exception_handler(request: Request, exc: DomainException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.message, "details": exc.details}
        )

    @app.exception_handler(ValidationError)
    async def validation_handler(request: Request, exc: ValidationError):
        return JSONResponse(status_code=422, content={"error": "Validation failed"})

    @app.exception_handler(Exception)
    async def generic_handler(request: Request, exc: Exception):
        # Log and return 500
```

### 6.2 Logging Middleware
**File:** `app/infrastructure/adapter/input/middleware/LoggingMiddleware.py` (NEW)

Use structlog for structured logging of all requests.

### 6.3 Authentication Dependency
**Location:** `app/infrastructure/dependencies/Dependencies.py`

```python
async def get_current_user(
    request: Request,
    jwt_service: IJwtService = Depends(get_jwt_service),
    session_repo: ISessionRepository = Depends(get_session_repository),
    user_repo: IUserRepository = Depends(get_user_repository)
) -> User:
    # 1. Extract Bearer token from Authorization header
    # 2. Decode using jwt_service
    # 3. Validate session is active
    # 4. Load and return user
    # Raises: TokenExpiredException, SessionExpiredException
```

**Usage:** Add `current_user: User = Depends(get_current_user)` to protected endpoints

---

## Phase 7: Dependency Injection

### 7.1 DI Container
**File:** `app/infrastructure/dependencies/Container.py` (NEW)

```python
class Container:
    def __init__(self, settings: Settings):
        self._settings = settings
        self._db_connection: DatabaseConnection | None = None
        self._redis_connection: RedisConnection | None = None

        # Singletons
        self._datetime_converter: DateTimeProtocol | None = None
        self._uuid_generator: UuidGeneratorProtocol | None = None
        self._salter: Salter | None = None
        self._jwt_generator: JwtTokenGenerator | None = None

    async def initialize(self):
        # Initialize database connection
        self._db_connection = AsyncPostgresConnection(self._settings.database)
        await self._db_connection.initialize()

        # Initialize Redis
        self._redis_connection = RedisConnection(self._settings.redis)
        await self._redis_connection.initialize()

        # Initialize singletons
        self._datetime_converter = DateTimeConverter()
        self._uuid_generator = UUIDv7Generator()
        self._salter = Salter(self._settings.crypto.password_salt.get_secret_value())
        self._jwt_generator = JwtTokenGenerator(
            secret_key=self._settings.jwt.secret_key.get_secret_value(),
            datetime_converter=self._datetime_converter
        )

    async def shutdown(self):
        if self._db_connection:
            await self._db_connection.close()
        if self._redis_connection:
            await self._redis_connection.close()

    # Factory methods for scoped dependencies
    def get_user_repository(self, session: AsyncSession) -> IUserRepository:
        return UserRepository(session, UserMapper())

    def get_register_service(self, session: AsyncSession, uow: IUnitOfWork) -> IRegisterUser:
        return RegisterUserService(
            user_repo=self.get_user_repository(session),
            otp_repo=self.get_otp_repository(session),
            auth_provider_repo=self.get_auth_provider_repository(session),
            salter=self._salter,
            uuid_gen=self._uuid_generator,
            datetime_conv=self._datetime_converter,
            otp_factory=OtpCodeFactory(...),
            uow=uow
        )

    # ... other service factories
```

### 7.2 FastAPI Dependencies
**File:** `app/infrastructure/dependencies/Dependencies.py` (NEW)

```python
_container: Container | None = None

def init_container(settings: Settings) -> Container:
    global _container
    _container = Container(settings)
    return _container

def get_container() -> Container:
    return _container

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    container = get_container()
    async with container._db_connection.get_session() as session:
        yield session

async def get_uow(session: AsyncSession = Depends(get_db_session)) -> IUnitOfWork:
    return SQLAlchemyUnitOfWork(session)

async def get_register_service(
    session: AsyncSession = Depends(get_db_session),
    uow: IUnitOfWork = Depends(get_uow)
) -> IRegisterUser:
    return get_container().get_register_service(session, uow)

async def get_auth_service(
    session: AsyncSession = Depends(get_db_session),
    uow: IUnitOfWork = Depends(get_uow)
) -> IAuthenticateUser:
    return get_container().get_authenticate_service(session, uow)

# ... other dependencies
```

---

## Phase 8: FastAPI Application

### 8.1 Main Application
**File:** `app/main.py` (REPLACE CURRENT)

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import structlog

from app.env.Settings import Settings
from app.infrastructure.dependencies.Container import Container
from app.infrastructure.dependencies.Dependencies import init_container
from app.infrastructure.adapter.input.http.AuthenticationRouter import router as auth_router
from app.infrastructure.adapter.input.http.SessionRouter import router as session_router
from app.infrastructure.adapter.input.middleware.ExceptionHandler import register_exception_handlers

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    settings = Settings()
    container = init_container(settings)
    await container.initialize()

    # Configure structlog
    structlog.configure(...)

    yield

    # Shutdown
    await container.shutdown()

def create_app() -> FastAPI:
    settings = Settings()

    app = FastAPI(
        title="Authentication Services",
        version="0.1.0",
        description="Scalable authentication microservice",
        lifespan=lifespan,
        docs_url="/docs" if settings.server.debug else None
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.server.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )

    # Exception handlers
    register_exception_handlers(app)

    # Routes
    app.include_router(auth_router)
    app.include_router(session_router)
    # ... other routers

    # Health check
    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}

    return app

app = create_app()
```

**Key:** Use lifespan context manager for startup/shutdown. Container initialized once, shared globally.

---

## Phase 9: Database Setup

### 9.1 Alembic Migrations
**Setup:**
1. Initialize Alembic: `alembic init alembic`
2. Configure `alembic/env.py`:
   - Import all SQLAlchemy models
   - Set `target_metadata = BaseModel.metadata`
   - Configure async engine
3. Generate migration: `alembic revision --autogenerate -m "Initial schema"`
4. Review and apply: `alembic upgrade head`

### 9.2 Seed Data
**File:** `scripts/seed_database.py` (UPDATE EXISTING)

Seed default data:
- Plans: Anonym (1/day), Free (50/day), Pro (1000/day), Enterprise (unlimited)
- Services: 3dbinpacking, cvmaker, jobportal, media_information, etc. (10 services)

---

## Implementation Order

### Week 1: Foundation & Fixes
1. ✅ Fix `IUserRepository.py` return types (User not DTO)
2. ✅ Fix `SessionFactory.py` import
3. ✅ Fix exception import paths
4. ✅ Create `Settings.py`
5. ✅ Create `DatabaseConnection.py` and `UnitOfWork.py`
6. ✅ Create `RedisConnection.py`

### Week 2: Database Layer
7. ✅ Create all SQLAlchemy models
8. ✅ Create all mappers
9. ✅ Create repository implementations
10. ✅ Create `JwtService.py` and `TransactionLogger.py`
11. ✅ Setup Alembic and run migrations

### Week 3: Application Services
12. ✅ Create `RegisterUserService.py`
13. ✅ Create `AuthenticateUserService.py`
14. ✅ Create `RevokeUserSessionService.py`
15. ✅ Create `LinkProviderUserService.py`

### Week 4: HTTP Layer
16. ✅ Create `AuthenticationRouter.py`
17. ✅ Create `SessionRouter.py`
18. ✅ Create `UserRouter.py`, `ServiceRouter.py`, `PlanRouter.py`
19. ✅ Create exception handler middleware
20. ✅ Create DI `Container.py` and `Dependencies.py`
21. ✅ Implement `main.py` with lifespan

### Week 5: Integration & Testing
22. ✅ Seed database with plans/services
23. ✅ Write unit tests for services
24. ✅ Write integration tests
25. ✅ Write E2E tests for endpoints

---

## Critical Files to Create/Modify

### Must Fix First (Architectural Issues):
1. `app/application/port/output/IUserRepository.py` - Change DTO → User
2. `app/application/utils/SessionFactory.py` - Fix import

### Must Create (Foundation):
3. `app/env/Settings.py` - Environment configuration
4. `app/config/database/DatabaseConnection.py` - Async DB connection
5. `app/config/database/UnitOfWork.py` - Transaction management
6. `app/infrastructure/dependencies/Container.py` - DI container
7. `app/main.py` - FastAPI app initialization

### Must Create (Database):
8. `app/infrastructure/adapter/output/database/model/` - All SQLAlchemy models (8 files)
9. `app/infrastructure/adapter/output/database/mapper/` - All mappers (8 files)
10. `app/infrastructure/adapter/output/database/repository/` - All repositories (6 files)

### Must Create (Application):
11. `app/application/service/` - All services (5 files)

### Must Create (HTTP):
12. `app/infrastructure/adapter/input/http/` - All routers (5 files)
13. `app/infrastructure/adapter/input/middleware/ExceptionHandler.py`

---

## Key Architectural Decisions

| Area | Decision | Rationale |
|------|----------|-----------|
| **Port Return Types** | Domain entities (User, Session) not DTOs | Hexagonal architecture - ports operate on domain |
| **Transaction Management** | UnitOfWork pattern injected per request | Explicit boundaries, testability |
| **Service Structure** | One service per input port interface | Single Responsibility Principle |
| **Mapping Strategy** | Mappers in infrastructure layer | Domain independence |
| **Session Management** | AsyncSession per request via DI | Request-scoped, automatic cleanup |
| **Error Handling** | Domain exceptions → HTTP in middleware | Clean separation |
| **DI Pattern** | Container + FastAPI Depends() | Type-safe, testable |

---

## Verification Steps

### After Foundation (Phase 1-2):
- [ ] `Settings.py` loads `.env` correctly
- [ ] Database connection establishes
- [ ] Redis connection establishes

### After Database Layer (Phase 3):
- [ ] Alembic creates all tables
- [ ] Mappers convert domain ↔ models
- [ ] Repository methods execute without errors

### After Application Services (Phase 4):
- [ ] `RegisterUserService.execute` creates user and OTP
- [ ] `AuthenticateUserService.auth_email` validates and creates session

### After HTTP Layer (Phase 5):
- [ ] `POST /auth/register` returns 201 with user_id
- [ ] `POST /auth/login/email` returns 200 with tokens
- [ ] Exception middleware transforms domain exceptions

### Final Integration:
- [ ] Full flow: register → verify email → login → get sessions → revoke
- [ ] Protected endpoints require valid JWT
- [ ] Rate limiting works
- [ ] Logging captures all transactions
- [ ] Health check endpoint responds

---

## Environment Variables Required

Create `.env` file:
```env
# Database
DATABASE__URL=postgresql+asyncpg://user:pass@localhost:5432/auth_db
DATABASE__POOL_SIZE=10

# Redis
REDIS__URL=redis://localhost:6379/0

# JWT
JWT__SECRET_KEY=your-secret-key-here
JWT__ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT__REFRESH_TOKEN_EXPIRE_DAYS=30

# Crypto
CRYPTO__PASSWORD_SALT=your-salt-here
CRYPTO__ENCRYPTION_KEY=your-fernet-key-here

# Server
SERVER__ENVIRONMENT=development
SERVER__DEBUG=true
SERVER__ALLOWED_ORIGINS=["http://localhost:3000"]
```

---

## Success Criteria

✅ All port interfaces use domain entities
✅ Application services implement all use cases
✅ Database repositories persist domain entities
✅ HTTP endpoints handle requests with proper DTOs
✅ Middleware handles exceptions and authentication
✅ DI container wires all dependencies
✅ FastAPI app starts and serves requests
✅ Database migrations create schema
✅ End-to-end authentication flow works
✅ Tests pass (unit, integration, E2E)
