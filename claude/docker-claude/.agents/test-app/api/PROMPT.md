# FastAPI Backend - UserHub API

Create a complete FastAPI backend for the UserHub user management application.

## Requirements

### Core Features
1. **User Authentication**
   - JWT token-based authentication
   - Login endpoint with email/password
   - Token refresh mechanism
   - Password hashing with bcrypt

2. **User Management CRUD**
   - Create user (registration)
   - Read user (get by ID, get all with pagination)
   - Update user (profile fields)
   - Delete user (soft delete with is_active flag)

3. **Database Integration**
   - PostgreSQL connection with asyncpg
   - SQLAlchemy ORM with async support
   - Alembic migrations
   - Connection pooling

4. **Security**
   - Password hashing
   - JWT token generation and validation
   - CORS configuration
   - Input validation with Pydantic
   - SQL injection prevention

## Files to Create

### 1. `main.py` (150-200 lines)
- FastAPI application initialization
- CORS middleware configuration
- Router registration
- Health check endpoint
- Exception handlers
- Startup and shutdown events

### 2. `models.py` (80-100 lines)
- SQLAlchemy User model
- Base model with common fields (id, created_at, updated_at)
- Relationship definitions
- Table indexes

### 3. `schemas.py` (120-150 lines)
- Pydantic models for request/response
- UserCreate, UserUpdate, UserResponse schemas
- LoginRequest, TokenResponse schemas
- Validation rules (email format, password strength)

### 4. `auth.py` (150-180 lines)
- JWT token creation and validation
- Password hashing and verification
- Authentication dependency
- Token refresh logic
- OAuth2PasswordBearer setup

### 5. `database.py` (80-100 lines)
- Database connection configuration
- Session management with async context manager
- Database URL from environment variables
- Connection pool settings

### 6. `crud.py` (200-250 lines)
- CRUD operations for users
- Async database queries
- Pagination helper functions
- Filter and search functionality
- Error handling for database operations

### 7. `routes/users.py` (150-200 lines)
- User CRUD endpoints:
  - POST /api/users/ (create user)
  - GET /api/users/ (list users with pagination)
  - GET /api/users/{id} (get single user)
  - PUT /api/users/{id} (update user)
  - DELETE /api/users/{id} (soft delete)
- Authentication required for protected endpoints

### 8. `routes/auth.py` (100-120 lines)
- POST /api/auth/login (login)
- POST /api/auth/register (register)
- POST /api/auth/refresh (refresh token)
- GET /api/auth/me (get current user)

### 9. `config.py` (60-80 lines)
- Settings class with Pydantic BaseSettings
- Environment variable loading
- Database URL, JWT secret, token expiry
- CORS origins configuration

### 10. `requirements.txt` (15-20 packages)
Include all dependencies with versions:
- fastapi>=0.104.0
- uvicorn[standard]>=0.24.0
- sqlalchemy>=2.0.0
- asyncpg>=0.29.0
- pydantic>=2.4.0
- pydantic-settings>=2.0.0
- python-jose[cryptography]>=3.3.0
- passlib[bcrypt]>=1.7.4
- python-multipart>=0.0.6
- alembic>=1.12.0
- python-dotenv>=1.0.0

### 11. `.env.example`
Template for environment variables:
```
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/userhub
JWT_SECRET_KEY=your-secret-key-here-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### 12. `alembic.ini`
Alembic configuration for database migrations

### 13. `alembic/env.py`
Alembic environment setup with async support

### 14. `alembic/versions/001_initial.py`
Initial migration creating users table

## Technical Stack
- **Framework**: FastAPI 0.104+
- **Python**: 3.10+
- **Database**: PostgreSQL with asyncpg driver
- **ORM**: SQLAlchemy 2.0 (async)
- **Authentication**: JWT with python-jose
- **Password Hashing**: bcrypt via passlib
- **Migrations**: Alembic
- **Validation**: Pydantic v2

## Code Quality Requirements
- ✅ Type hints for all functions
- ✅ Async/await for all I/O operations
- ✅ Comprehensive error handling
- ✅ Input validation with Pydantic
- ✅ Docstrings for public functions
- ✅ Follow PEP 8 style guidelines
- ✅ SQL injection prevention (parameterized queries)
- ✅ No hardcoded secrets
- ✅ Production-ready code (no TODOs)

## API Endpoints Summary

### Authentication (Public)
- POST `/api/auth/register` - Register new user
- POST `/api/auth/login` - Login and get tokens
- POST `/api/auth/refresh` - Refresh access token

### Users (Protected)
- GET `/api/users/` - List users (pagination: ?skip=0&limit=10)
- POST `/api/users/` - Create user (admin only)
- GET `/api/users/{id}` - Get user by ID
- PUT `/api/users/{id}` - Update user
- DELETE `/api/users/{id}` - Soft delete user

### Health
- GET `/health` - Health check endpoint

## Directory Structure
```
api/
├── main.py
├── models.py
├── schemas.py
├── auth.py
├── database.py
├── crud.py
├── config.py
├── requirements.txt
├── .env.example
├── alembic.ini
├── routes/
│   ├── __init__.py
│   ├── auth.py
│   └── users.py
└── alembic/
    ├── env.py
    └── versions/
        └── 001_initial.py
```

## Special Instructions
1. Use async/await for all database operations
2. Implement proper dependency injection for database sessions
3. Add comprehensive exception handling with proper HTTP status codes
4. Include request/response examples in docstrings
5. Add pagination for list endpoints
6. Implement field-level permissions (users can update their own profile)
7. Add database indexes on frequently queried fields (email, username)
8. Include CORS middleware with configurable origins
9. Log important events (login attempts, user creation)
10. Make the API ready to run with `uvicorn main:app --reload`
