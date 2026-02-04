# Phase 2: Domain Factories Implementation Plan

## Overview

Extract OTP generation and session creation logic from application services into domain factories, following strict OOP and hexagonal architecture principles.

**Status:** Ready for Implementation
**Estimated Complexity:** Medium (7 files to create/modify)
**Risk Level:** Medium (includes critical bug fix in RefreshTokenService)

---

## Problem Statement

### Current Violations

**OTP Generation Duplicated 4x:**
- `UserRegistrationService._create_otp()` (lines 252-286)
- `ResendOtpService.resend_email_otp()` (lines 71-91)
- `ResendOtpService.resend_phone_otp()` (lines 116-136)
- `LinkAuthProviderService.link_email()` (lines 83-109)

All use identical logic: generate 6-digit code via `secrets.choice(string.digits)`, hash with Salter, save to repository.

**Session Creation Duplicated 2x:**
- `AuthenticationService._create_session()` (lines 235-284) - ✅ Uses TokenPolicy correctly
- `RefreshTokenService.execute()` (lines 86-144) - ❌ HARDCODES `timedelta(hours=1)` and `timedelta(days=7)`

### Critical Bug Found

**RefreshTokenService Constructor Signature Mismatch:**
- `dependencies.py:166` tries to inject `token_policy=token_policy`
- `RefreshTokenService.__init__` (lines 25-33) does NOT accept `token_policy` parameter
- Result: Service hardcodes token expiry instead of using domain policy

**Company Rule Violation:** Business logic (OTP algorithm, token structure) lives in application layer instead of domain.

---

## Solution Design

### Architecture Pattern

Follow existing TokenPolicy/QuotaDefaults pattern:
1. **Value Objects**: Encapsulate business rules (OtpPolicy)
2. **Factories**: Create domain entities (OtpCodeFactory, SessionFactory)
3. **Singleton DI**: Wire factories in dependencies.py
4. **Service Orchestration**: Services use factories, handle persistence

### Key Design Decisions

**1. Create OtpPolicy Value Object**
- Encapsulates OTP business rules (code length, expiry)
- Consistent with TokenPolicy/QuotaDefaults pattern
- Improves testability and future extensibility

**2. Factories Return Tuples**
- `OtpCodeFactory.create() -> tuple[OtpCode, str]` (entity for DB, raw code for delivery)
- `SessionFactory.create() -> tuple[Session, AuthenticationResult]` (entity for DB, DTO for response)

**3. Factories Are Sync**
- No I/O operations (pure entity creation)
- Async boundary remains at repository layer

**4. Services Handle Persistence**
- Factories create entities
- Services call `repository.save(entity)`
- Maintains transaction control in application layer

---

## Implementation Steps

### Step 1: Create OtpPolicy Value Object

**File:** `app/domain/authentication/OtpPolicy.py`

```python
from dataclasses import dataclass
from datetime import timedelta


@dataclass
class OtpPolicy:
    expiry_seconds: int
    code_length: int

    @staticmethod
    def default() -> 'OtpPolicy':
        return OtpPolicy(expiry_seconds=300, code_length=6)

    @staticmethod
    def from_config(expiry_seconds: int, code_length: int) -> 'OtpPolicy':
        return OtpPolicy(expiry_seconds=expiry_seconds, code_length=code_length)

    def get_expiry_timedelta(self) -> timedelta:
        return timedelta(seconds=self.expiry_seconds)

    def get_code_length(self) -> int:
        return self.code_length
```

**Test File:** `app/tests/unit/test_otp_policy.py`

Test coverage:
- `test_default_creation` - verify default values
- `test_from_config_creation` - verify custom config
- `test_get_expiry_timedelta` - verify conversion to timedelta
- `test_get_code_length` - verify code length getter

---

### Step 2: Create OtpCodeFactory

**File:** `app/domain/authentication/OtpCodeFactory.py`

