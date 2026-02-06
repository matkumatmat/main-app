# KAuth Frontend API Documentation

This document provides comprehensive documentation for the KAuth authentication frontend API integration. It details all endpoints, request/response formats, headers, and error handling for backend implementation.

## Table of Contents

- [Base Configuration](#base-configuration)
- [Request Headers](#request-headers)
- [Authentication Endpoints](#authentication-endpoints)
- [Response Formats](#response-formats)
- [Error Handling](#error-handling)
- [Security Considerations](#security-considerations)

---

## Base Configuration

### API Base URL
- **Development**: `http://localhost/api/auth`
- **Production**: Set via environment variable `PUBLIC_API_BASE_URL`

### Request Timeout
- **Default**: 10 seconds (10000ms)

### Credentials
- **withCredentials**: `true` (cookies enabled for session management)

---

## Request Headers

All requests from the frontend include the following headers:

### Standard Headers

```http
Content-Type: application/json
Accept: application/json
X-Client-Version: 1.0.0
X-Client-Platform: web
X-Request-Id: <uuid-v4>
X-Request-Timestamp: <ISO-8601-timestamp>
```

### Authentication Header (when authenticated)

```http
Authorization: Bearer <access-token>
```

### Header Descriptions

| Header | Type | Required | Description |
|--------|------|----------|-------------|
| `Content-Type` | String | Yes | Always `application/json` |
| `Accept` | String | Yes | Always `application/json` |
| `X-Client-Version` | String | Yes | Frontend version for compatibility checks |
| `X-Client-Platform` | String | Yes | Platform identifier (`web`) |
| `X-Request-Id` | UUID v4 | Yes | Unique request identifier for tracing |
| `X-Request-Timestamp` | ISO 8601 | Yes | Request creation timestamp |
| `Authorization` | String | Conditional | Bearer token for authenticated requests |

---

## Authentication Endpoints

### 1. Sign Up

Creates a new user account and sends OTP verification email.

**Endpoint**: `POST /signup`

**Request Body**:
```json
{
  "fullName": "John Doe",
  "email": "john@example.com",
  "password": "SecurePass123"
}
```

**Validation Rules**:
- `fullName`:
  - Required
  - Min length: 2 characters
  - Max length: 100 characters
- `email`:
  - Required
  - Valid email format
- `password`:
  - Required
  - Min length: 8 characters
  - Max length: 128 characters
  - Must contain: uppercase letter, lowercase letter, and number

**Success Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "01933b8f-8c5e-7890-b123-456789abcdef",
      "email": "john@example.com",
      "fullName": "John Doe",
      "isVerified": false,
      "createdAt": "2024-01-15T10:30:00.000Z"
    },
    "message": "Account created successfully. Please verify your email."
  }
}
```

**Error Response** (400 Bad Request):
```json
{
  "success": false,
  "message": "Validation failed",
  "errors": {
    "email": ["Email already exists"],
    "password": ["Password must contain uppercase letter"]
  }
}
```

---

### 2. Sign In

Authenticates user and returns access tokens.

**Endpoint**: `POST /signin`

**Request Body**:
```json
{
  "email": "john@example.com",
  "password": "SecurePass123"
}
```

**Validation Rules**:
- `email`:
  - Required
  - Valid email format
- `password`:
  - Required
  - Min length: 8 characters

**Success Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "01933b8f-8c5e-7890-b123-456789abcdef",
      "email": "john@example.com",
      "fullName": "John Doe",
      "isVerified": true,
      "createdAt": "2024-01-15T10:30:00.000Z"
    },
    "tokens": {
      "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "tokenType": "Bearer",
      "expiresIn": 3600
    }
  }
}
```

**Error Response** (401 Unauthorized):
```json
{
  "success": false,
  "message": "Invalid email or password"
}
```

**Error Response** (403 Forbidden - Unverified):
```json
{
  "success": false,
  "message": "Please verify your email before signing in"
}
```

---

### 3. Verify OTP

Verifies email with 6-digit OTP code.

**Endpoint**: `POST /verify-otp`

**Request Body**:
```json
{
  "email": "john@example.com",
  "otp": "123456"
}
```

**Validation Rules**:
- `email`:
  - Required
  - Valid email format
- `otp`:
  - Required
  - Exactly 6 digits
  - Numeric only

**Success Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "01933b8f-8c5e-7890-b123-456789abcdef",
      "email": "john@example.com",
      "fullName": "John Doe",
      "isVerified": true,
      "createdAt": "2024-01-15T10:30:00.000Z"
    },
    "tokens": {
      "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "tokenType": "Bearer",
      "expiresIn": 3600
    },
    "message": "Email verified successfully"
  }
}
```

**Error Response** (400 Bad Request):
```json
{
  "success": false,
  "message": "Invalid or expired OTP"
}
```

**Error Response** (404 Not Found):
```json
{
  "success": false,
  "message": "User not found"
}
```

---

### 4. Resend OTP

Sends a new OTP code to user's email.

**Endpoint**: `POST /resend-otp`

**Request Body**:
```json
{
  "email": "john@example.com"
}
```

**Validation Rules**:
- `email`:
  - Required
  - Valid email format

**Success Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "message": "OTP sent successfully"
  }
}
```

