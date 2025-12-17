# Backend - Ticket Management System

## Overview

This directory contains the backend implementation for the **Ticket Management System**, a comprehensive DevOps ticketing solution designed to handle infrastructure support requests, incident management, and service requests.

**Technology Stack**: Python 3.11+ | FastAPI | PostgreSQL | Redis | Celery

**Design Reference**: This implementation follows the specifications in `/design` folder including:
- System Architecture: `/design/system-architecture.excalidraw`
- UML Diagrams: `/design/uml-diagram.md`
- State Management: `/design/state-diagram.md`
- Workflow: `/design/flow-diagram.md`
- Interactions: `/design/sequence-diagram.md`

---

## Directory Structure

```
backend/
│
├── auth/                          # Authentication & Authorization Module
│   ├── __init__.py
│   ├── models.py                 # User, Role, Session, Token models
│   ├── routes.py                 # Auth API endpoints
│   ├── schemas.py                # Pydantic validation schemas
│   ├── dependencies.py           # Auth dependencies & middleware
│   ├── jwt.py                    # JWT token management
│   ├── permissions.py            # RBAC permission handlers
│   └── README.md                 # Auth module documentation
│
├── api/                          # API Layer
│   ├── v1/                       # API Version 1
│   │   ├── __init__.py
│   │   ├── tickets.py           # Ticket management endpoints
│   │   ├── users.py             # User management endpoints
│   │   ├── comments.py          # Comment endpoints
│   │   ├── attachments.py       # File attachment endpoints
│   │   ├── notifications.py     # Notification endpoints
│   │   ├── escalations.py       # Escalation endpoints
│   │   ├── sla.py               # SLA policy endpoints
│   │   ├── reports.py           # Analytics & reporting endpoints
│   │   └── health.py            # Health check endpoints
│   └── __init__.py
│
├── models/                       # Database Models (SQLAlchemy ORM)
│   ├── __init__.py
│   ├── base.py                  # Base model class
│   ├── user.py                  # User entity
│   ├── ticket.py                # Ticket entity
│   ├── comment.py               # Comment entity
│   ├── attachment.py            # Attachment entity
│   ├── notification.py          # Notification entity
│   ├── sla_policy.py            # SLA Policy entity
│   ├── escalation.py            # Escalation entity
│   ├── ticket_history.py        # Ticket audit history
│   └── enums.py                 # Shared enumerations
│
├── schemas/                      # Pydantic Schemas (Request/Response)
│   ├── __init__.py
│   ├── base.py                  # Base schema classes
│   ├── ticket.py                # Ticket schemas
│   ├── user.py                  # User schemas
│   ├── comment.py               # Comment schemas
│   ├── notification.py          # Notification schemas
│   ├── attachment.py            # Attachment schemas
│   ├── escalation.py            # Escalation schemas
│   └── sla.py                   # SLA schemas
│
├── services/                     # Business Logic Layer
│   ├── __init__.py
│   ├── ticket_service.py        # Ticket operations & workflow
│   ├── user_service.py          # User management
│   ├── notification_service.py  # Multi-channel notifications
│   ├── assignment_service.py    # Auto-assignment & routing
│   ├── sla_service.py           # SLA monitoring & enforcement
│   ├── escalation_service.py    # Escalation management
│   ├── comment_service.py       # Comment operations
│   ├── attachment_service.py    # File handling
│   └── report_service.py        # Analytics & reporting
│
├── repositories/                 # Data Access Layer (Repository Pattern)
│   ├── __init__.py
│   ├── base_repository.py       # Abstract base repository
│   ├── ticket_repository.py     # Ticket data access
│   ├── user_repository.py       # User data access
│   ├── comment_repository.py    # Comment data access
│   ├── notification_repository.py
│   └── audit_repository.py      # Audit log access
│
├── core/                         # Core Configuration & Utilities
│   ├── __init__.py
│   ├── config.py                # Application configuration (Pydantic Settings)
│   ├── database.py              # Database session & connection
│   ├── security.py              # Security utilities (hashing, tokens)
│   ├── logging.py               # Logging configuration
│   ├── exceptions.py            # Custom exception classes
│   └── constants.py             # Application constants
│
├── middleware/                   # Custom Middleware
│   ├── __init__.py
│   ├── auth_middleware.py       # JWT authentication middleware
│   ├── cors_middleware.py       # CORS configuration
│   ├── rate_limit.py            # Rate limiting middleware
│   ├── logging_middleware.py    # Request/response logging
│   └── error_handler.py         # Global error handling
│
├── workers/                      # Background Workers (Celery)
│   ├── __init__.py
│   ├── celery_app.py            # Celery configuration
│   ├── notification_worker.py   # Async notification sender
│   ├── sla_monitor_worker.py    # SLA breach monitoring
│   ├── email_worker.py          # Email sending tasks
│   └── sms_worker.py            # SMS sending tasks
│
├── utils/                        # Utility Functions
│   ├── __init__.py
│   ├── email.py                 # Email utilities
│   ├── sms.py                   # SMS utilities (Twilio)
│   ├── validators.py            # Custom validators
│   ├── helpers.py               # Helper functions
│   ├── file_handler.py          # File upload/download utilities
│   └── date_utils.py            # Date/time utilities
│
├── db_migrations/                # Database Migrations (Flyway SQL)
│   ├── V1__initial_schema.sql
│   ├── V2__auth_tables.sql
│   ├── V3__ticket_tables.sql
│   ├── V4__notification_tables.sql
│   ├── V5__sla_escalation_tables.sql
│   ├── V6__indexes_optimization.sql
│   └── README.md                # Migration documentation
│
├── tests/                        # Test Suite
│   ├── __init__.py
│   ├── conftest.py              # Pytest fixtures & configuration
│   ├── unit/                    # Unit tests
│   │   ├── test_ticket_service.py
│   │   ├── test_auth_service.py
│   │   ├── test_sla_service.py
│   │   └── ...
│   ├── integration/             # Integration tests
│   │   ├── test_ticket_api.py
│   │   ├── test_auth_api.py
│   │   └── ...
│   └── e2e/                     # End-to-end tests
│       └── test_ticket_workflow.py
│
├── alembic/                      # Alembic migrations (alternative to Flyway)
│   ├── versions/
│   ├── env.py
│   └── alembic.ini
│
├── main.py                       # FastAPI application entry point
├── requirements.txt              # Python dependencies
├── requirements-dev.txt          # Development dependencies
├── .env.example                  # Environment variables template
├── Dockerfile                    # Docker container definition
├── docker-compose.yml            # Docker services orchestration
├── pytest.ini                    # Pytest configuration
├── .flake8                       # Flake8 linting configuration
├── .pylintrc                     # Pylint configuration
├── README.md                     # This file
├── ARCHITECTURE.md               # Detailed architecture documentation
├── DATABASE_SCHEMA.md            # Complete database schema reference
└── API_DOCUMENTATION.md          # API endpoint documentation
```

