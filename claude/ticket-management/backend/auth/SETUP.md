# Authentication Service Setup Guide

## Overview

Complete authentication service for the Ticket Management System with JWT-based authentication, RBAC, and comprehensive security features.

## What Was Created

### Core Components

1. **models.py** - SQLAlchemy database models
   - User, RefreshToken, UserSession, PasswordReset, AuditLog
   - Aligned with database migrations from `/backend/db_migrations/`

2. **schemas.py** - Pydantic validation schemas
   - Request/response models for all endpoints
   - Password strength validation
   - Email validation

3. **jwt.py** - JWT token management
   - Access token generation (15 min expiry)
   - Refresh token generation (7 day expiry)
   - Token validation and decoding

4. **dependencies.py** - FastAPI dependencies
   - get_current_user()
   - Role-based authorization
   - Permission checking
   - Request context extraction

5. **permissions.py** - RBAC system
   - 6 user roles with hierarchical levels
   - 30+ granular permissions
   - Permission checking functions

6. **config.py** - Configuration management
   - Environment-based settings
   - JWT configuration
   - Security policies

7. **utils.py** - Utility functions
   - Token generation
   - Password utilities
   - Audit logging
   - Email helpers (placeholders)

8. **routes.py** - API endpoints
   - /api/v1/auth/register
   - /api/v1/auth/login
   - /api/v1/auth/logout
   - /api/v1/auth/refresh
   - /api/v1/auth/me
   - /api/v1/auth/change-password
   - /api/v1/auth/forgot-password
   - /api/v1/auth/reset-password
   - /api/v1/auth/sessions

9. **main.py** - FastAPI application
   - CORS middleware
   - Error handling
   - Health check endpoint
   - Database initialization

10. **Dockerfile** - Multi-stage Docker build
    - Optimized image size
    - Non-root user
    - Health checks

11. **requirements.txt** - Python dependencies
    - FastAPI, SQLAlchemy, Passlib, python-jose
    - All necessary authentication libraries

12. **.env.example** - Environment template
    - All configuration options documented
    - Secure defaults

## Quick Start

### 1. Using Docker Compose (Recommended)

```bash
# Navigate to backend directory
cd /mnt/d/vscode/epam_git/mcp/claude/ticket-management/backend

# Start all services (database, migrations, auth service)
docker-compose up -d

# View logs
docker-compose logs -f auth-service

# Check service health
curl http://localhost:8001/health

# Access API documentation
open http://localhost:8001/docs
```

### 2. Local Development

```bash
# Navigate to auth directory
cd /mnt/d/vscode/epam_git/mcp/claude/ticket-management/backend/auth

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env with your configuration
nano .env

# Run the service
python main.py

# Or with uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

## Database Integration

The auth service uses the database tables created by Flyway migrations:

- **users** - V1__create_users_table.sql
- **refresh_tokens** - V2__create_refresh_tokens_table.sql
- **user_sessions** - V3__create_user_sessions_table.sql
- **password_resets** - V4__create_password_resets_table.sql
- **audit_logs** - V5__create_audit_logs_table.sql

All tables are automatically created by Flyway before the auth service starts (see docker-compose.yml dependency chain).

## API Usage Examples

### Register a New User

```bash
curl -X POST http://localhost:8001/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john.doe",
    "email": "john.doe@example.com",
    "password": "SecurePass123!",
    "first_name": "John",
    "last_name": "Doe",
    "department": "Engineering"
  }'
```

### Login

```bash
curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john.doe",
    "password": "SecurePass123!"
  }'
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 900,
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "john.doe",
    "email": "john.doe@example.com",
    "role": "END_USER",
    ...
  }
}
```

### Access Protected Endpoint

```bash
curl -X GET http://localhost:8001/api/v1/auth/me \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Refresh Token

```bash
curl -X POST http://localhost:8001/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }'
```

## User Roles & Permissions

### Role Hierarchy (Highest to Lowest)

