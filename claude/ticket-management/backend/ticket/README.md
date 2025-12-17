# Ticket Management Service

Complete ticket management service for DevOps support system with full CRUD operations, comments, attachments, and audit history.

## Overview

The Ticket Management Service provides comprehensive ticket handling capabilities including:

- **Ticket CRUD Operations**: Create, read, update, delete tickets
- **Status Workflow**: NEW → OPEN → IN_PROGRESS → RESOLVED → CLOSED
- **Assignment Management**: Assign tickets to engineers and teams
- **Comments System**: Public and internal comments with attachments
- **File Attachments**: Upload and manage ticket attachments (up to 50MB)
- **Audit History**: Complete change tracking for compliance
- **SLA Tracking**: Automatic calculation of response and resolution due dates
- **Search & Filtering**: Full-text search and advanced filtering

## Project Structure

```
backend/ticket/
├── main.py              # FastAPI application entry point
├── config.py            # Service configuration
├── models.py            # SQLAlchemy ORM models (already created)
├── schemas.py           # Pydantic request/response schemas
├── routes.py            # API endpoint handlers
├── dependencies.py      # FastAPI dependencies
├── utils.py             # Helper functions
├── requirements.txt     # Python dependencies
├── Dockerfile          # Container definition
└── README.md           # This file
```

## API Endpoints

### Tickets

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/v1/tickets` | List tickets with filtering | Yes |
| POST | `/api/v1/tickets` | Create new ticket | Yes |
| GET | `/api/v1/tickets/{id}` | Get ticket details | Yes |
| PUT | `/api/v1/tickets/{id}` | Update ticket (full) | Yes |
| PATCH | `/api/v1/tickets/{id}` | Update ticket (partial) | Yes |
| DELETE | `/api/v1/tickets/{id}` | Delete ticket (admin only) | Admin |

### Ticket Actions

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| PUT | `/api/v1/tickets/{id}/assign` | Assign ticket to engineer | Engineer+ |
| PATCH | `/api/v1/tickets/{id}/status` | Update ticket status | Yes |
| POST | `/api/v1/tickets/{id}/resolve` | Mark ticket as resolved | Engineer+ |
| POST | `/api/v1/tickets/{id}/close` | Close ticket | Engineer+ |
| POST | `/api/v1/tickets/{id}/reopen` | Reopen closed ticket | Yes |
| GET | `/api/v1/tickets/{id}/history` | Get ticket history | Yes |

### Comments

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/v1/tickets/{id}/comments` | List ticket comments | Yes |
| POST | `/api/v1/tickets/{id}/comments` | Add comment to ticket | Yes |
| PUT | `/api/v1/comments/{id}` | Update comment | Author |
| DELETE | `/api/v1/comments/{id}` | Delete comment | Author/Admin |

### Attachments

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/v1/tickets/{id}/attachments` | List attachments | Yes |
| POST | `/api/v1/tickets/{id}/attachments` | Upload attachment | Yes |
| GET | `/api/v1/attachments/{id}` | Download attachment | Yes |
| DELETE | `/api/v1/attachments/{id}` | Delete attachment | Uploader/Admin |

## Setup Instructions

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Auth Service running on port 8001

### Local Development

1. **Create virtual environment**:
   ```bash
   cd backend/ticket
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment variables**:
   ```bash
   export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/ticket_management"
   export JWT_SECRET_KEY="your-secret-key-change-this-in-production-min-32-characters"
   export DEBUG="true"
   export ENVIRONMENT="development"
   ```

4. **Run database migrations** (if using Flyway):
   ```bash
   # Run from project root
   flyway migrate
   ```

5. **Start the service**:
   ```bash
   python main.py
   # Or using uvicorn directly:
   uvicorn main:app --reload --port 8002
   ```

6. **Access API documentation**:
   - Swagger UI: http://localhost:8002/docs
   - ReDoc: http://localhost:8002/redoc
   - Health check: http://localhost:8002/health

### Docker Deployment

1. **Build Docker image**:
   ```bash
   docker build -t ticket-service:latest .
   ```

2. **Run container**:
   ```bash
   docker run -d \
     --name ticket-service \
     -p 8002:8002 \
     -e DATABASE_URL="postgresql://postgres:postgres@db:5432/ticket_management" \
     -e JWT_SECRET_KEY="your-secret-key" \
     -e ENVIRONMENT="production" \
     -v /data/attachments:/tmp/ticket-attachments \
     ticket-service:latest
   ```

3. **Using Docker Compose** (recommended):
   ```yaml
   version: '3.8'
   services:
     ticket-service:
       build: ./backend/ticket
       ports:
         - "8002:8002"
       environment:
         - DATABASE_URL=postgresql://postgres:postgres@db:5432/ticket_management
         - JWT_SECRET_KEY=${JWT_SECRET_KEY}
         - AUTH_SERVICE_URL=http://auth-service:8001
       volumes:
         - attachments_data:/tmp/ticket-attachments
       depends_on:
         - db
         - auth-service

   volumes:
     attachments_data:
   ```

## Environment Variables