---

## Quick Start

### Prerequisites

```bash
# Required
- Python 3.11+
- PostgreSQL 14+
- Redis 6+

# Optional (for full stack)
- Docker & Docker Compose
- Node.js 18+ (for frontend)
```

### Environment Setup

1. **Clone and navigate to backend**
```bash
cd backend
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For development
```

4. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Initialize database**
```bash
# Run Flyway migrations
flyway migrate -configFiles=db_migrations/flyway.conf

# OR use Alembic
alembic upgrade head
```

6. **Start the application**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

7. **Access API documentation**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Docker Setup

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

---

## Core Features

### 1. Authentication & Authorization

**Reference**: `/design/uml-diagram.md` - User entity

- **JWT Token-based Authentication**
  - Access tokens (15 minutes expiry)
  - Refresh tokens (7 days expiry)
  - Token rotation on refresh

- **Role-Based Access Control (RBAC)**
  - 6 User Roles: ADMIN, MANAGER, TEAM_LEAD, SENIOR_ENGINEER, DEVOPS_ENGINEER, END_USER
  - Hierarchical permissions
  - Resource-level access control

- **Security Features**
  - Password hashing with bcrypt
  - Account lockout after failed attempts
  - Email verification
  - Password reset functionality
  - MFA support (optional)
  - Session management with Redis

**Details**: See `/backend/auth/README.md`

---

### 2. Ticket Management

**Reference**: `/design/uml-diagram.md` - Ticket entity, `/design/state-diagram.md`

#### Ticket Lifecycle States

```
NEW → OPEN → IN_PROGRESS → RESOLVED → CLOSED
         ↓          ↓            ↓
   PENDING_INFO  ESCALATED   REOPENED
```

#### Features
- Create, read, update, delete tickets
- Auto-assignment by category
- Priority-based routing (P1-Critical, P2-High, P3-Medium, P4-Low)
- Category classification (VM, Network, Storage, Database, Security, etc.)
- Full-text search
- Advanced filtering and sorting
- Attachment support
- Comment threading
- State machine validation

