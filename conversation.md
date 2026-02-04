# Diskusi Arsitektur: Central Authentication & Multi-Service Platform

## Konteks

**Visi:** Membangun platform SaaS multi-service yang dapat bersaing dengan Lynk.ID dan platform sejenis, dengan sistem central authentication, authorization, dan payment.

**Current State:**
- Monorepo dengan 3 service utama: KAuthApp, KSysAdmin, KSysPayment
- Single PostgreSQL database (k_user_management)
- Shared Redis untuk caching/session
- Nginx sebagai API gateway
- Port: Public Server (8001), Admin Server (8002), Nginx (80)

---

## Q1: Arsitektur Central Auth vs Per-Service Data

**Pertanyaan:**
> "Disini hanya sebagai authentication dan authorization ya? Sedangkan data user masing-masing di service nya masing-masing akan di store ke database masing-masing service?"

**Jawaban: YA, Sangat Masuk Akal! ✅**

Inilah pola yang benar untuk multi-tenant SaaS platform:

### Central System (KAuthApp + KSysPayment + KSysAdmin)

**Tanggung Jawab:**
1. **User Authentication** (login, register, JWT tokens)
2. **User Authorization** (roles, permissions, scopes)
3. **User Profile** (email, nama, phone, avatar)
4. **Payment & Subscription** (billing, payment methods, invoices)
5. **Session Management** (JWT, refresh tokens)
6. **Admin Monitoring** (KSysAdmin - system health)

**Database: `k_user_management`**
- `users` - Core user data (id, email, password_hash, created_at)
- `user_profiles` - Profile info (name, avatar, phone)
- `user_roles` - Role assignments
- `subscriptions` - User subscriptions
- `payments` - Payment records
- `sessions` - Active sessions

### Per-Service System (Service A, B, C, ...)

**Tanggung Jawab:**
1. **Domain-Specific Logic** (e.g., e-commerce, CRM, analytics)
2. **Service-Specific Data** (orders, products, analytics data)
3. **Business Rules** (specific to that service)

**Database: `service_a_db`, `service_b_db`, etc.**
- Each service has its own database
- Stores ONLY domain-specific data
- References user by `user_id` (UUID from central auth)

**Example:**
```
Central Auth DB (k_user_management):
- users: {id: uuid_123, email: "user@example.com", ...}

E-Commerce Service DB (service_ecommerce_db):
- orders: {id: order_1, user_id: uuid_123, products: [...], total: 1000000}
- carts: {id: cart_1, user_id: uuid_123, items: [...]}

CRM Service DB (service_crm_db):
- customers: {id: cust_1, user_id: uuid_123, company: "...", notes: "..."}
- deals: {id: deal_1, customer_id: cust_1, amount: 5000000}
```

### Communication Pattern

**Scenario: User Login & Access Service**

1. **User Login (Central Auth)**
   ```
   POST /api/auth/login
   → Returns JWT token with claims: {user_id, email, roles, scopes}
   ```

2. **User Access Service A**
   ```
   GET /api/service-a/orders
   Headers: Authorization: Bearer <JWT_TOKEN>

   Service A:
   1. Validates JWT token (using shared public key or introspection)
   2. Extracts user_id from token
   3. Queries its own database: SELECT * FROM orders WHERE user_id = 'uuid_123'
   4. Returns data
   ```

3. **Service A Needs User Profile Info**
   ```
   Option 1 (Recommended): Include basic info in JWT token
   - Token payload: {user_id, email, name, avatar_url}
   - No extra API call needed

   Option 2: Service-to-Service API call
   - Service A calls: GET /api/auth/users/{user_id}
   - Central Auth returns user profile
   ```

### Benefits

✅ **Loose Coupling**: Services independent, can be deployed/scaled separately
✅ **Security**: Central auth ensures consistent authentication
✅ **Scalability**: Each service scales independently
✅ **Data Isolation**: Service failures don't affect others
✅ **Flexibility**: Some services can be serverless, databaseless
✅ **Multi-Tenancy**: Easy to implement per-organization isolation

### Drawbacks to Watch

⚠️ **Distributed Transactions**: Need saga pattern or eventual consistency
⚠️ **Data Duplication**: May need to cache user profile in services
⚠️ **Network Latency**: Service-to-service calls add latency
⚠️ **Token Management**: JWT token size if too many claims

---

## Q2: Serverless & Databaseless Services

**Pertanyaan:**
> "Masing-masing service bisa ada yang serverless ada juga databaseless"

**Jawaban: Sangat Memungkinkan! ✅**

### Serverless Services

**Example: Notification Service**

