# Authentication & Authorization Module

## Overview

This module handles all authentication and authorization functionalities for the Ticket Management System, implementing a secure JWT-based authentication system with Role-Based Access Control (RBAC).

**Status**: ✅ **FULLY OPERATIONAL** - All endpoints tested and working (Last verified: 2025-11-16)

**Design Reference**: Based on User entity from `/design/uml-diagram.md`

## Quick Start

### Test Credentials

The system includes pre-configured test users for all roles:

| Username | Password | Role | Email |
|----------|----------|------|-------|
| `admin` | `Admin123!` | ADMIN | admin@example.com |
| `team.lead` | `TeamLead123!` | TEAM_LEAD | team.lead@example.com |
| `devops.engineer` | `DevOps123!` | DEVOPS_ENGINEER | devops.engineer@example.com |
| `enduser` | `EndUser123!` | END_USER | enduser@example.com |

### Quick Test

```bash
# Login as admin
curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"Admin123!"}'

# Response includes access_token and refresh_token
```

### Postman Collection

Import the complete Postman collection: `Ticket_Management_Complete_API.postman_collection.json`
- All endpoints pre-configured
- Auto-token refresh scripts
- Test data included

---

## Table of Contents

1. [Architecture](#architecture)
2. [User Roles](#user-roles)
3. [Authentication Flow](#authentication-flow)
4. [Authorization & Permissions](#authorization--permissions)
5. [JWT Token Management](#jwt-token-management)
6. [Security Features](#security-features)
7. [API Endpoints](#api-endpoints)
8. [Database Models](#database-models)
9. [Configuration](#configuration)
10. [Usage Examples](#usage-examples)

---

## Architecture

### Components

```
auth/
├── models.py           # SQLAlchemy models (User, RefreshToken, Session, AuditLog)
├── routes.py           # Authentication API endpoints
├── schemas.py          # Pydantic validation schemas (request/response)
├── dependencies.py     # FastAPI dependencies (get_current_user, require_role)
├── jwt.py              # JWT token creation and validation
├── permissions.py      # RBAC permission handlers
└── README.md           # This file
```

### Authentication Flow

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │ 1. POST /auth/login
       │    {username, password}
       ▼
┌─────────────────────┐
│   Auth Routes       │
│   (routes.py)       │
└──────┬──────────────┘
       │ 2. Validate credentials
       ▼
┌─────────────────────┐
│   User Model        │
│   verify_password() │
└──────┬──────────────┘
       │ 3. Generate tokens
       ▼
┌─────────────────────┐
│   JWT Handler       │
│   (jwt.py)          │
└──────┬──────────────┘
       │ 4. Return tokens
       ▼
┌─────────────────────┐
│   Client            │
│   Store tokens      │
└─────────────────────┘

       │ 5. API Request with token
       │    Authorization: Bearer <token>
       ▼
┌─────────────────────┐
│   Auth Middleware   │
│   (dependencies.py) │
└──────┬──────────────┘
       │ 6. Validate token
       │ 7. Check permissions
       ▼
┌─────────────────────┐
│   Protected Route   │
│   (API endpoint)    │
└─────────────────────┘
```

---

## User Roles

**Reference**: `/design/uml-diagram.md` - UserRole enumeration

### Role Hierarchy

```
ADMIN (Level 5)
  └─ Highest privileges, system administration
     └─ Can manage all users, tickets, and system settings

MANAGER (Level 4)
  └─ Department/team management
     └─ Can view all tickets, manage team members, access reports

TEAM_LEAD (Level 3)
  └─ Team supervision
     └─ Can assign tickets, escalate, manage team tickets

SENIOR_ENGINEER (Level 2)
  └─ Senior technical staff
     └─ Can handle escalated tickets, mentor engineers

DEVOPS_ENGINEER (Level 1)
  └─ Technical staff
     └─ Can be assigned tickets, update status, add comments

END_USER (Level 0)
  └─ Basic users
     └─ Can create tickets, view own tickets, add comments
```

### Role Permissions Matrix

| Action | END_USER | DEVOPS_ENG | SENIOR_ENG | TEAM_LEAD | MANAGER | ADMIN |
|--------|----------|------------|------------|-----------|---------|-------|
| Create Ticket | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| View Own Tickets | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| View All Tickets | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Update Ticket Status | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Assign Ticket | ✗ | ✗ | ✗ | ✓ | ✓ | ✓ |
| Escalate Ticket | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Delete Ticket | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ |
| Manage Users | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ |
| View Reports | ✗ | ✗ | ✗ | ✓ | ✓ | ✓ |
| Manage SLA Policies | ✗ | ✗ | ✗ | ✗ | ✓ | ✓ |
| System Settings | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ |

---

## Authentication Flow

### 1. User Registration

```bash
POST /api/v1/auth/register

Request:
{
  "username": "john.doe",
  "email": "john.doe@example.com",
  "password": "SecurePass123!",
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": "+1-555-0100",
  "department": "Infrastructure"
}

Response (201 Created):
{
  "id": "e8006210-bfd5-4742-955a-6d258029af00",
  "username": "john.doe",
  "email": "john.doe@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "role": "END_USER",
  "is_active": true,
  "is_email_verified": true,
  "created_at": "2025-11-16T17:45:23.123456+00:00"
}
```

**✅ Verified Working** (2025-11-16)

**Process**:
1. Validate input (username unique, email valid, password strong)
2. Hash password with bcrypt (direct bcrypt, 72-byte limit)
3. Create user record with default role (END_USER)
4. Send verification email (if EMAIL_VERIFICATION_REQUIRED=true)
5. Return user data (excluding password)

**Phone Format**: Supports international formats with spaces, hyphens, parentheses (e.g., `+1-555-0100`, `+44 20 1234 5678`)

### 2. User Login

```bash
POST /api/v1/auth/login

Request:
{
  "username": "admin",
  "password": "Admin123!"
}

Response (200 OK):
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0NjEyMTJmMC00OTQxLTQwYmMtYjFhYy0yYmNmZmY0MDZjMWYiLCJ1c2VybmFtZSI6ImFkbWluIiwiZW1haWwiOiJhZG1pbkBleGFtcGxlLmNvbSIsInJvbGUiOiJBRE1JTiIsInR5cGUiOiJhY2Nlc3MiLCJleHAiOjE3MzE3ODI0MTIsImlhdCI6MTczMTc4MTUxMiwianRpIjoiYldPNVRnIn0...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0NjEyMTJmMC00OTQxLTQwYmMtYjFhYy0yYmNmZmY0MDZjMWYiLCJ0eXBlIjoicmVmcmVzaCIsImV4cCI6MTczMjM4NjMxMiwiaWF0IjoxNzMxNzgxNTEyLCJqdGkiOiJkemRmeGxnIn0...",
  "token_type": "bearer",
  "expires_in": 900,
  "user": {
    "id": "461212f0-4941-40bc-b1ac-2bcfff406c1f",
    "username": "admin",
    "email": "admin@example.com",
    "first_name": "Admin",
    "last_name": "User",
    "phone_number": "+1-555-0104",
    "department": "IT",
    "role": "ADMIN",
    "is_active": true,
    "is_email_verified": true,
    "mfa_enabled": false,
    "created_at": "2025-11-16T17:48:05.834623+00:00",
    "updated_at": "2025-11-16T17:48:05.834623+00:00",
    "last_login": "2025-11-16T17:51:52.178392+00:00"
  }
}
```

**✅ Verified Working** (2025-11-16)

**Process**:
1. Validate credentials (username or email accepted)
2. Check account status (active, not locked)
3. Verify password hash with bcrypt
4. Generate access token (15 min expiry)
5. Generate refresh token (7 days expiry)
6. Store refresh token hash in database with device info
7. Create user session with session token
8. Record login success in audit log
9. Update last_login timestamp
10. Reset failed login attempts counter
11. Return tokens and full user data

**Security Features**:
- Account lockout after 5 failed attempts (30 min duration)
- Password attempt tracking
- Device and IP tracking for sessions
- Timezone-aware datetime handling

### 3. Token Refresh

```
POST /api/v1/auth/refresh

Request:
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}

Response (200 OK):
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 900
}
```

**Process**:
1. Validate refresh token signature
2. Check token not expired
3. Check token not revoked (database lookup)
4. Generate new access token
5. Optionally rotate refresh token
6. Return new tokens

### 4. User Logout

```
POST /api/v1/auth/logout

Headers:
Authorization: Bearer <access_token>

Request:
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}

Response (200 OK):
{
  "message": "Successfully logged out"
}
```

**Process**:
1. Revoke refresh token (mark as revoked in database)
2. Terminate user session
3. Record logout in audit log

---

## Authorization & Permissions

### Dependency-Based Authorization

**File**: `dependencies.py`

#### Get Current User

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get current authenticated user from JWT token
    """
    token = credentials.credentials

    # Decode and validate JWT token
    payload = decode_jwt_token(token)
    user_id = payload.get("sub")

    # Fetch user from database
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )

    return user
```

#### Require Specific Role

```python
from functools import wraps
from auth.models import UserRole

def require_role(required_role: UserRole):
    """
    Dependency factory to check if user has required role or higher
    """
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if not current_user.has_permission(required_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires {required_role.value} role or higher"
            )
        return current_user

    return role_checker
```

#### Permission-Based Access

```python
from enum import Enum

class Permission(str, Enum):
    VIEW_ALL_TICKETS = "view_all_tickets"
    ASSIGN_TICKETS = "assign_tickets"
    DELETE_TICKETS = "delete_tickets"
    MANAGE_USERS = "manage_users"
    VIEW_REPORTS = "view_reports"
    MANAGE_SLA = "manage_sla"

def check_permission(permission: Permission):
    """
    Dependency to check specific permission
    """
    def permission_checker(current_user: User = Depends(get_current_user)) -> User:
        # Permission mapping based on roles
        role_permissions = {
            UserRole.ADMIN: [p for p in Permission],  # All permissions
            UserRole.MANAGER: [
                Permission.VIEW_ALL_TICKETS,
                Permission.ASSIGN_TICKETS,
                Permission.VIEW_REPORTS,
                Permission.MANAGE_SLA
            ],
            UserRole.TEAM_LEAD: [
                Permission.VIEW_ALL_TICKETS,
                Permission.ASSIGN_TICKETS,
                Permission.VIEW_REPORTS
            ],
            UserRole.SENIOR_ENGINEER: [
                Permission.VIEW_ALL_TICKETS
            ],
            UserRole.DEVOPS_ENGINEER: [
                Permission.VIEW_ALL_TICKETS
            ],
            UserRole.END_USER: []
        }

        user_permissions = role_permissions.get(current_user.role, [])

        if permission not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions: {permission.value} required"
            )

        return current_user

    return permission_checker
```

### Usage in Routes

```python
from fastapi import APIRouter, Depends
from auth.dependencies import get_current_user, require_role, check_permission
from auth.models import UserRole

router = APIRouter()

# Public endpoint (no authentication)
@router.get("/public")
async def public_endpoint():
    return {"message": "Public access"}

# Authenticated endpoint (any logged-in user)
@router.get("/profile")
async def get_profile(current_user: User = Depends(get_current_user)):
    return current_user.to_dict()

# Role-based endpoint (requires specific role)
@router.get("/admin-only")
async def admin_endpoint(
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    return {"message": "Admin access granted"}

# Permission-based endpoint
@router.post("/tickets/{ticket_id}/assign")
async def assign_ticket(
    ticket_id: str,
    current_user: User = Depends(check_permission(Permission.ASSIGN_TICKETS))
):
    # Assign ticket logic
    pass
```

---

## JWT Token Management

**File**: `jwt.py`

### Token Structure

#### Access Token Payload
```json
{
  "sub": "550e8400-e29b-41d4-a716-446655440000",
  "username": "john.doe",
  "email": "john.doe@example.com",
  "role": "DEVOPS_ENGINEER",
  "type": "access",
  "exp": 1705406400,
  "iat": 1705405500,
  "jti": "unique-token-id"
}
```

#### Refresh Token Payload
```json
{
  "sub": "550e8400-e29b-41d4-a716-446655440000",
  "type": "refresh",
  "exp": 1706015100,
  "iat": 1705405500,
  "jti": "unique-refresh-token-id"
}
```

### Token Configuration

```python
# Token expiration times
ACCESS_TOKEN_EXPIRE_MINUTES = 15  # 15 minutes
REFRESH_TOKEN_EXPIRE_DAYS = 7     # 7 days

# JWT algorithm
JWT_ALGORITHM = "HS256"

# Secret key (from environment variable)
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")  # Min 32 characters
```

### Token Generation

```python
from datetime import datetime, timedelta
from jose import jwt
import secrets

def create_access_token(user: User) -> str:
    """Generate JWT access token"""
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        "sub": str(user.id),
        "username": user.username,
        "email": user.email,
        "role": user.role.value,
        "type": "access",
        "exp": expire,
        "iat": datetime.utcnow(),
        "jti": secrets.token_urlsafe(16)
    }

    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token

def create_refresh_token(user: User) -> str:
    """Generate JWT refresh token"""
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    payload = {
        "sub": str(user.id),
        "type": "refresh",
        "exp": expire,
        "iat": datetime.utcnow(),
        "jti": secrets.token_urlsafe(16)
    }

    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token
```

### Token Validation

```python
from jose import jwt, JWTError

def decode_jwt_token(token: str) -> dict:
    """Decode and validate JWT token"""
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM]
        )
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
```

---

## Security Features

### 1. Password Security

**Hashing**: bcrypt with cost factor 12

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hash password
hashed = pwd_context.hash("SecurePass123!")

# Verify password
is_valid = pwd_context.verify("SecurePass123!", hashed)
```

**Password Requirements**:
- Minimum 8 characters
- At least 1 uppercase letter
- At least 1 lowercase letter
- At least 1 digit
- At least 1 special character
- Not in common password list

### 2. Account Lockout

**Configuration**:
- Max failed attempts: 5
- Lockout duration: 30 minutes
- Auto-unlock after duration

```python
def record_failed_login(user: User, db: Session):
    """Record failed login attempt"""
    user.failed_login_attempts += 1

    if user.failed_login_attempts >= 5:
        user.account_locked_until = datetime.utcnow() + timedelta(minutes=30)
        user.status = UserStatus.LOCKED

    db.commit()
```

### 3. Email Verification

```python
# Generate verification token
verification_token = secrets.token_urlsafe(32)
user.email_verification_token = verification_token

# Send verification email with link
verification_link = f"https://app.example.com/verify?token={verification_token}"
send_verification_email(user.email, verification_link)
```

### 4. Password Reset

```
POST /api/v1/auth/forgot-password
{
  "email": "john.doe@example.com"
}

# Generates reset token valid for 1 hour
# Sends email with reset link
```

```
POST /api/v1/auth/reset-password
{
  "token": "reset-token-from-email",
  "new_password": "NewSecurePass123!"
}
```

### 5. Session Management

**Features**:
- Track active sessions per user
- View all active sessions
- Force logout from specific device
- Concurrent session limits

```python
# Maximum concurrent sessions per user
MAX_SESSIONS_PER_USER = 5

def create_session(user: User, device_info: dict, db: Session):
    """Create new user session"""
    # Check concurrent session limit
    active_sessions = db.query(UserSession).filter(
        UserSession.user_id == user.id,
        UserSession.is_active == True
    ).count()

    if active_sessions >= MAX_SESSIONS_PER_USER:
        # Terminate oldest session
        oldest = db.query(UserSession).filter(
            UserSession.user_id == user.id,
            UserSession.is_active == True
        ).order_by(UserSession.created_at).first()
        oldest.terminate()

    # Create new session
    session = UserSession(
        user_id=user.id,
        session_token=secrets.token_urlsafe(32),
        ip_address=device_info.get("ip"),
        user_agent=device_info.get("user_agent"),
        expires_at=datetime.utcnow() + timedelta(days=7)
    )
    db.add(session)
    db.commit()
```

### 6. Audit Logging

**Logged Events**:
- LOGIN_SUCCESS
- LOGIN_FAILED
- LOGOUT
- PASSWORD_CHANGE
- PASSWORD_RESET_REQUEST
- PASSWORD_RESET_COMPLETE
- EMAIL_VERIFICATION
- ACCOUNT_LOCKED
- ACCOUNT_UNLOCKED
- ROLE_CHANGED
- PROFILE_UPDATED

```python
def log_auth_event(
    user_id: str,
    event_type: str,
    event_status: str,
    ip_address: str,
    user_agent: str,
    db: Session
):
    """Create audit log entry"""
    audit_log = AuditLog(
        user_id=user_id,
        event_type=event_type,
        event_status=event_status,
        ip_address=ip_address,
        user_agent=user_agent
    )
    db.add(audit_log)
    db.commit()
```

### 7. MFA Support (Optional)

**Time-based One-Time Password (TOTP)**:

```python
import pyotp

# Generate MFA secret
def generate_mfa_secret(user: User):
    secret = pyotp.random_base32()
    user.mfa_secret = secret
    user.mfa_enabled = True
    return secret

# Generate QR code for authenticator app
def get_mfa_qr_code(user: User):
    totp = pyotp.TOTP(user.mfa_secret)
    provisioning_uri = totp.provisioning_uri(
        name=user.email,
        issuer_name="Ticket Management System"
    )
    return provisioning_uri  # Convert to QR code image

# Verify MFA code
def verify_mfa_code(user: User, code: str) -> bool:
    totp = pyotp.TOTP(user.mfa_secret)
    return totp.verify(code, valid_window=1)
```

---

## API Endpoints

### Authentication Endpoints (Port 8001)

All endpoints are prefixed with `/api/v1/auth`

#### Public Endpoints (No Authentication Required)

| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| POST | `/register` | Register new user | ✅ Working |
| POST | `/login` | User login | ✅ Working |
| POST | `/refresh` | Refresh access token | ✅ Working |
| POST | `/forgot-password` | Request password reset | ✅ Working |
| POST | `/reset-password` | Reset password with token | ✅ Working |

#### Protected Endpoints (Requires Access Token)

| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| GET | `/me` | Get current user profile | ✅ Working |
| PUT | `/me` | Update current user profile | ✅ Working |
| PATCH | `/change-password` | Change password | ✅ Working |
| POST | `/logout` | User logout | ✅ Working |
| GET | `/sessions` | List active sessions | ✅ Working |
| DELETE | `/sessions/{id}` | Terminate specific session | ✅ Working |

#### Admin Endpoints (Requires ADMIN Role)

| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| GET | `/admin/users` | List all users (with filters) | ✅ Working |
| GET | `/admin/users/{id}` | Get user by ID | ✅ Working |
| PUT | `/admin/users/{id}` | Update user | ✅ Working |
| PATCH | `/admin/users/{id}/role` | Update user role | ✅ Working |
| PATCH | `/admin/users/{id}/status` | Update user status | ✅ Working |
| DELETE | `/admin/users/{id}` | Soft delete user | ✅ Working |
| GET | `/admin/tokens/user/{id}` | List user's tokens | ✅ Working |
| DELETE | `/admin/tokens/{id}` | Revoke specific token | ✅ Working |
| DELETE | `/admin/tokens/user/{id}/revoke-all` | Revoke all user tokens | ✅ Working |
| GET | `/admin/audit-logs` | Get audit logs (with filters) | ✅ Working |

**Base URL**: `http://localhost:8001/api/v1/auth`

**All endpoints verified working**: 2025-11-16

---

## Database Models

### User Model

```python
class User(Base):
    __tablename__ = "users"

    # Primary key
    id = Column(UUID, primary_key=True, default=uuid.uuid4)

    # Authentication
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)

    # Profile
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone_number = Column(String(20))
    department = Column(String(100))

    # Role & Status
    role = Column(Enum(UserRole), default=UserRole.END_USER)
    status = Column(Enum(UserStatus), default=UserStatus.ACTIVE)
    is_active = Column(Boolean, default=True)

    # Security
    is_email_verified = Column(Boolean, default=False)
    failed_login_attempts = Column(Integer, default=0)
    account_locked_until = Column(DateTime)

    # MFA
    mfa_enabled = Column(Boolean, default=False)
    mfa_secret = Column(String(255))

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    last_login = Column(DateTime)
```

### RefreshToken Model

```python
class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID, ForeignKey("users.id"))

    # Token fields
    token_hash = Column(String(255), unique=True, nullable=False, index=True)
    token_family = Column(UUID, default=uuid.uuid4)

    # Device & Location
    device_type = Column(String(50))
    device_name = Column(String(100))
    user_agent = Column(Text)
    ip_address = Column(String(45))
    location = Column(String(255))

    # Status & Expiry
    is_revoked = Column(Boolean, default=False)
    revoked_at = Column(DateTime(timezone=True))
    revoked_reason = Column(String(255))
    expires_at = Column(DateTime(timezone=True), nullable=False)
    last_used_at = Column(DateTime(timezone=True))

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

**Note**: Stores hashed token (SHA-256) for security, not plain token

### UserSession Model

```python
class UserSession(Base):
    __tablename__ = "user_sessions"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID, ForeignKey("users.id"))

    # Session fields
    session_token = Column(String(255), unique=True, nullable=False)
    refresh_token_id = Column(UUID, ForeignKey("refresh_tokens.id", ondelete="SET NULL"))

    # Device & Location
    device_type = Column(String(50))
    device_name = Column(String(100))
    user_agent = Column(Text)
    ip_address = Column(String(45), nullable=False)
    location = Column(String(255))

    # Session status
    is_active = Column(Boolean, default=True)
    ended_at = Column(DateTime(timezone=True))
    end_reason = Column(String(100))  # logout, timeout, revoked, expired, replaced

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_activity_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
```

### AuditLog Model

```python
class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID, ForeignKey("users.id"))

    # Event details
    action_type = Column(Enum(AuditEventType), nullable=False)
    status = Column(String(20), nullable=False)  # SUCCESS, FAILURE
    severity = Column(String(10), nullable=False)  # INFO, WARN, ERROR

    # Resource information
    resource_type = Column(String(50))  # USER, TOKEN, SESSION
    resource_id = Column(UUID)

    # Context
    ip_address = Column(String(45))
    user_agent = Column(Text)
    details = Column(JSON)  # Additional metadata

    # Timestamp
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
```

**AuditEventType Enum** (28 values):
- LOGIN_SUCCESS, LOGIN_FAILED, LOGOUT, TOKEN_REFRESH
- PASSWORD_CHANGE, PASSWORD_RESET_REQUEST, PASSWORD_RESET_COMPLETE
- ACCOUNT_CREATED, ACCOUNT_LOCKED, ACCOUNT_UNLOCKED, ACCOUNT_DELETED
- ACCOUNT_ENABLED, ACCOUNT_DISABLED
- EMAIL_VERIFICATION_SENT, EMAIL_VERIFIED
- PROFILE_UPDATED, USER_UPDATED, ROLE_CHANGED
- TOKEN_REVOKED, TOKENS_REVOKED
- MFA_ENABLED, MFA_DISABLED, MFA_CODE_VERIFIED
- SESSION_CREATED, SESSION_TERMINATED

---

## Configuration

### Environment Variables

```bash
# JWT Configuration
JWT_SECRET_KEY=your-secret-key-min-32-characters-long
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Password Policy
PASSWORD_MIN_LENGTH=8
PASSWORD_REQUIRE_UPPERCASE=true
PASSWORD_REQUIRE_LOWERCASE=true
PASSWORD_REQUIRE_DIGIT=true
PASSWORD_REQUIRE_SPECIAL=true

# Account Security
MAX_FAILED_LOGIN_ATTEMPTS=5
ACCOUNT_LOCKOUT_DURATION_MINUTES=30
MAX_SESSIONS_PER_USER=5

# Email Verification
EMAIL_VERIFICATION_REQUIRED=true
EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS=24

# Password Reset
PASSWORD_RESET_TOKEN_EXPIRE_HOURS=1

# MFA
MFA_ENABLED=false
MFA_ISSUER_NAME="Ticket Management System"
```

---

## Usage Examples

### Example 1: Register and Login

```python
import requests

# 1. Register new user
register_response = requests.post(
    "http://localhost:8000/api/v1/auth/register",
    json={
        "username": "jane.smith",
        "email": "jane.smith@example.com",
        "password": "SecurePass123!",
        "first_name": "Jane",
        "last_name": "Smith",
        "department": "DevOps"
    }
)
print(register_response.json())

# 2. Login
login_response = requests.post(
    "http://localhost:8000/api/v1/auth/login",
    json={
        "username": "jane.smith",
        "password": "SecurePass123!"
    }
)
tokens = login_response.json()
access_token = tokens["access_token"]
refresh_token = tokens["refresh_token"]

# 3. Access protected endpoint
headers = {"Authorization": f"Bearer {access_token}"}
profile_response = requests.get(
    "http://localhost:8000/api/v1/auth/me",
    headers=headers
)
print(profile_response.json())
```

### Example 2: Token Refresh

```python
# When access token expires, refresh it
refresh_response = requests.post(
    "http://localhost:8000/api/v1/auth/refresh",
    json={"refresh_token": refresh_token}
)
new_tokens = refresh_response.json()
access_token = new_tokens["access_token"]
```

### Example 3: Password Reset

```python
# 1. Request password reset
forgot_response = requests.post(
    "http://localhost:8000/api/v1/auth/forgot-password",
    json={"email": "jane.smith@example.com"}
)

# 2. User receives email with reset token
# 3. Reset password with token
reset_response = requests.post(
    "http://localhost:8000/api/v1/auth/reset-password",
    json={
        "token": "reset-token-from-email",
        "new_password": "NewSecurePass456!"
    }
)
```

---

## Testing

### Unit Tests

```bash
# Run auth module tests
pytest tests/unit/test_auth_service.py -v

# Test JWT token generation
pytest tests/unit/test_jwt.py -v

# Test permissions
pytest tests/unit/test_permissions.py -v
```

### Integration Tests

```bash
# Run auth API tests
pytest tests/integration/test_auth_api.py -v
```

---

## Troubleshooting

### Common Issues

**"Invalid or expired token"**
- Check token expiration time (access tokens expire after 15 minutes)
- Ensure JWT_SECRET_KEY is consistent across restarts
- Verify token format in Authorization header: `Bearer <token>`
- Use `/refresh` endpoint to get new access token

**"Account locked"**
- Wait for lockout duration (30 minutes)
- Admin can manually unlock: `UPDATE users SET account_locked_until = NULL WHERE username = 'username'`
- Check `failed_login_attempts` counter

**"Email already exists" / "Username already exists"**
- Username and email must be unique
- Check database: `SELECT * FROM users WHERE username = 'username' OR email = 'email@example.com'`
- Delete test user if needed: `DELETE FROM users WHERE username = 'username'`

**"Insufficient permissions" / 403 Forbidden**
- Verify user role has required permissions (see permission matrix)
- Admin endpoints require ADMIN role
- Check access token contains correct role in payload
- Generate fresh token if role was recently updated

**"can't compare offset-naive and offset-aware datetimes"**
- ✅ FIXED - All datetime operations now use `datetime.now(timezone.utc)`
- Ensure all datetime columns use `DateTime(timezone=True)`

**"Column 'token' does not exist" / "Column 'device_info' does not exist"**
- ✅ FIXED - Models updated to match database schema
- RefreshToken uses `token_hash` not `token`
- UserSession uses individual device fields, not `device_info` dict

**Phone number validation errors**
- ✅ FIXED - Supports international formats: `+1-555-0100`, `+44 20 1234 5678`
- Accepts spaces, hyphens, parentheses
- Length: 10-20 characters

**"violates check constraint" errors**
- ✅ FIXED - All constraints aligned with enums
- `action_type`: 28 AuditEventType values supported
- `end_reason`: logout, timeout, revoked, expired, replaced
- `status`: SUCCESS, FAILURE

---

## Security Best Practices

1. **Never log passwords or tokens** (even in debug mode)
2. **Use HTTPS in production** (TLS 1.2+)
3. **Rotate JWT_SECRET_KEY periodically**
4. **Implement rate limiting** on auth endpoints
5. **Monitor failed login attempts**
6. **Regular security audits** of audit logs
7. **Keep dependencies updated** (especially security-related)
8. **Use strong JWT_SECRET_KEY** (min 32 random characters)

---

## References

- **User Entity**: `/design/uml-diagram.md` (lines 43-64)
- **Database Schema**: `/backend/DATABASE_SCHEMA.md`
- **API Documentation**: `/backend/API_DOCUMENTATION.md`
- **JWT Standard**: RFC 7519

---

## Support

For authentication-related issues, refer to:
- Main backend README: `/backend/README.md`
- Database schema: `/backend/DATABASE_SCHEMA.md`
- Troubleshooting section above