**Error Response** (429 Too Many Requests):
```json
{
  "success": false,
  "message": "Please wait 60 seconds before requesting another OTP"
}
```

---

### 5. Refresh Token

Refreshes access token using refresh token.

**Endpoint**: `POST /refresh`

**Request Body**:
```json
{
  "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Success Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "tokenType": "Bearer",
    "expiresIn": 3600
  }
}
```

**Error Response** (401 Unauthorized):
```json
{
  "success": false,
  "message": "Invalid refresh token"
}
```

---

### 6. Sign Out

Signs out user and invalidates tokens.

**Endpoint**: `POST /signout`

**Headers Required**:
```http
Authorization: Bearer <access-token>
```

**Success Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "message": "Signed out successfully"
  }
}
```

---

## Response Formats

### Success Response Structure

```typescript
interface ApiResponse<T> {
  success: true;
  data: T;
  message?: string;
}
```

### Error Response Structure

```typescript
interface ApiErrorResponse {
  success: false;
  message: string;
  errors?: Record<string, string[]>;
}
```

### Common Data Types

#### User Object
```typescript
interface User {
  id: string;              // UUID7 format
  email: string;
  fullName: string;
  isVerified: boolean;
  createdAt: string;       // ISO 8601 format
}
```

#### Auth Tokens Object
```typescript
interface AuthTokens {
  accessToken: string;     // JWT token
  refreshToken: string;    // JWT token
  tokenType: string;       // Always "Bearer"
  expiresIn: number;       // Seconds until expiration
}
```

---

## Error Handling

### HTTP Status Codes

| Status Code | Meaning | Usage |
|-------------|---------|-------|
| `200` | Success | Request completed successfully |
| `400` | Bad Request | Validation errors or malformed request |
| `401` | Unauthorized | Invalid or expired credentials |
| `403` | Forbidden | Action not allowed (e.g., unverified user) |
| `404` | Not Found | Resource doesn't exist |
| `429` | Too Many Requests | Rate limit exceeded |
| `500` | Internal Server Error | Server-side error |

### Frontend Error Handling

The frontend implements automatic error handling:

1. **Validation Errors** (400): Display field-specific errors
2. **Authentication Errors** (401): Attempt token refresh, then redirect to sign-in
3. **Network Errors**: Display user-friendly message
4. **Rate Limiting** (429): Display cooldown timer

### Error Message Examples

```typescript
// Field validation errors
{
  "success": false,
  "message": "Validation failed",
  "errors": {
    "email": ["Invalid email format"],
    "password": ["Password must be at least 8 characters"]
  }
}

// Authentication error
{
  "success": false,
  "message": "Invalid email or password"
}