```python
# AWS Lambda / Google Cloud Functions
# File: service_notification/lambda_handler.py

import boto3
import jwt

def lambda_handler(event, context):
    # Validate JWT token from Authorization header
    token = event['headers']['Authorization'].replace('Bearer ', '')

    try:
        # Verify token (shared secret or public key)
        payload = jwt.decode(token, PUBLIC_KEY, algorithms=['HS256'])
        user_id = payload['user_id']

        # Send notification (no database needed)
        sns = boto3.client('sns')
        sns.publish(
            TopicArn='arn:aws:sns:...',
            Message=f"Notification for user {user_id}"
        )

        return {'statusCode': 200, 'body': 'Notification sent'}
    except:
        return {'statusCode': 401, 'body': 'Invalid token'}
```

**Characteristics:**
- No persistent database
- Stateless processing
- Triggered by events (HTTP request, queue message, schedule)
- Uses external services (S3, SNS, SES, etc.)

**Use Cases:**
- Email/SMS notifications
- PDF generation
- Image processing
- Report generation
- Webhooks

### Databaseless Services

**Example: Analytics Aggregation Service**

```python
# Uses external data warehouse (BigQuery, Redshift)
# No PostgreSQL database

from google.cloud import bigquery

def get_user_analytics(user_id: str, token: str):
    # Validate token
    verify_jwt(token)

    # Query BigQuery (no local database)
    client = bigquery.Client()
    query = f"""
        SELECT
            event_date,
            COUNT(*) as event_count
        FROM analytics.events
        WHERE user_id = '{user_id}'
        GROUP BY event_date
    """

    results = client.query(query)
    return [dict(row) for row in results]
```

**Characteristics:**
- Reads from data warehouse or external API
- No relational database
- May use caching (Redis) for performance

**Use Cases:**
- Analytics dashboards
- Reporting services
- Search services (using Elasticsearch)
- Recommendation engines

### Architecture Pattern

```
┌─────────────────────────────────────────────┐
│         Central Auth System                 │
│  KAuthApp + KSysPayment + KSysAdmin        │
│  Database: k_user_management                │
│  Ports: 8001 (public), 8002 (admin)        │
└─────────────────┬───────────────────────────┘
                  │ JWT Token
                  ↓
    ┌─────────────────────────────────┐
    │      Nginx API Gateway          │
    │      Port 80/443                │
    └─────────────────┬───────────────┘
                      │
        ┌─────────────┼─────────────┬──────────────┐
        ↓             ↓             ↓              ↓
┌───────────┐  ┌───────────┐  ┌──────────┐  ┌──────────────┐
│ Service A │  │ Service B │  │Service C │  │  Service D   │
│ (Regular) │  │(Serverless)│  │(Database)│  │(Databaseless)│
├───────────┤  ├───────────┤  ├──────────┤  ├──────────────┤
│ FastAPI   │  │AWS Lambda │  │ FastAPI  │  │  FastAPI     │
│ Port 8003 │  │ Function  │  │Port 8004 │  │  Port 8005   │
│ DB: Own   │  │ No DB     │  │DB: Own   │  │  No DB       │
│ PostgreSQL│  │ Uses SNS  │  │PostgreSQL│  │  Uses Redis  │
└───────────┘  └───────────┘  └──────────┘  └──────────────┘
```

---

## Q3: Database Scaling - Master-Slave Replication

**Pertanyaan:**
> "Apakah sangat masuk akal jika saya ingin master-slave kedepannya?"

**Jawaban: YA, Master-Slave adalah Strategi Yang Tepat! ✅**

### Current State (Single Instance)

```
┌─────────────────────────┐
│   PostgreSQL (Port 5433)│
│   Database: k_user_mgmt │
│   Read + Write          │
└─────────────────────────┘
         ↑
         │
    All Queries
```

**Limitations:**
- Single point of failure
- Read queries compete with write queries
- Limited throughput
- No geographic distribution

### Master-Slave Architecture (Recommended for Scale-Up)

```
                    ┌─────────────────────────┐
                    │   PostgreSQL Master     │
                    │   Write Operations      │
                    │   Port 5432             │
                    └──────────┬──────────────┘
                               │
                     Replication (Streaming)
                               │
        ┌──────────────────────┼──────────────────────┐
        ↓                      ↓                      ↓
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│Slave 1 (Read)│     │Slave 2 (Read)│     │Slave 3 (Read)│
│Port 5433      │     │Port 5434      │     │Port 5435      │
│Asia Region    │     │Europe Region  │     │US Region      │
└───────────────┘     └───────────────┘     └───────────────┘
```

