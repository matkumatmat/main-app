# Enhanced Logging Factory Examples

## Overview

The enhanced logging factory provides structured, production-ready logging with:
- **System Logs**: Security, Application, Performance, Error subtypes
- **User Audit Logs**: Immutable compliance trail
- **Request Context**: Automatic propagation across logs
- **Performance Tracking**: Built-in timers and slow operation detection

---

## Log Output Format (JSON)

All logs output as structured JSON for easy parsing and analysis:

```json
{
  "timestamp": "2026-02-03T10:30:45.123Z",
  "category": "system",
  "type": "security",
  "service": "KAuthApp",
  "label": "failed_login",
  "level": "warning",
  "event": "Invalid credentials provided",
  "email": "attacker@example.com",
  "ip_address": "192.168.1.100",
  "attempts": 5,
  "request_id": "req-abc-123"
}
```

---

## 1. System Logger - Security Events

Track authentication failures, brute force, permission violations:

```python
from shared.backend.loggingFactory import LoggerFactory

system_logger = LoggerFactory.getSystemLogger("KAuthApp")

# Failed login attempt
system_logger.security(
    "failed_login",
    "Invalid credentials provided",
    email="attacker@example.com",
    ip_address="192.168.1.100",
    attempts=5
)

# Brute force detection
system_logger.security(
    "brute_force_detected",
    "Multiple failed login attempts from same IP",
    ip_address="192.168.1.100",
    attempts=10,
    time_window_minutes=5
)

# Invalid token usage
system_logger.security(
    "invalid_token",
    "Expired JWT token used",
    token_id="token-xyz",
    user_id="user-123"
)
```

**Output:**
```json
{
  "category": "system",
  "type": "security",
  "level": "warning",
  "label": "failed_login",
  "event": "Invalid credentials provided",
  "email": "attacker@example.com",
  "ip_address": "192.168.1.100",
  "attempts": 5
}
```

---

## 2. System Logger - Application Flow

Track business logic execution:

```python
# User registration flow
system_logger.application(
    "user_registration",
    "New user registration completed",
    level="info",
    user_id="user-123",
    email="newuser@example.com"
)

# Payment processing
system_logger.application(
    "payment_processing",
    "Payment initiated",
    level="info",
    payment_id="pay-456",
    amount=150.00,
    currency="USD"
)

# Feature flag change
system_logger.application(
    "feature_flag_changed",
    "Feature flag updated",
    level="info",
    flag_name="new_ui_enabled",
    old_value=False,
    new_value=True
)
```

---

## 3. System Logger - Performance Tracking

Detect slow operations (default threshold: 500ms):

```python
# Manual performance logging
system_logger.performance(
    "database_query",
    duration_ms=750,  # Exceeds threshold
    threshold_ms=500,
    query="SELECT * FROM users WHERE ...",
    rows_returned=1500
)

# Context manager (automatic timing)
with system_logger.measurePerformance("external_api_call", threshold_ms=200):
    response = await httpx.get("https://api.example.com/data")
    # Logs only if execution time > 200ms

# With additional context
with system_logger.measurePerformance(
    "database_transaction",
    threshold_ms=1000,
    user_id="user-123",
    operation="bulk_update"
):
    await session.execute(bulk_update_query)
```

**Output (slow operation):**
```json
{
  "category": "system",
  "type": "performance",
  "level": "warning",
  "label": "database_query",
  "event": "Slow operation detected: database_query",
  "duration_ms": 750,
  "threshold_ms": 500,
  "query": "SELECT * FROM users WHERE ...",
  "rows_returned": 1500
}
```

---

## 4. System Logger - Error Handling

Log exceptions with full stack trace and context:

```python
try:
    result = await process_payment(user_id, amount)
except Exception as e:
    system_logger.error(
        "payment_processing_failed",
        e,
        message="Failed to process payment",
        user_id="user-456",
        amount=150.00,
        payment_gateway="stripe"
    )
    raise  # Re-raise after logging
```

**Output:**
```json
{
  "category": "system",
  "type": "error",
  "level": "error",
  "label": "payment_processing_failed",
  "event": "Failed to process payment",
  "error_detail": {
    "exception_type": "PaymentGatewayError",
    "exception_message": "Connection timeout to payment gateway",
    "stack_trace": "Traceback (most recent call last):\n  File \"...\", line 123\n    ..."
  },
  "user_id": "user-456",
  "amount": 150.0,
  "payment_gateway": "stripe"
}
```

---

## 5. User Audit Logger

Track user actions for compliance (IMMUTABLE logs):