```python
import secrets
import string
from datetime import datetime
from uuid import UUID

from app.domain.authentication.OtpCode import OtpCode
from app.domain.authentication.OtpPolicy import OtpPolicy
from app.domain.ValueObjects import OtpDeliveryMethod, OtpPurpose
from app.shared.Cryptography import Salter
from app.shared.DateTime import DateTimeProtocol
from app.shared.UuidGenerator import UuidGeneratorProtocol


class OtpCodeFactory:
    def __init__(
        self,
        salter: Salter,
        uuid_generator: UuidGeneratorProtocol,
        datetime_converter: DateTimeProtocol,
        otp_policy: OtpPolicy,
    ):
        self.salter = salter
        self.uuid_generator = uuid_generator
        self.datetime_converter = datetime_converter
        self.otp_policy = otp_policy

    def create(
        self,
        user_id: UUID | None,
        delivery_target: str,
        delivery_method: OtpDeliveryMethod,
        purpose: OtpPurpose,
        current_time: datetime,
    ) -> tuple[OtpCode, str]:
        raw_code = ''.join(
            secrets.choice(string.digits)
            for _ in range(self.otp_policy.get_code_length())
        )

        code_hash = self.salter.hash_password(raw_code)

        expires_at = self.datetime_converter.add_timedelta(
            current_time,
            self.otp_policy.get_expiry_timedelta()
        )

        otp_entity = OtpCode(
            id=self.uuid_generator.generate(),
            user_id=user_id,
            code_hash=code_hash,
            delivery_method=delivery_method,
            delivery_target=delivery_target,
            purpose=purpose,
            expires_at=expires_at,
            used_at=None,
            created_at=current_time,
        )

        return otp_entity, raw_code
```

**Test File:** `app/tests/unit/test_otp_code_factory.py`

Test coverage:
- `test_create_generates_correct_length` - verify code length matches policy
- `test_create_code_contains_only_digits` - verify numeric code
- `test_create_hashes_code_correctly` - verify hash matches raw code
- `test_create_calculates_expiry_from_policy` - verify expiry time
- `test_create_returns_tuple` - verify return structure
- `test_create_with_null_user_id` - edge case handling

---

### Step 3: Create SessionFactory

**File:** `app/domain/authorization/SessionFactory.py`

```python
from datetime import datetime
from uuid import UUID

from app.application.dto.AuthenticationDTO import AuthenticationResult
from app.domain.authorization.Session import Session
from app.domain.authorization.TokenPolicy import TokenPolicy
from app.shared.Cryptography import Salter
from app.shared.DateTime import DateTimeProtocol
from app.shared.TokenGenerator import ITokenGenerator
from app.shared.UuidGenerator import UuidGeneratorProtocol


class SessionFactory:
    def __init__(
        self,
        token_generator: ITokenGenerator,
        salter: Salter,
        uuid_generator: UuidGeneratorProtocol,
        datetime_converter: DateTimeProtocol,
        token_policy: TokenPolicy,
    ):
        self.token_generator = token_generator
        self.salter = salter
        self.uuid_generator = uuid_generator
        self.datetime_converter = datetime_converter
        self.token_policy = token_policy

    def create(
        self,
        user_id: UUID,
        device_info: str,
        ip_address: str,
        current_time: datetime,
    ) -> tuple[Session, AuthenticationResult]:
        session_id = self.uuid_generator.generate()

        access_token_payload = {
            "user_id": str(user_id),
            "session_id": str(session_id),
            "type": "access"
        }
        access_token = self.token_generator.generate(
            access_token_payload,
            expires_delta=self.token_policy.get_access_token_expiry()
        )

        refresh_token_payload = {
            "user_id": str(user_id),
            "session_id": str(session_id),
            "type": "refresh"
        }
        refresh_token = self.token_generator.generate(
            refresh_token_payload,
            expires_delta=self.token_policy.get_refresh_token_expiry()
        )

        refresh_token_hash = self.salter.hash_password(refresh_token)

        expires_at = self.datetime_converter.add_timedelta(
            current_time,
            self.token_policy.get_refresh_token_expiry()
        )

        session = Session(
            id=session_id,
            user_id=user_id,
            refresh_token_hash=refresh_token_hash,
            device_info=device_info,
            ip_address=ip_address,
            expires_at=expires_at,
            revoked_at=None,
            created_at=current_time,
        )

        result = AuthenticationResult(
            user_id=user_id,
            session_id=session_id,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=self.token_policy.get_access_token_expiry_seconds(),
            token_type="Bearer",
        )

        return session, result
```