**Benefits:**

1. **High Availability**: If master fails, promote slave
2. **Read Scalability**: Distribute read queries across slaves
3. **Performance**: Reduce load on master
4. **Geographic Distribution**: Place replicas near users
5. **Backup**: Slaves serve as hot backups

### Implementation Strategy

#### Phase 1: Setup Replication

**PostgreSQL Configuration:**

Master (`postgresql.conf`):
```ini
# Enable replication
wal_level = replica
max_wal_senders = 3
wal_keep_size = 64MB

# Replication slots (optional but recommended)
max_replication_slots = 3
```

Master (`pg_hba.conf`):
```
# Allow replication connections
host replication replicator 10.0.0.0/8 md5
```

Slave (`recovery.conf` or `postgresql.conf` in PG12+):
```ini
primary_conninfo = 'host=master_ip port=5432 user=replicator password=xxx'
primary_slot_name = 'slave_1_slot'
```

#### Phase 2: Application Changes

**Database Connection Strategy:**

```python
# shared/backend/database/engine.py

from sqlalchemy.ext.asyncio import create_async_engine
from shared.backend.config.settings import settings

# Master connection (writes)
master_engine = create_async_engine(
    settings.database_url_master,  # postgresql+asyncpg://...master:5432/...
    pool_size=20,
    max_overflow=10
)

# Slave connections (reads)
slave_engines = [
    create_async_engine(
        settings.database_url_slave_1,  # ...slave1:5433/...
        pool_size=30,  # More read capacity
        max_overflow=20
    ),
    create_async_engine(
        settings.database_url_slave_2,  # ...slave2:5434/...
        pool_size=30,
        max_overflow=20
    )
]

# Load balancing for reads
import random

async def getDbRead() -> AsyncSession:
    """Get read-only database session (slave)"""
    engine = random.choice(slave_engines)  # Simple round-robin
    session_factory = async_sessionmaker(bind=engine, ...)
    async with session_factory() as session:
        yield session

async def getDbWrite() -> AsyncSession:
    """Get read-write database session (master)"""
    session_factory = async_sessionmaker(bind=master_engine, ...)
    async with session_factory() as session:
        yield session
```

**Repository Pattern Changes:**

```python
# Base repository with read/write separation

class BaseRepository(Generic[ModelType]):
    def __init__(self, model: type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session  # Could be read or write session

    async def getById(self, id: uuid.UUID) -> ModelType | None:
        """Read operation - use slave"""
        # This method called with read session from getDbRead()
        result = await self.session.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()

    async def create(self, entity: ModelType) -> ModelType:
        """Write operation - use master"""
        # This method called with write session from getDbWrite()
        self.session.add(entity)
        await self.session.flush()
        await self.session.refresh(entity)
        return entity
```

**Router Example:**

```python
from shared.backend.database.engine import getDbRead, getDbWrite

@router.get('/users/{user_id}')
async def getUser(
    user_id: UUID,
    session: AsyncSession = Depends(getDbRead)  # Read from slave
):
    repo = UserRepository(session)
    user = await repo.getById(user_id)
    return user

@router.post('/users')
async def createUser(
    data: UserInput,
    session: AsyncSession = Depends(getDbWrite)  # Write to master
):
    repo = UserRepository(session)
    user = await repo.create(User(**data.dict()))
    return user
```

#### Phase 3: Monitoring & Failover

**Replication Lag Monitoring:**

```python
async def checkReplicationLag() -> dict:
    """Check replication lag for all slaves"""
    master_session = await getDbWrite()

    # Get current LSN from master
    result = await master_session.execute(
        text("SELECT pg_current_wal_lsn()")
    )
    master_lsn = result.scalar()

    # Check each slave
    slave_statuses = []
    for i, slave_engine in enumerate(slave_engines):
        async with slave_engine.connect() as conn:
            result = await conn.execute(
                text("SELECT pg_last_wal_replay_lsn()")
            )
            slave_lsn = result.scalar()

            # Calculate lag (simplified)
            lag = master_lsn - slave_lsn

            slave_statuses.append({
                'slave': f'slave_{i+1}',
                'lag_bytes': lag,
                'healthy': lag < 1024 * 1024  # < 1MB lag
            })

    return slave_statuses
```

**Automatic Failover (Advanced):**

Consider using:
- **Patroni** - HA solution for PostgreSQL
- **PgBouncer** - Connection pooling and routing
- **HAProxy** - Load balancing for database connections

### Replication Lag Considerations

**Important:**
- Replication is asynchronous (typically 10-100ms lag)
- Critical: Read-after-write consistency