```python
from shared.backend.loggingFactory import LoggerFactory

user_logger = LoggerFactory.getUserLogger("KAuthApp")

# User login
user_logger.audit(
    "login",
    user_id="user-789",
    resource="session:abc-123",
    ip_address="192.168.1.50",
    user_agent="Mozilla/5.0 ..."
)

# Data modification
user_logger.audit(
    "update",
    user_id="user-789",
    resource="profile:user-789",
    changes={"email": "newemail@example.com"},
    ip_address="192.168.1.50"
)

# Permission change
user_logger.audit(
    "permission_granted",
    user_id="admin-001",
    resource="user:user-789",
    permission="admin_access",
    granted_by="admin-001"
)
```

**Output:**
```json
{
  "category": "user",
  "type": "audit",
  "level": "info",
  "action": "login",
  "event": "User login",
  "user_id": "user-789",
  "resource": "session:abc-123",
  "ip_address": "192.168.1.50",
  "user_agent": "Mozilla/5.0 ..."
}
```

---

## 6. Request Context Binding

Automatically add request_id and user context to all logs:

### Option A: Manual Binding (Middleware)

```python
from shared.backend.loggingFactory import (
    bindRequestContext,
    clearRequestContext
)

# In FastAPI middleware
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    # Bind context at start of request
    bindRequestContext(
        request_id=request.state.request_id,
        user_id=getattr(request.state, "user_id", None),
        ip_address=request.client.host
    )

    try:
        response = await call_next(request)
        return response
    finally:
        # Clear context after request
        clearRequestContext()
```

### Option B: Context Manager

```python
from shared.backend.loggingFactory import logRequestContext

async def process_request(request: Request):
    with logRequestContext(
        request_id=request.state.request_id,
        user_id=current_user.id
    ):
        # All logs here automatically include request_id and user_id
        system_logger.application(
            "payment_processing",
            "Payment initiated",
            amount=150.00
        )

        user_logger.audit(
            "payment_create",
            user_id=current_user.id,
            resource="payment:pay-123"
        )
```

**Output (with context):**
```json
{
  "category": "system",
  "type": "application",
  "event": "Payment initiated",
  "amount": 150.0,
  "request_id": "req-xyz-789",
  "user_id": "user-999",
  "ip_address": "192.168.1.75"
}
```

---

## FastAPI Integration Example

```python
from fastapi import FastAPI, Request
from shared.backend.loggingFactory import (
    setupLogging,
    LoggerFactory,
    bindRequestContext,
    clearRequestContext
)

app = FastAPI()

# Setup logging on startup
@app.on_event("startup")
async def startup():
    setupLogging()

# Create logger instances
system_logger = LoggerFactory.getSystemLogger("KAuthApp")
user_logger = LoggerFactory.getUserLogger("KAuthApp")

# Middleware for request context
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    bindRequestContext(
        request_id=request.headers.get("X-Request-ID", "unknown"),
        ip_address=request.client.host
    )

    try:
        response = await call_next(request)
        return response
    finally:
        clearRequestContext()

# Endpoint example
@app.post("/api/auth/login")
async def login(credentials: LoginInput):
    try:
        user = await authenticate(credentials)

        # Audit log
        user_logger.audit(
            "login",
            user_id=user.id,
            resource=f"session:{user.session_id}",
            email=user.email
        )

        return {"token": user.token}

    except InvalidCredentialsError as e:
        # Security log
        system_logger.security(
            "failed_login",
            "Invalid credentials provided",
            email=credentials.email
        )
        raise HTTPException(401, "Invalid credentials")

    except Exception as e:
        # Error log
        system_logger.error(
            "login_error",
            e,
            email=credentials.email
        )
        raise
```

---

## Log Analysis Queries

### Find all failed login attempts:
```bash
cat logs/app.log | jq 'select(.type == "security" and .label == "failed_login")'
```

### Find slow database queries:
```bash
cat logs/app.log | jq 'select(.type == "performance" and .label == "database_query" and .duration_ms > 1000)'
```

### Track user actions:
```bash
cat logs/app.log | jq 'select(.category == "user" and .user_id == "user-123")'
```

### Trace request flow:
```bash
cat logs/app.log | jq 'select(.request_id == "req-abc-123")'
```

---

## Best Practices

1. **Always use context binding** in middleware for request tracing
2. **Log errors with full context** (user_id, operation, relevant data)
3. **Set appropriate performance thresholds** based on operation type
4. **Use audit logs for compliance** (logins, data mutations, permissions)
5. **Include relevant context** in all logs (don't log just the message)
6. **Use label field** for log aggregation and filtering
7. **Clear context** after request completes (prevent data leakage)

---

## Performance Thresholds

Recommended thresholds:
- Database queries: 500ms
- External API calls: 1000ms
- File operations: 200ms
- Cache operations: 50ms
- Business logic: 100ms