**State Transition Rules**: See `/design/state-diagram.md`

---

### 3. SLA Management

**Reference**: `/design/uml-diagram.md` - SLAPolicy entity

#### Priority-Based SLA Policies

| Priority | Response Time | Resolution Time | Auto-Escalate |
|----------|---------------|-----------------|---------------|
| P1 (Critical) | 5 minutes | 4 hours | After 15 min |
| P2 (High) | 30 minutes | 8 hours | After 1 hour |
| P3 (Medium) | 2 hours | 24 hours | After 4 hours |
| P4 (Low) | 1 day | 5 days | After 2 days |

#### Features
- Automatic SLA calculation
- Breach detection (scheduled job every 5 minutes)
- Due date calculation
- SLA compliance reporting
- Custom SLA policies per category

---

### 4. Escalation Management

**Reference**: `/design/flow-diagram.md` - Emergency Ticket Flow

#### Escalation Triggers
- SLA breach detection
- Manual escalation by engineer
- Critical priority (P1) tickets
- Multiple reopens (after 2nd reopen)

#### Escalation Path
```
DevOps Engineer → Senior Engineer → Team Lead → Manager → Admin
```

#### Features
- Multi-level escalation
- Automatic notification to next level
- Escalation history tracking
- Acknowledgment tracking
- Escalation metrics

---

### 5. Notification System

**Reference**: `/design/flow-diagram.md` - Notification Flow

#### Notification Channels
- **Email**: SMTP integration
- **SMS**: Twilio integration
- **In-App**: Real-time notifications
- **Slack**: Webhook integration (future)

#### Notification Events
- Ticket created
- Ticket assigned
- Status changed
- Comment added
- SLA breach warning
- Escalation triggered
- Resolution requested
- Ticket closed

#### Features
- Template-based messages
- Multi-channel delivery
- Delivery status tracking
- Retry logic for failures
- User notification preferences

---

### 6. Assignment & Routing

**Reference**: `/design/sequence-diagram.md` - Assign Ticket Sequence

#### Auto-Assignment Strategy
- **Category-based routing**: VM issues → VM specialists
- **Load balancing**: Distribute evenly across available engineers
- **Skill matching**: Match ticket requirements to engineer skills
- **Availability checking**: Only assign to active engineers
- **Round-robin distribution**: Fair workload distribution

#### Manual Assignment
- Assign to specific engineer
- Reassign tickets
- Bulk assignment operations

---

### 7. Audit & History

**Reference**: `/design/uml-diagram.md` - TicketHistory entity

#### Tracked Changes
- Status transitions
- Assignment changes
- Priority updates
- Field modifications
- Comment additions
- Attachments uploaded

#### Audit Log Features
- Complete audit trail
- User action tracking
- Timestamp recording
- IP address logging
- Rollback capability (view history)

---

## API Overview

### Base URL
```
http://localhost:8000/api/v1
```

### Authentication
All protected endpoints require JWT token in header:
```
Authorization: Bearer <access_token>
```

### API Endpoints Summary

#### Authentication (`/api/v1/auth`)
- `POST /register` - User registration
- `POST /login` - User login (returns JWT tokens)
- `POST /logout` - User logout
- `POST /refresh` - Refresh access token
- `POST /forgot-password` - Request password reset
- `POST /reset-password` - Reset password with token
- `GET /me` - Get current user profile
- `PUT /me` - Update current user profile

#### Tickets (`/api/v1/tickets`)
- `GET /` - List tickets (with pagination & filters)
- `POST /` - Create new ticket
- `GET /{id}` - Get ticket details
- `PUT /{id}` - Update ticket
- `DELETE /{id}` - Delete ticket
- `PATCH /{id}/status` - Update ticket status
- `POST /{id}/assign` - Assign ticket to engineer
- `POST /{id}/escalate` - Escalate ticket
- `GET /{id}/history` - Get ticket history timeline
- `POST /{id}/comments` - Add comment to ticket
- `GET /{id}/comments` - List ticket comments
- `POST /{id}/attachments` - Upload attachment
- `GET /{id}/attachments` - List attachments

#### Users (`/api/v1/users`)
- `GET /` - List users (Admin only)
- `POST /` - Create user (Admin only)
- `GET /{id}` - Get user details
- `PUT /{id}` - Update user
- `DELETE /{id}` - Deactivate user (Admin only)
- `PATCH /{id}/role` - Update user role (Admin only)
- `GET /{id}/tickets` - Get user's tickets
- `GET /{id}/stats` - Get user statistics