### Required

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host:5432/dbname` |
| `JWT_SECRET_KEY` | Secret key for JWT validation | Min 32 characters |

### Optional

| Variable | Default | Description |
|----------|---------|-------------|
| `AUTH_SERVICE_URL` | `http://localhost:8001` | Auth service URL |
| `ENVIRONMENT` | `development` | Environment (development/production) |
| `DEBUG` | `false` | Enable debug mode |
| `SERVICE_PORT` | `8002` | Service port |
| `UPLOAD_STORAGE_PATH` | `/tmp/ticket-attachments` | File upload directory |
| `UPLOAD_MAX_FILE_SIZE` | `52428800` | Max file size (50MB) |
| `TICKET_REOPEN_WINDOW_DAYS` | `7` | Days after closure ticket can be reopened |
| `SLA_ENABLED` | `true` | Enable SLA tracking |
| `NOTIFICATIONS_ENABLED` | `true` | Enable notifications |

## Usage Examples

### Creating a Ticket

```bash
curl -X POST "http://localhost:8002/api/v1/tickets" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Production database is down",
    "description": "The production PostgreSQL database is not responding. All services are affected. Started at 14:30 UTC.",
    "category": "INCIDENT",
    "priority": "P1",
    "environment": "PRODUCTION",
    "affected_service": "PostgreSQL Database",
    "impact_level": "CRITICAL",
    "tags": ["database", "production", "outage"]
  }'
```

### Listing Tickets with Filters

```bash
curl -X GET "http://localhost:8002/api/v1/tickets?status=OPEN&status=IN_PROGRESS&priority=P1&priority=P2&sort_by=priority&order=asc" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Adding a Comment

```bash
curl -X POST "http://localhost:8002/api/v1/tickets/{ticket_id}/comments" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Investigating the issue. Database server shows high CPU usage.",
    "comment_type": "COMMENT",
    "is_internal": false
  }'
```

### Uploading an Attachment

```bash
curl -X POST "http://localhost:8002/api/v1/tickets/{ticket_id}/attachments" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "file=@/path/to/error.log"
```

### Assigning a Ticket

```bash
curl -X PUT "http://localhost:8002/api/v1/tickets/{ticket_id}/assign" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "assignee_id": "550e8400-e29b-41d4-a716-446655440000",
    "notes": "John has expertise in database issues"
  }'
```

### Resolving a Ticket

```bash
curl -X POST "http://localhost:8002/api/v1/tickets/{ticket_id}/resolve" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "resolution_notes": "Issue resolved by restarting the database service and clearing connection pool. Root cause was memory leak in connection handler. Applied patch v2.3.1."
  }'
```

## Ticket Status Workflow

```
NEW (created)
  ↓
OPEN (assigned/acknowledged)
  ↓
IN_PROGRESS (work started)
  ↓ ↔ PENDING_INFO (waiting for information)
  ↓
RESOLVED (solution provided)
  ↓
CLOSED (verified and closed)
  ↓