// Rate limiting error
{
  "success": false,
  "message": "Too many requests. Please try again in 60 seconds"
}
```

---

## Security Considerations

### Backend Implementation Requirements

1. **Password Hashing**
   - Use Argon2id (as configured in shared Rust crypto module)
   - Never store plain-text passwords
   - Min cost factor: 19

2. **OTP Generation**
   - Generate cryptographically secure 6-digit codes
   - Set expiration: 10 minutes
   - Limit attempts: 5 per OTP
   - Implement cooldown: 60 seconds between resends

3. **Token Security**
   - Access token expiry: 1 hour
   - Refresh token expiry: 7 days
   - Store refresh tokens hashed in database
   - Invalidate tokens on sign out

4. **Rate Limiting**
   - Sign up: 5 requests per hour per IP
   - Sign in: 10 requests per hour per IP
   - OTP verification: 5 attempts per OTP
   - OTP resend: 1 request per minute per email

5. **Request Validation**
   - Validate all request headers
   - Sanitize input data
   - Enforce CORS policies
   - Check `X-Request-Id` for duplicate prevention

6. **Session Management**
   - Store session metadata in Redis
   - Write rate limit counters to Redis
   - Use nginx to check Redis before forwarding requests
   - Implement device fingerprinting for context-binding

7. **Email Security**
   - Send OTP to verified email addresses only
   - Include expiration time in email
   - Log all OTP generation/verification attempts

### Redis Keys for Rate Limiting

Backend should write these Redis keys for nginx rate limiting:

```
rate_limit:signin:{ip}:{timestamp}       # TTL: 3600s
rate_limit:signup:{ip}:{timestamp}       # TTL: 3600s
rate_limit:otp_verify:{email}:{otp_id}   # TTL: 600s
rate_limit:otp_resend:{email}            # TTL: 60s
```

### Audit Logging

Backend should log:
- All authentication attempts (success/failure)
- OTP generation and verification
- Token refresh attempts
- Sign out events

Use `UserLog` from `shared/backend/loggingFactory.py`.

---

## Frontend File Structure

```
src/
├── components/
│   ├── Auth/
│   │   ├── SignInForm.tsx       # Sign-in form with validation
│   │   ├── SignUpForm.tsx       # Sign-up form with validation
│   │   └── OtpForm.tsx          # OTP verification with animations
│   └── UI/
│       ├── Button.tsx           # Reusable button component
│       ├── Input.tsx            # Reusable input with error handling
│       └── Card.tsx             # Reusable card container
├── controllers/
│   └── authController.ts        # Authentication API calls
├── lib/
│   ├── api/
│   │   └── apiClient.ts         # Axios configuration & interceptors
│   └── schemas/
│       └── authSchemas.ts       # Zod validation schemas
├── pages/
│   ├── sign-in.astro            # Sign-in page
│   ├── sign-up.astro            # Sign-up page
│   └── verify-otp.astro         # OTP verification page
└── styles/
    └── global.css               # Tailwind + theme configuration
```

---

## Testing Checklist

### Backend Implementation Testing

- [ ] Sign up creates user with hashed password
- [ ] Sign up sends OTP email
- [ ] Sign up validates input (email format, password strength)
- [ ] Sign up prevents duplicate emails
- [ ] Sign in validates credentials
- [ ] Sign in returns JWT tokens
- [ ] Sign in prevents unverified users (optional based on requirements)
- [ ] OTP verification validates code
- [ ] OTP verification expires after 10 minutes
- [ ] OTP verification limits attempts
- [ ] OTP resend implements cooldown
- [ ] Token refresh validates refresh token
- [ ] Token refresh returns new access token
- [ ] Sign out invalidates tokens
- [ ] Rate limiting enforced at nginx layer
- [ ] All requests include required headers
- [ ] CORS configured correctly
- [ ] Redis session metadata written
- [ ] Audit logs generated for all auth events

---

## Environment Variables

### Frontend (.env)

```env
PUBLIC_API_BASE_URL=http://localhost/api/auth
```

### Backend (.env)

Reference backend environment configuration from root project.

Required for authentication:
- Database credentials
- Redis credentials
- JWT secret keys
- SMTP configuration for OTP emails
- Crypto master key (for Argon2id)

---

## Notes for Backend Developers

1. **User Model Fields**:
   - Use UUID7 for `id` (better indexing than UUID4)
   - Store `isVerified` boolean for email verification status
   - Use timestamps from SQLModel

2. **Token Storage**:
   - Access tokens: Store in localStorage (frontend handles this)
   - Refresh tokens: Store hashed in database
   - Session metadata: Store in Redis with user_id as key

3. **Email Template**:
   Create professional email template for OTP with:
   - 6-digit code prominently displayed
   - Expiration time (10 minutes)
   - Warning not to share code
   - Brand styling matching frontend

4. **Error Messages**:
   Keep error messages user-friendly but secure:
   - Don't reveal if email exists on sign-in (timing attack prevention)
   - Use generic messages for auth failures
   - Provide specific validation feedback for sign-up

5. **Performance**:
   - Index email column in users table
   - Cache OTP codes in Redis (not database)
   - Use Redis for rate limiting
   - Optimize JWT verification

---

## Support

For questions or issues with the frontend implementation:
- Check this documentation first
- Review the code comments in controller and API client files
- Test with the provided validation schemas

For backend implementation support:
- Follow CLAUDE.md architectural guidelines
- Use shared modules from `shared/backend/`
- Implement repository pattern for database access
- Follow strict OOP principles