#### Notifications (`/api/v1/notifications`)
- `GET /` - List user notifications
- `GET /{id}` - Get notification details
- `PATCH /{id}/read` - Mark as read
- `PATCH /read-all` - Mark all as read
- `GET /unread-count` - Get unread count

#### Reports (`/api/v1/reports`)
- `GET /dashboard` - Dashboard metrics
- `GET /tickets/stats` - Ticket statistics
- `GET /sla/compliance` - SLA compliance report
- `GET /engineer/performance` - Engineer performance metrics
- `GET /trends` - Trend analysis
- `GET /export` - Export reports (CSV/Excel)

**Full API Documentation**: See `/backend/API_DOCUMENTATION.md`

---

## Database Architecture

**Reference**: `/design/uml-diagram.md`

### Database: PostgreSQL 14+

### Core Tables

1. **users** - User accounts and authentication
2. **tickets** - Support tickets
3. **comments** - Ticket comments
4. **attachments** - File attachments
5. **ticket_history** - Audit trail
6. **notifications** - Notification records
7. **sla_policies** - SLA policy definitions
8. **escalations** - Escalation tracking
9. **refresh_tokens** - JWT refresh tokens
10. **user_sessions** - Active user sessions

### Relationships

```
User (1:N) Tickets (as requestor)
User (1:N) Tickets (as assignee)
Ticket (1:N) Comments
Ticket (1:N) Attachments
Ticket (1:N) TicketHistory
Ticket (1:N) Notifications
Ticket (1:N) Escalations
User (1:N) Comments
SLAPolicy (1:N) Tickets
```

**Complete Schema Documentation**: See `/backend/DATABASE_SCHEMA.md`

**Migration Scripts**: See `/backend/db_migrations/README.md`

---

## Technology Stack

### Core Framework
- **FastAPI** - Modern, fast web framework for building APIs
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation using Python type hints

### Database & ORM
- **PostgreSQL** - Primary database
- **SQLAlchemy** - ORM and query builder
- **Alembic/Flyway** - Database migrations
- **psycopg2** - PostgreSQL adapter

### Caching & Queue
- **Redis** - Session storage, caching, task queue
- **Celery** - Distributed task queue
- **RabbitMQ** (optional) - Message broker alternative

### Authentication & Security
- **python-jose** - JWT token encoding/decoding
- **passlib** - Password hashing (bcrypt)
- **python-multipart** - Form data and file uploads

### Background Tasks
- **Celery** - Async task processing
- **APScheduler** - Job scheduling (alternative)
- **Celery Beat** - Periodic task scheduler

### Notifications
- **SMTP** (smtplib) - Email sending
- **Twilio** - SMS sending
- **python-slack-sdk** - Slack integration

### Testing
- **pytest** - Testing framework
- **pytest-asyncio** - Async test support
- **pytest-cov** - Code coverage
- **httpx** - Async HTTP client for testing
- **faker** - Test data generation

### Code Quality
- **black** - Code formatter
- **flake8** - Linting
- **pylint** - Static code analysis
- **mypy** - Static type checker
- **isort** - Import sorting

### Monitoring & Logging
- **python-json-logger** - JSON logging
- **prometheus-client** - Metrics export
- **sentry-sdk** - Error tracking

---

## Development Workflow

### Code Style

```bash
# Format code
black .

# Sort imports
isort .

# Lint
flake8 .
pylint backend/

# Type check
mypy .
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=backend --cov-report=html

# Run specific test
pytest tests/unit/test_ticket_service.py -v

# Run integration tests only
pytest tests/integration/ -v
```

### Database Migrations

```bash
# Create new migration (Alembic)
alembic revision --autogenerate -m "Add new field"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1

# View migration history
alembic history
```

---

## Security Best Practices

### Implemented Security Measures

1. **Authentication**
   - JWT with short-lived access tokens
   - Secure refresh token rotation
   - Account lockout after failed attempts

2. **Authorization**
   - Role-based access control (RBAC)
   - Resource-level permissions
   - Principle of least privilege

3. **Data Protection**
   - Password hashing with bcrypt (cost factor 12)
   - SQL injection prevention (ORM)
   - XSS protection (input sanitization)
   - CSRF protection