**Test File:** `app/tests/unit/test_session_factory.py`

Test coverage:
- `test_create_generates_session_id` - verify session ID generation
- `test_create_generates_tokens` - verify token generation
- `test_create_hashes_refresh_token` - verify hashing
- `test_create_calculates_expiry_from_policy` - verify expiry from policy
- `test_access_token_payload_correct` - verify payload structure

---

### Step 4: Wire Dependencies

**File:** `app/infrastructure/dependencies.py`

**Add Imports** (after line 37):
```python
from app.domain.authentication.OtpPolicy import OtpPolicy
from app.domain.authentication.OtpCodeFactory import OtpCodeFactory
from app.domain.authorization.SessionFactory import SessionFactory
```

**Create Singletons** (after line 45):
```python
# After token_policy creation
otp_policy = OtpPolicy.from_config(
    expiry_seconds=config.auth.otp_expiry_seconds,
    code_length=config.auth.otp_code_length
)

# After line 59 (after uuid_generator, salter, etc.)
otp_factory = OtpCodeFactory(
    salter=salter,
    uuid_generator=uuid_generator,
    datetime_converter=datetime_converter,
    otp_policy=otp_policy
)

session_factory = SessionFactory(
    token_generator=token_generator,
    salter=salter,
    uuid_generator=uuid_generator,
    datetime_converter=datetime_converter,
    token_policy=token_policy
)
```

**Inject into Services:**

Update `get_authentication_service()` (~line 113):
```python
return AuthenticationService(
    # ... existing params ...
    token_policy=token_policy,
    session_factory=session_factory  # ADD THIS
)
```

Update `get_user_registration_service()` (~line 138):
```python
return UserRegistrationService(
    # ... existing params ...
    logger=root_logger,
    otp_factory=otp_factory  # ADD THIS
)
```

Update `get_refresh_token_service()` (~line 159):
```python
return RefreshTokenService(
    # ... existing params ...
    token_policy=token_policy,  # Already there but not accepted by __init__!
    session_factory=session_factory  # ADD THIS
)
```

Update `get_resend_otp_service()` (~line 189):
```python
return ResendOtpService(
    # ... existing params ...
    rate_limiter=rate_limiter,
    otp_factory=otp_factory  # ADD THIS
)
```

Update `get_link_auth_provider_service()` (find this function):
```python
return LinkAuthProviderService(
    # ... existing params ...
    otp_factory=otp_factory  # ADD THIS
)
```

---

### Step 5: Migrate UserRegistrationService

**File:** `app/application/service/UserRegistrationService.py`

**Add Import** (after line 41):
```python
from app.domain.authentication.OtpCodeFactory import OtpCodeFactory
```

**Update Constructor** (line 44):
```python
def __init__(
    self,
    # ... existing params ...
    logger: ILogger | None = None,
    otp_factory: OtpCodeFactory,  # ADD THIS
):
    # ... existing assignments ...
    self.otp_factory = otp_factory  # ADD THIS
```

**DELETE Method** `_create_otp()` (lines 252-286):
- Remove entire method

**Replace OTP Creation** in `_register_with_email()` (around line 156):
```python
# OLD:
await self._create_otp(
    user_id=saved_user.id,
    target=email,
    delivery_method=OtpDeliveryMethod.EMAIL,
    purpose=OtpPurpose.REGISTRATION,
    current_time=current_time,
)

# NEW:
otp_entity, raw_code = self.otp_factory.create(
    user_id=saved_user.id,
    delivery_target=email,
    delivery_method=OtpDeliveryMethod.EMAIL,
    purpose=OtpPurpose.REGISTRATION,
    current_time=current_time
)
await self.otp_repository.save(otp_entity)

if self.config.debug_otp:
    self.logger.debug("OTP code generated", code=raw_code, target=email)
```

**Replace OTP Creation** in `_register_with_phone()` (around line 215):
- Same pattern as above, use `OtpDeliveryMethod.WHATSAPP`

**Remove Imports** (lines 1-3):
```python
import secrets  # DELETE
import string  # DELETE
from datetime import timedelta  # DELETE (if not used elsewhere)
```