**Solution: Session-Level Routing**

```python
@router.post('/users')
async def createUser(data: UserInput, session: AsyncSession = Depends(getDbWrite)):
    # Write to master
    user = await userService.create(data)

    # Redirect to detail page
    return RedirectResponse(
        url=f'/users/{user.id}',
        headers={'X-Read-From-Master': 'true'}  # Flag for next request
    )

@router.get('/users/{user_id}')
async def getUser(
    user_id: UUID,
    x_read_from_master: str = Header(None),
    session: AsyncSession = Depends(...)  # Dynamic dependency
):
    # If flag set, read from master to ensure consistency
    if x_read_from_master:
        session = await getDbWrite()
    else:
        session = await getDbRead()

    user = await userService.getById(user_id, session)
    return user
```

### Cost Considerations

**Single Database:**
- Cost: $50-200/month (depending on specs)
- Good for: < 1000 concurrent users, < 100 req/s

**Master + 2 Slaves:**
- Cost: $150-600/month
- Good for: 1000-10,000 concurrent users, 100-1000 req/s

**Recommendation:**
1. Start with single instance
2. Monitor query performance (slow query log)
3. Add read replica when:
   - Read queries > 70% of total
   - CPU usage consistently > 70%
   - Query latency > 100ms
4. Implement master-slave when user base > 5000

---

## Q4: API Documentation Access

**Pertanyaan:**
> "Bagaimana saya membuka dokumentasi dari admin auth ini? Saya mencoba akses localhost:8080/api/admin/docs ini salah"

**Jawaban:**

### Correct URLs

**Admin Server Docs:**
```
http://localhost:8002/docs
```

Bukan `localhost:8080/api/admin/docs` karena:
- Admin server running di port **8002** (bukan 8080)
- Docs ada di root `/docs` (bukan `/api/admin/docs`)

**Public Server Docs (Auth + Payment):**
```
http://localhost:8001/docs
```

**Via Nginx Gateway:**
```
http://localhost/api/admin/docs   ❌ WRONG - Not configured
http://localhost:8002/docs         ✅ CORRECT - Direct to admin server
```

### Why This Happens?

**Current Nginx Configuration:**
```nginx
location /api/admin/ {
    proxy_pass http://localhost:8002/api/admin/;
}
```

This only proxies `/api/admin/*` routes, NOT `/docs`.

### Solution 1: Access Directly (Current)

Bypass nginx, access servers directly:
- Admin: `http://localhost:8002/docs`
- Public: `http://localhost:8001/docs`

### Solution 2: Add Docs Routes to Nginx (Recommended)

Update `nginx/nginx.conf`:

```nginx
# Admin API routes
location /api/admin/ {
    proxy_pass http://localhost:8002/api/admin/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}

# Admin Docs (NEW)
location /admin/docs {
    proxy_pass http://localhost:8002/docs;
    proxy_set_header Host $host;
}

# Public API routes
location /api/auth/ {
    proxy_pass http://localhost:8001/api/auth/;
}

location /api/payment/ {
    proxy_pass http://localhost:8001/api/payment/;
}

# Public Docs (NEW)
location /docs {
    proxy_pass http://localhost:8001/docs;
    proxy_set_header Host $host;
}
```

**After reload:**
```bash
nginx -s reload
```

**New URLs:**
- Admin docs: `http://localhost/admin/docs`
- Public docs: `http://localhost/docs`

### OpenAPI Endpoints Summary

After configuration:

| Service | Direct URL | Via Nginx (after config) |
|---------|-----------|---------------------------|
| Admin Docs | http://localhost:8002/docs | http://localhost/admin/docs |
| Admin API | http://localhost:8002/api/admin/* | http://localhost/api/admin/* |
| Public Docs | http://localhost:8001/docs | http://localhost/docs |
| Auth API | http://localhost:8001/api/auth/* | http://localhost/api/auth/* |
| Payment API | http://localhost:8001/api/payment/* | http://localhost/api/payment/* |

---

## Architecture Recommendations

### 1. JWT Token Structure (Central Auth)

**Token Payload:**
```json
{
  "user_id": "019c29f5-a658-7470-8c2b-bf1daf8c6e88",
  "email": "user@example.com",
  "name": "John Doe",
  "roles": ["user", "premium"],
  "scopes": ["service_a:read", "service_b:write"],
  "subscription_tier": "pro",
  "exp": 1707062400,
  "iat": 1707058800
}
```

**Benefits:**
- Services can validate token without calling auth API
- Contains essential user info (no extra queries)
- Scopes control per-service access