1. **ADMIN** (Level 5) - Full system access
2. **MANAGER** (Level 4) - Department management
3. **TEAM_LEAD** (Level 3) - Team supervision
4. **SENIOR_ENGINEER** (Level 2) - Senior technical staff
5. **DEVOPS_ENGINEER** (Level 1) - Technical staff
6. **END_USER** (Level 0) - Basic users

### Key Permissions

- **CREATE_TICKET** - All roles
- **VIEW_ALL_TICKETS** - DEVOPS_ENGINEER and above
- **ASSIGN_TICKET** - TEAM_LEAD and above
- **DELETE_TICKET** - MANAGER and above
- **MANAGE_USERS** - ADMIN only

See `/backend/auth/permissions.py` for complete permission matrix.

## Security Features

### Implemented

✅ JWT-based authentication (access + refresh tokens)
✅ Bcrypt password hashing (cost factor 12)
✅ Account lockout after failed attempts (5 attempts, 30 min lockout)
✅ Session management and tracking
✅ Audit logging for security events
✅ Role-based access control (RBAC)
✅ Permission-based authorization
✅ Password strength validation
✅ Refresh token rotation support
✅ Device and IP tracking
✅ Multi-session support (max 5 concurrent)

### Optional Features (Configured via .env)

- Email verification
- Multi-factor authentication (MFA/TOTP)
- Rate limiting
- Custom password policies

## Configuration

### Critical Settings

**JWT_SECRET_KEY** - MUST be changed in production!
```bash
# Generate a secure key:
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**DATABASE_URL** - Connection string
```
postgresql://user:password@host:port/database
```

### Security Policies

```env
MAX_FAILED_LOGIN_ATTEMPTS=5
ACCOUNT_LOCKOUT_DURATION_MINUTES=30
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
PASSWORD_MIN_LENGTH=8
```

## Monitoring & Logging

### Health Check

```bash
curl http://localhost:8001/health
```

### View Logs

```bash
# Docker
docker-compose logs -f auth-service

# Local
# Logs output to console with configured LOG_LEVEL
```

### Audit Logs

All authentication events are logged to the `audit_logs` table:
- Login success/failure
- Logout
- Password changes
- Account lockouts
- Token refresh
- Profile updates

## Testing

### Run Tests (when implemented)

```bash
pytest tests/ -v
```

### Manual Testing

Use the interactive API documentation:
http://localhost:8001/docs

## Troubleshooting

### Service won't start

1. Check database is running:
   ```bash
   docker-compose ps database
   ```

2. Check migrations completed:
   ```bash
   docker-compose logs flyway
   ```

3. Check auth service logs:
   ```bash
   docker-compose logs auth-service
   ```

### Authentication fails

1. Verify JWT_SECRET_KEY is set and consistent
2. Check token expiration (default: 15 minutes)
3. Ensure user account is active and not locked
4. Check audit logs for details

### Database connection errors

1. Verify DATABASE_URL format
2. Check PostgreSQL is accepting connections
3. Ensure network connectivity (docker network)

## Next Steps

### Recommended Additions

1. **Email Service Integration**
   - Implement actual email sending (SendGrid, AWS SES)
   - Update utils.py email functions

2. **MFA Implementation**
   - Complete MFA endpoints in routes.py
   - Add QR code generation

3. **Rate Limiting**
   - Add slowapi or similar middleware
   - Configure per-endpoint limits

4. **Tests**
   - Unit tests for all modules
   - Integration tests for API endpoints
   - Authentication flow tests

5. **Admin Endpoints**
   - User management (CRUD)
   - Role assignment
   - Audit log viewing

## References

- Full Documentation: `/backend/auth/README.md`
- Database Schema: `/backend/db_migrations/README.md`
- Database ERD: `/backend/db_migrations/database-erd.excalidraw`
- API Documentation: http://localhost:8001/docs (when running)

## Support

For issues or questions:
1. Check logs: `docker-compose logs auth-service`
2. Review configuration: `.env` file
3. Verify database tables exist
4. Check network connectivity between services