---

### Step 6: Migrate AuthenticationService

**File:** `app/application/service/AuthenticationService.py`

**Add Import** (after line 24):
```python
from app.domain.authorization.SessionFactory import SessionFactory
```

**Update Constructor** (line 29):
```python
def __init__(
    self,
    # ... existing params ...
    token_policy: TokenPolicy,
    session_factory: SessionFactory,  # ADD THIS
):
    # ... existing assignments ...
    self.session_factory = session_factory  # ADD THIS
```

**Simplify `_create_session()` Method** (lines 235-284):
```python
async def _create_session(self, user_id: UUID, device_info: str, ip_address: str) -> AuthenticationResult:
    current_time = self.datetime_converter.now_utc()

    session_entity, auth_result = self.session_factory.create(
        user_id=user_id,
        device_info=device_info,
        ip_address=ip_address,
        current_time=current_time
    )

    await self.session_repository.save(session_entity)

    return auth_result
```

---

### Step 7: CRITICAL BUG FIX - Migrate RefreshTokenService

**File:** `app/application/service/RefreshTokenService.py`

**Add Imports** (top of file):
```python
from app.domain.authorization.TokenPolicy import TokenPolicy
from app.domain.authorization.SessionFactory import SessionFactory
```

**FIX Constructor** - Add Missing Parameter (lines 25-39):
```python
def __init__(
    self,
    session_repository: ISessionRepository,
    transaction_logger: ITransactionLogger,
    salter: Salter,
    token_generator: ITokenGenerator,
    uuid_generator: UuidGeneratorProtocol,
    datetime_converter: DateTimeProtocol,
    token_policy: TokenPolicy,  # ADD THIS - was missing!
    session_factory: SessionFactory,  # ADD THIS
):
    self.session_repository = session_repository
    self.transaction_logger = transaction_logger
    self.salter = salter
    self.token_generator = token_generator
    self.uuid_generator = uuid_generator
    self.datetime_converter = datetime_converter
    self.token_policy = token_policy  # ADD THIS
    self.session_factory = session_factory  # ADD THIS
```

**Replace Session Creation** in `execute()` (lines 86-144):
```python
async def execute(self, refresh_token: str) -> AuthenticationResult:
    # ... keep validation logic (lines 42-84) ...

    await self.session_repository.revoke(matching_session.id)

    # REPLACE lines 86-144 with:
    new_session, auth_result = self.session_factory.create(
        user_id=user_id,
        device_info=matching_session.device_info,
        ip_address=matching_session.ip_address,
        current_time=current_time
    )

    await self.session_repository.save(new_session)

    await self.transaction_logger.log_user_behavior(
        UserBehaviorLog(
            id=self.uuid_generator.generate(),
            user_id=user_id,
            action=UserBehaviorAction.TOKEN_REFRESH,
            ip_address=matching_session.ip_address,
            user_agent=matching_session.device_info,
            additional_metadata={
                "old_session_id": str(matching_session.id),
                "new_session_id": str(new_session.id)
            },
            created_at=current_time
        )
    )

    return auth_result
```

**Remove Import** (line 1):
```python
from datetime import timedelta  # DELETE
```

---

### Step 8: Migrate ResendOtpService

**File:** `app/application/service/ResendOtpService.py`

**Add Import**:
```python
from app.domain.authentication.OtpCodeFactory import OtpCodeFactory
```

**Update Constructor** (line 28):
```python
def __init__(
    self,
    # ... existing params ...
    rate_limiter: OtpRateLimiter,
    otp_factory: OtpCodeFactory,  # ADD THIS
):
    # ... existing assignments ...
    self.otp_factory = otp_factory  # ADD THIS
```

**Replace OTP Creation** in `resend_email_otp()` (lines 64-91):
```python
# REPLACE lines 64-91 with:
current_time = self.datetime_converter.now_utc()

otp_entity, raw_code = self.otp_factory.create(
    user_id=user_id,
    delivery_target=email,
    delivery_method=OtpDeliveryMethod.EMAIL,
    purpose=OtpPurpose.REGISTRATION,
    current_time=current_time
)

await self.otp_repository.save(otp_entity)

if self.config.debug_otp:
    print(f"\n[DEBUG] Resend OTP for {email}: {raw_code}\n")
```