### 2. Service Registration Pattern

**Central Registry (Redis):**
```python
# When service starts, register itself
await redis.hset('services:registry', 'service_a', json.dumps({
    'name': 'E-Commerce Service',
    'url': 'https://ecommerce.yourdomain.com',
    'health_endpoint': '/health',
    'version': '1.0.0',
    'status': 'active'
}))
```

**Admin Dashboard Shows All Services:**
- List all registered services
- Health status
- Version info
- Last heartbeat

### 3. API Gateway Pattern

**Recommended: Kong or Traefik (Alternative to Nginx)**

Benefits:
- Automatic service discovery
- Built-in authentication plugins
- Rate limiting per service
- Metrics aggregation
- Admin UI

**Example with Kong:**
```bash
# Register service
curl -X POST http://localhost:8001/services/ \
  --data 'name=service-a' \
  --data 'url=http://service-a:8003'

# Add JWT authentication
curl -X POST http://localhost:8001/services/service-a/plugins \
  --data 'name=jwt'
```

### 4. Multi-Tenancy Strategy

**Option A: Separate Database per Organization**
- Database: `org_123_db`, `org_456_db`
- Pros: Complete isolation, easy backup/restore per org
- Cons: More databases to manage

**Option B: Single Database with tenant_id**
- All tables have `tenant_id` column
- Row-level security policies
- Pros: Easier to manage
- Cons: Need careful query filtering

**Recommendation:** Start with Option B, migrate to A for large enterprises

### 5. Service Communication Patterns

**Synchronous (REST API):**
```python
# Service A calls Service B
response = await httpx.get(
    'https://service-b.internal/api/data',
    headers={'Authorization': f'Bearer {service_token}'}
)
```

**Asynchronous (Message Queue):**
```python
# Service A publishes event
await rabbitmq.publish(
    exchange='events',
    routing_key='user.registered',
    message={'user_id': '...', 'email': '...'}
)

# Service B subscribes to event
@consumer('user.registered')
async def on_user_registered(message):
    # Create customer record in CRM
    pass
```

**Recommendation:** Use async for:
- Event notifications
- Background processing
- Non-critical operations

Use sync for:
- Real-time data queries
- User-facing operations

---

## Next Steps

### Immediate (Before Scaling)

1. **Add Docs to Nginx** ✅
   - Update nginx.conf with docs routes
   - Test access via nginx gateway

2. **Document JWT Claims** ✅
   - Define standard token payload
   - Create validation logic for services

3. **Create Service Template** 📋
   - Boilerplate for new services
   - Include JWT validation
   - Include health check endpoint

### Short-Term (1-3 Months)

1. **Implement Service Discovery** 🔍
   - Service registry in Redis
   - Health check monitoring
   - Admin dashboard showing all services

2. **Add Read Replicas** 🗄️
   - When traffic > 100 req/s
   - Monitor replication lag
   - Implement read/write routing

3. **Build 2-3 Sample Services** 🚀
   - Validate architecture
   - Test JWT authentication
   - Measure performance

### Long-Term (3-6 Months)

1. **API Gateway Migration** 🌐
   - Migrate from Nginx to Kong/Traefik
   - Service mesh (optional: Istio)
   - Advanced routing/load balancing

2. **Multi-Region Deployment** 🌍
   - Deploy replicas in Asia, Europe, US
   - Use CDN for static assets
   - Database read replicas per region

3. **Observability Stack** 📊
   - Distributed tracing (Jaeger)
   - Centralized logging (ELK stack)
   - Metrics (Prometheus + Grafana)

---

## Closing Notes

**Your Vision:**
> "Saya ingin menjadi pesaing Lynk.ID"

**Key Success Factors:**

1. ✅ **Solid Foundation**: Current architecture supports multi-service platform
2. ✅ **Scalability**: Master-slave ready, service isolation enables independent scaling
3. ✅ **Security**: JWT-based auth with central control
4. ✅ **Flexibility**: Services can be serverless/databaseless as needed
5. ✅ **Developer Experience**: Clear patterns, good documentation

**You're on the Right Track!** 🎯

Architecture yang kamu bangun sekarang sudah sangat solid dan scalable. Dengan pattern central auth + distributed services, kamu bisa:
- Deploy unlimited services independently
- Scale per-service based on demand
- Maintain security centrally
- Compete with major SaaS platforms

**Saran Prioritas:**
1. Selesaikan KAuthApp (login, register, JWT)
2. Build 1-2 sample services untuk validate pattern
3. Implement monitoring & logging
4. Baru scale up (master-slave, multi-region)

Good luck! 🚀