REOPENED (if issue returns) → back to OPEN
```

### Valid Status Transitions

- **NEW** → OPEN, IN_PROGRESS, CLOSED
- **OPEN** → IN_PROGRESS, PENDING_INFO, RESOLVED, CLOSED
- **IN_PROGRESS** → PENDING_INFO, RESOLVED, ESCALATED, OPEN
- **PENDING_INFO** → IN_PROGRESS, OPEN, CLOSED
- **RESOLVED** → CLOSED, REOPENED
- **CLOSED** → REOPENED
- **REOPENED** → OPEN, IN_PROGRESS, RESOLVED
- **ESCALATED** → IN_PROGRESS, RESOLVED, CLOSED

## Ticket Priority Levels

| Priority | Name | Response SLA | Resolution SLA | Use Case |
|----------|------|--------------|----------------|----------|
| **P1** | Critical | 1 hour | 4 hours | Production outage, critical system down |
| **P2** | High | 4 hours | 24 hours | Major feature broken, significant impact |
| **P3** | Medium | 8 hours | 72 hours | Minor bug, workaround available |
| **P4** | Low | 24 hours | 168 hours | Enhancement request, cosmetic issue |

## Permission Model

### End User
- Create tickets
- View own tickets
- Comment on own tickets
- Upload attachments to own tickets

### DevOps Engineer
- All End User permissions
- View all tickets
- Edit assigned tickets
- Assign tickets to self
- Create internal comments
- Resolve and close tickets

### Team Lead
- All DevOps Engineer permissions
- Assign tickets to team members
- Edit team tickets
- View team metrics

### Manager
- All Team Lead permissions
- View all teams
- Reassign any ticket
- Edit any ticket

### Admin
- All permissions
- Delete tickets
- Delete comments
- Manage users
- System configuration

## SLA Tracking

### Automatic Calculation

When a ticket is created, the system automatically calculates:

1. **Response Due Date**: Based on priority (e.g., P1 = 1 hour)
2. **Resolution Due Date**: Based on priority (e.g., P1 = 4 hours)

### SLA Breach Handling

- System tracks if response/resolution exceeds SLA
- Creates history entry for SLA breach
- Can trigger notifications (if configured)
- Visible in ticket details and reports

## File Attachments

### Supported File Types

- Documents: PDF, DOC, DOCX, TXT
- Images: PNG, JPG, JPEG, GIF
- Spreadsheets: XLS, XLSX, CSV
- Archives: ZIP
- Logs: LOG, JSON, XML

### Upload Limits

- **Maximum file size**: 50MB per file
- **Storage**: Local filesystem (configurable for S3/Azure Blob)
- **Security**: File hash calculated for integrity
- **Virus scanning**: Optional (configure VIRUS_SCAN_ENABLED)

## Audit History

Every change to a ticket is automatically logged with:

- Change type (status change, assignment, update, etc.)
- Field name and old/new values
- User who made the change
- Timestamp
- Additional metadata (JSON)

### History Entry Types

- `CREATED` - Ticket created
- `STATUS_CHANGE` - Status updated
- `PRIORITY_CHANGE` - Priority updated
- `ASSIGNMENT_CHANGE` - Assignee changed
- `UPDATE` - General ticket update
- `COMMENT_ADDED` - Comment added
- `ATTACHMENT_ADDED` - File uploaded
- `RESOLVED` - Ticket resolved
- `CLOSED` - Ticket closed
- `REOPENED` - Ticket reopened
- `ESCALATED` - Ticket escalated
- `SLA_BREACH` - SLA deadline missed

## Error Handling

The service returns standard HTTP status codes:

- `200 OK` - Successful request
- `201 Created` - Resource created successfully
- `204 No Content` - Successful deletion
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Missing or invalid authentication
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

Error responses include:
```json
{
  "detail": "Error description",
  "error_code": "OPTIONAL_ERROR_CODE"
}
```

## Logging

The service logs:

- All HTTP requests and responses
- Ticket operations (create, update, delete)
- Status changes
- Assignment changes
- File uploads
- Errors and exceptions

Log levels:
- `DEBUG` - Detailed debugging information
- `INFO` - General information (default)
- `WARNING` - Warning messages
- `ERROR` - Error messages
- `CRITICAL` - Critical failures

## Testing

### Manual Testing with Postman

Import the Postman collection from `/backend/ticket/Ticket_Management_API.postman_collection.json` (if available).

### Health Check

```bash
curl http://localhost:8002/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "ticket-service",
  "version": "1.0.0",
  "environment": "development"
}
```

## Troubleshooting

### Database Connection Issues

**Problem**: Service can't connect to database

**Solution**:
```bash
# Check DATABASE_URL is correct
echo $DATABASE_URL

# Test PostgreSQL connection
psql $DATABASE_URL

# Verify database exists
psql -U postgres -c "\l"

# Check migrations have run
psql $DATABASE_URL -c "SELECT * FROM information_schema.tables WHERE table_name = 'tickets';"
```

### JWT Validation Errors

**Problem**: 401 Unauthorized errors

**Solution**:
- Ensure JWT_SECRET_KEY matches auth service
- Verify token is not expired
- Check token format: `Bearer <token>`

### File Upload Failures

**Problem**: Attachments fail to upload

**Solution**:
```bash
# Check upload directory exists and is writable
ls -la /tmp/ticket-attachments
mkdir -p /tmp/ticket-attachments
chmod 755 /tmp/ticket-attachments

# Check file size limit
# Maximum: 50MB (52428800 bytes)

# Verify allowed file extensions in config
```

### Performance Issues

**Problem**: Slow API responses

**Solution**:
- Check database indexes are created
- Review slow query logs
- Enable connection pooling
- Consider caching for read-heavy endpoints

## Integration with Auth Service

The Ticket Service integrates with the Auth Service for:

1. **JWT Token Validation**: All requests require valid JWT from auth service
2. **User Information**: Extracts user ID and role from JWT payload
3. **Permission Checks**: Role-based access control

### JWT Token Structure

```json
{
  "sub": "user_id",
  "username": "john.doe",
  "email": "john@example.com",
  "role": "DEVOPS_ENGINEER",
  "type": "access",
  "exp": 1234567890,
  "iat": 1234567890,
  "jti": "unique_token_id"
}
```

## Production Deployment Checklist

- [ ] Set strong JWT_SECRET_KEY (min 32 characters)
- [ ] Use production database with backups
- [ ] Configure file storage (S3/Azure Blob recommended)
- [ ] Enable HTTPS/TLS
- [ ] Set up monitoring and alerting
- [ ] Configure log aggregation
- [ ] Enable virus scanning for uploads
- [ ] Set rate limiting
- [ ] Configure backup strategy
- [ ] Set up database connection pooling
- [ ] Review and adjust SLA settings
- [ ] Configure notification service integration
- [ ] Set ENVIRONMENT=production
- [ ] Set DEBUG=false
- [ ] Disable API documentation in production

## Support

For issues, questions, or contributions:

- Create an issue in the project repository
- Contact the DevOps team
- Check the main project README at `/README.md`

## License

Internal use only - Ticket Management System