**Replace OTP Creation** in `resend_phone_otp()` (lines 109-136):
- Same pattern as above, use `OtpDeliveryMethod.WHATSAPP`

**Remove Imports**:
```python
import secrets  # DELETE
import string  # DELETE
from datetime import timedelta  # DELETE
```

---

### Step 9: Migrate LinkAuthProviderService

**File:** `app/application/service/LinkAuthProviderService.py`

**Add Import**:
```python
from app.domain.authentication.OtpCodeFactory import OtpCodeFactory
```

**Update Constructor**:
```python
def __init__(
    self,
    # ... existing params ...
    otp_factory: OtpCodeFactory,  # ADD THIS
):
    # ... existing assignments ...
    self.otp_factory = otp_factory  # ADD THIS
```

**Replace OTP Creation** in `link_email()` (lines 83-109):
```python
# REPLACE with:
otp_entity, raw_code = self.otp_factory.create(
    user_id=user_id,
    delivery_target=email,
    delivery_method=OtpDeliveryMethod.EMAIL,
    purpose=OtpPurpose.REGISTRATION,
    current_time=current_time
)

await self.otp_repository.save(otp_entity)

if self.config.debug_otp:
    print(f"\n[DEBUG] Link Email OTP for {email}: {raw_code}\n")
```

**Remove Imports**:
```python
import secrets  # DELETE
import string  # DELETE
from datetime import timedelta  # DELETE
```

---

## Validation & Testing

### Manual Testing Sequence

After implementation, test end-to-end:

**1. User Registration Flow:**
```bash
# Start server
poetry run python -m app.main

# Register user via API
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'

# Check logs for OTP (debug mode)
# Verify OTP code is 6 digits
# Verify OTP expires in 5 minutes
```

**2. Login and Token Refresh:**
```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'

# Extract refresh_token from response
# Wait 1 second
# Refresh token
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "<token>"}'

# Verify new access_token expires in 1 hour (from policy, not hardcoded)
# Verify new refresh_token expires in 7 days (from policy, not hardcoded)
```

**3. OTP Resend:**
```bash
# Resend OTP
curl -X POST http://localhost:8000/api/v1/auth/resend-otp \
  -H "Content-Type: application/json" \
  -d '{"user_id": "<user_id>"}'

# Verify new OTP invalidates old one
# Verify new OTP is 6 digits
```

### Unit Test Commands

```bash
# Test OtpPolicy
poetry run pytest app/tests/unit/test_otp_policy.py -v

# Test OtpCodeFactory
poetry run pytest app/tests/unit/test_otp_code_factory.py -v

# Test SessionFactory
poetry run pytest app/tests/unit/test_session_factory.py -v
```

### Integration Test Commands

```bash
# Run all integration tests
poetry run pytest app/tests/integration/ -v

# Specific service tests
poetry run pytest app/tests/integration/test_user_registration.py -v
poetry run pytest app/tests/integration/test_authentication.py -v
poetry run pytest app/tests/integration/test_token_refresh.py -v
```

### Full Test Suite

```bash
# Run everything
poetry run pytest -v

# With coverage
poetry run pytest --cov=app --cov-report=html
```

---

## Success Criteria

### Code Quality Checks

**OTP Generation:**
- [ ] Search codebase for `secrets.choice(string.digits)` - should only appear in OtpCodeFactory
- [ ] Search for `import secrets` in application services - should be ZERO
- [ ] Search for `import string` in application services - should be ZERO
- [ ] All OTP creation uses `otp_factory.create()`

**Session Creation:**
- [ ] Search for `timedelta(hours=1)` in services - should be ZERO
- [ ] Search for `timedelta(days=7)` in services - should be ZERO
- [ ] Search for hardcoded `expires_in=3600` - should be ZERO
- [ ] All session creation uses `session_factory.create()`

**Factory Pattern:**
- [ ] OtpCodeFactory exists in `app/domain/authentication/`
- [ ] SessionFactory exists in `app/domain/authorization/`
- [ ] OtpPolicy exists in `app/domain/authentication/`
- [ ] All factories injected via dependencies.py
- [ ] All factories are singleton instances