4. **API Security**
   - Rate limiting (100 requests/minute)
   - CORS configuration
   - Request validation (Pydantic)
   - Security headers (HSTS, CSP, etc.)

5. **Logging & Monitoring**
   - Audit logging for sensitive operations
   - Failed login attempt tracking
   - PII data masking in logs
   - Security event monitoring

---

## Performance Optimization

### Implemented Optimizations

1. **Database**
   - Strategic indexes on frequently queried columns
   - Connection pooling (SQLAlchemy)
   - Query optimization (select specific fields)
   - Database-level caching

2. **Application**
   - Redis caching for frequently accessed data
   - Async operations where possible
   - Background task processing (Celery)
   - Response compression

3. **API**
   - Pagination for list endpoints
   - Field selection (sparse fieldsets)
   - Response caching
   - Rate limiting to prevent abuse

---

## Monitoring & Observability

### Health Checks
```
GET /health       - Basic health check
GET /ready        - Readiness probe
GET /metrics      - Prometheus metrics
```

### Logging Levels
- **DEBUG**: Detailed information for diagnosing problems
- **INFO**: General informational messages
- **WARNING**: Warning messages for potentially harmful situations
- **ERROR**: Error events that might still allow the application to continue
- **CRITICAL**: Critical events that may cause the application to abort

### Metrics Tracked
- Request count and latency
- Error rates by endpoint
- Active database connections
- Cache hit/miss rates
- Background job queue length
- SLA compliance rate

---

## Deployment

### Environment Variables

See `.env.example` for complete list. Key variables:

```bash
# Application
APP_NAME=Ticket Management System
ENVIRONMENT=production
DEBUG=False

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/ticket_db

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_SECRET_KEY=<strong-secret-key-min-32-chars>
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
CORS_ORIGINS=https://app.example.com

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=noreply@example.com
SMTP_PASSWORD=<app-password>
```

### Docker Deployment

```bash
# Build image
docker build -t ticket-backend:latest .

# Run container
docker run -d \
  -p 8000:8000 \
  --env-file .env \
  --name ticket-backend \
  ticket-backend:latest
```

### Production Checklist

- [ ] Set `DEBUG=False`
- [ ] Use strong `JWT_SECRET_KEY` (min 32 chars)
- [ ] Configure proper CORS origins
- [ ] Enable HTTPS/TLS
- [ ] Set up database backups
- [ ] Configure log aggregation (ELK, CloudWatch)
- [ ] Set up monitoring (Prometheus + Grafana)
- [ ] Enable rate limiting
- [ ] Configure firewall rules
- [ ] Set resource limits (CPU, memory)
- [ ] Use environment-specific configs
- [ ] Enable database SSL connections

---

## Troubleshooting

### Common Issues

**Database connection errors**
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Check connection string in .env
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
```

**Redis connection errors**
```bash
# Check Redis is running
redis-cli ping

# Should return PONG
```

**JWT token errors**
```bash
# Ensure JWT_SECRET_KEY is set and at least 32 characters
# Check token expiry times are reasonable
```

**Migration errors**
```bash
# Reset migrations (development only)
alembic downgrade base
alembic upgrade head
```

---

## Contributing

### Development Setup
1. Fork the repository
2. Create feature branch: `git checkout -b feature/my-feature`
3. Make changes and add tests
4. Run tests: `pytest`
5. Format code: `black .` and `isort .`
6. Commit: `git commit -am 'Add my feature'`
7. Push: `git push origin feature/my-feature`
8. Create Pull Request

---

## Additional Documentation

- **Architecture Details**: [ARCHITECTURE.md](./ARCHITECTURE.md)
- **Database Schema**: [DATABASE_SCHEMA.md](./DATABASE_SCHEMA.md)
- **API Reference**: [API_DOCUMENTATION.md](./API_DOCUMENTATION.md)
- **Authentication**: [auth/README.md](./auth/README.md)
- **Database Migrations**: [db_migrations/README.md](./db_migrations/README.md)

---

## Design References

All implementation follows specifications from `/design` folder:

- **System Architecture**: `/design/system-architecture.excalidraw`
- **UML Diagrams**: `/design/uml-diagram.md`
- **State Diagrams**: `/design/state-diagram.md`
- **Flow Diagrams**: `/design/flow-diagram.md`
- **Sequence Diagrams**: `/design/sequence-diagram.md`

---

## License

Copyright © 2025 Ticket Management System. All rights reserved.

---

## Support

For issues, questions, or contributions, please refer to the project repository.