**Bug Fix Verification:**
- [ ] RefreshTokenService.__init__ accepts `token_policy` parameter
- [ ] RefreshTokenService.__init__ accepts `session_factory` parameter
- [ ] RefreshTokenService.execute() uses factory, not hardcoded timedeltas
- [ ] Token refresh returns tokens with correct expiry from policy

### Functional Checks

- [ ] User registration generates 6-digit OTP
- [ ] OTP expires after 5 minutes (from policy)
- [ ] Login creates session with 1-hour access token
- [ ] Login creates session with 7-day refresh token
- [ ] Token refresh creates new session with policy-based expiry
- [ ] Resend OTP generates new 6-digit code
- [ ] Link auth provider generates OTP

### Test Coverage

- [ ] OtpPolicy: 100% coverage
- [ ] OtpCodeFactory: 100% coverage
- [ ] SessionFactory: 100% coverage
- [ ] All integration tests pass
- [ ] No regression in existing functionality

---

## Files Modified Summary

| File | Type | Changes |
|------|------|---------|
| `app/domain/authentication/OtpPolicy.py` | CREATE | Value object for OTP business rules |
| `app/domain/authentication/OtpCodeFactory.py` | CREATE | Factory for OTP entity creation |
| `app/domain/authorization/SessionFactory.py` | CREATE | Factory for Session entity creation |
| `app/infrastructure/dependencies.py` | MODIFY | Wire factories into DI container |
| `app/application/service/UserRegistrationService.py` | MODIFY | Use OtpCodeFactory, delete _create_otp() |
| `app/application/service/AuthenticationService.py` | MODIFY | Use SessionFactory, simplify _create_session() |
| `app/application/service/RefreshTokenService.py` | **CRITICAL BUG FIX** | Add token_policy param, use SessionFactory |
| `app/application/service/ResendOtpService.py` | MODIFY | Use OtpCodeFactory |
| `app/application/service/LinkAuthProviderService.py` | MODIFY | Use OtpCodeFactory |
| `app/tests/unit/test_otp_policy.py` | CREATE | Unit tests for OtpPolicy |
| `app/tests/unit/test_otp_code_factory.py` | CREATE | Unit tests for OtpCodeFactory |
| `app/tests/unit/test_session_factory.py` | CREATE | Unit tests for SessionFactory |

**Total:** 3 new domain files, 3 new test files, 6 modified service files

---

## Post-Implementation

### Update Plan Status

After successful implementation, update `md/plan_001_refactor_domain.md`:

```markdown
| 2.1 | OTP generation logic | `UserRegistrationService.py:252-286` | `domain/authentication/OtpCodeFactory.py` | ✅ Done |
| 2.2 | Session creation logic | `AuthenticationService.py:232-281` | `domain/authorization/SessionFactory.py` | ✅ Done |
```

Update progress summary:
```markdown
| Phase 2: Factories | 2 | 2 | 0 | 0 |
| **TOTAL** | **10** | **6** | **0** | **4** |

**Overall Progress**: 60% Complete
```

### Next Phase Preview

After Phase 2 completion, proceed to:
- **Phase 3**: Add domain methods to Session entity (`belongs_to_user()`, `verify_refresh_token()`)
- **Phase 4**: Create PlanAssignmentService domain service

---

## Risk Mitigation

**Risk:** Constructor signature changes break running application
**Mitigation:** Update dependencies.py in same commit as service changes

**Risk:** RefreshTokenService bug fix changes token expiry behavior
**Mitigation:** Add specific test for token refresh expiry validation

**Risk:** OTP generation algorithm differs from original
**Mitigation:** Use exact same `secrets.choice(string.digits)` loop

**Risk:** Integration tests fail due to mock constructor mismatches
**Mitigation:** Update all test mocks to include new factory parameters

---

## Notes

- Follow strict OOP: No loose functions, all logic in classes
- File naming: CamelCase (e.g., `OtpCodeFactory.py`)
- Method naming: snake_case (e.g., `create_otp()`)
- No docstrings in implementation (company rule #13)
- No emojis in code or commits
- Business logic must live in domain layer only
