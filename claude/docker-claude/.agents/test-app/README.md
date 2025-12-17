# UserHub

A modern, full-stack user management application built with FastAPI, React, and PostgreSQL.

## Overview

UserHub is a comprehensive user management system that provides authentication, authorization, and CRUD operations for user accounts. It features a RESTful API backend, a responsive React frontend, and a robust PostgreSQL database layer.

## Features

- **User Registration**: Secure user registration with email validation and password strength requirements
- **Authentication**: JWT-based authentication with access and refresh token support
- **Profile Management**: Users can view and update their profile information
- **User CRUD Operations**: Complete create, read, update, and delete functionality for user accounts
- **Soft Deletes**: Users are marked inactive instead of being permanently deleted
- **Pagination**: Efficient pagination for user lists
- **Search & Filter**: Search users by name, email, or username
- **Role-Based Access**: Support for regular users and superuser/admin roles
- **Responsive Design**: Mobile-friendly UI that works on all devices
- **Real-time Validation**: Client-side and server-side validation for all forms

## Tech Stack

### Backend
- **Framework**: FastAPI 0.104+ (Python 3.10+)
- **Database**: PostgreSQL 16 with asyncpg driver
- **ORM**: SQLAlchemy 2.0 (async)
- **Authentication**: JWT tokens with python-jose
- **Password Hashing**: bcrypt via passlib
- **Migrations**: Alembic
- **Validation**: Pydantic v2

### Frontend
- **Framework**: React 18.2+
- **Language**: TypeScript 5.0+
- **Build Tool**: Vite 5.0+
- **Routing**: React Router 6.20+
- **HTTP Client**: Axios 1.6+
- **State Management**: Zustand 4.4+
- **Server State**: TanStack Query (React Query) 5.0+
- **Forms**: React Hook Form 7.48+
- **Validation**: Zod 3.22+
- **Notifications**: React Toastify 9.1+

### Database
- **Database**: PostgreSQL 16
- **Container**: Docker with Docker Compose
- **Admin Tool**: pgAdmin 4

## Architecture

```
userhub/
├── api/                    # FastAPI backend
│   ├── main.py            # Application entry point
│   ├── models.py          # SQLAlchemy database models
│   ├── schemas.py         # Pydantic request/response schemas
│   ├── auth.py            # JWT authentication logic
│   ├── database.py        # Database connection management
│   ├── crud.py            # Database CRUD operations
│   ├── config.py          # Application configuration
│   ├── requirements.txt   # Python dependencies
│   ├── .env.example       # Environment variables template
│   ├── alembic.ini        # Alembic configuration
│   ├── routes/            # API route handlers
│   │   ├── __init__.py
│   │   ├── auth.py        # Authentication endpoints
│   │   └── users.py       # User CRUD endpoints
│   └── alembic/           # Database migrations
│       ├── env.py
│       └── versions/
│           └── 001_initial.py
├── frontend/              # React TypeScript frontend
│   ├── src/
│   │   ├── main.tsx       # Application entry point
│   │   ├── App.tsx        # Root component with routing
│   │   ├── api/           # API client and endpoints
│   │   ├── types/         # TypeScript type definitions
│   │   ├── contexts/      # React contexts (auth)
│   │   ├── components/    # Reusable UI components
│   │   ├── pages/         # Page components
│   │   ├── hooks/         # Custom React hooks
│   │   ├── utils/         # Utility functions
│   │   └── styles/        # Global styles
│   ├── package.json       # Node dependencies
│   ├── tsconfig.json      # TypeScript configuration
│   ├── vite.config.ts     # Vite configuration
│   └── .env.example       # Environment variables template
├── database/              # PostgreSQL setup
│   ├── schema.sql         # Database schema definition
│   ├── seed_data.sql      # Sample data for development
│   ├── docker-compose.yml # Docker configuration
│   ├── .env.example       # Database environment variables
│   ├── migrations/        # SQL migration files
│   └── scripts/           # Database utility scripts
└── README.md              # This file
```

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python**: 3.10 or higher
- **Node.js**: 18.0 or higher
- **PostgreSQL**: 14.0 or higher (or Docker for containerized setup)
- **Docker & Docker Compose**: Latest version (for containerized database)
- **Git**: For version control

## Installation and Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd userhub
```

### 2. Database Setup

#### Option A: Using Docker (Recommended)

```bash
cd database
cp .env.example .env
# Edit .env with your preferred credentials
docker compose up -d
```

This will start:
- PostgreSQL on port 5432
- pgAdmin on port 5050 (http://localhost:5050)

#### Option B: Local PostgreSQL

```bash
cd database
# Create database
createdb userhub
# Run schema
psql -d userhub -f schema.sql
# Seed data (optional)
psql -d userhub -f seed_data.sql
```

### 3. Backend Setup

```bash
cd api

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your database credentials and JWT secret

# Run migrations
alembic upgrade head

# Start the server
uvicorn main:app --reload
```

The API will be available at http://localhost:8000
API documentation: http://localhost:8000/docs

### 4. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Edit .env with your API URL (default: http://localhost:8000)

# Start development server
npm run dev
```

The frontend will be available at http://localhost:5173

## Environment Variables

### Backend (.env)

```env
# Database
DATABASE_URL=postgresql+asyncpg://userhub:userhub123@localhost:5432/userhub

# JWT Configuration
JWT_SECRET_KEY=your-secret-key-here-change-in-production-min-32-chars
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Frontend (.env)

```env
VITE_API_BASE_URL=http://localhost:8000
```

### Database (.env)

```env
POSTGRES_USER=userhub
POSTGRES_PASSWORD=userhub123
POSTGRES_DB=userhub
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

PGADMIN_EMAIL=admin@userhub.com
PGADMIN_PASSWORD=admin
```

## API Endpoints

### Authentication (Public)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register a new user |
| POST | `/api/auth/login` | Login and receive JWT tokens |
| POST | `/api/auth/refresh` | Refresh access token |
| GET | `/api/auth/me` | Get current authenticated user |

### Users (Protected)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/users/` | Get list of users (pagination: ?skip=0&limit=10) |
| POST | `/api/users/` | Create a new user (admin only) |
| GET | `/api/users/{id}` | Get user by ID |
| PUT | `/api/users/{id}` | Update user information |
| DELETE | `/api/users/{id}` | Soft delete user (mark as inactive) |

### Health Check

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | API health check |

## Development Workflow

### Backend Development

```bash
# Run with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Create new migration
alembic revision --autogenerate -m "description"

# Run migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# Run tests (if implemented)
pytest
```

### Frontend Development

```bash
# Start dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint

# Type check
npm run type-check
```

### Database Management

```bash
# Access PostgreSQL CLI
docker exec -it userhub-postgres psql -U userhub -d userhub

# Backup database
./database/scripts/backup_db.sh

# Reset database
./database/scripts/reset_db.sh

# Access pgAdmin
# Open http://localhost:5050
# Login: admin@userhub.com / admin
# Add server with host: postgres, port: 5432
```

## Deployment

### Backend Deployment

1. Set production environment variables
2. Use a production WSGI server (e.g., Gunicorn with Uvicorn workers)
3. Set up HTTPS with a reverse proxy (Nginx/Caddy)
4. Configure proper CORS origins
5. Use a managed PostgreSQL database or secure your own instance

```bash
# Production server example
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Frontend Deployment

1. Build the production bundle: `npm run build`
2. Deploy the `dist/` folder to a static hosting service:
   - Vercel
   - Netlify
   - AWS S3 + CloudFront
   - Nginx
3. Configure environment variables on the hosting platform
4. Set up proper routing (SPA fallback to index.html)

### Database Deployment

1. Use a managed PostgreSQL service (AWS RDS, DigitalOcean, Supabase)
2. Or deploy using Docker on a VPS
3. Set up automated backups
4. Configure proper security groups and firewall rules
5. Use SSL/TLS connections
6. Implement connection pooling (PgBouncer)

## Security Considerations

- **JWT Secret**: Use a strong, random secret key (minimum 32 characters)
- **HTTPS**: Always use HTTPS in production
- **CORS**: Configure CORS to only allow your frontend domain
- **Password Policy**: Enforce strong passwords (8+ chars, uppercase, number, special char)
- **SQL Injection**: All queries are parameterized via SQLAlchemy
- **XSS Protection**: Input validation and output escaping
- **Rate Limiting**: Consider implementing rate limiting in production
- **Environment Variables**: Never commit .env files to version control

## Default Credentials (Development)

When using seed data, the following test accounts are available:

- **Admin User**
  - Email: admin@userhub.com
  - Password: Admin123!

- **Regular User**
  - Email: john.doe@example.com
  - Password: User123!

**IMPORTANT**: Change these credentials before deploying to production!

## Troubleshooting

### Database Connection Issues

```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# View PostgreSQL logs
docker logs userhub-postgres

# Test connection
psql -h localhost -U userhub -d userhub
```

### Backend Issues

```bash
# Check Python version
python --version  # Should be 3.10+

# Verify dependencies
pip list

# View application logs
# Uvicorn outputs logs to stdout
```

### Frontend Issues

```bash
# Check Node version
node --version  # Should be 18+

# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install

# Check for build errors
npm run build
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin feature/your-feature`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues, questions, or contributions, please open an issue on the GitHub repository.

## Acknowledgments

- FastAPI for the excellent web framework
- React team for the powerful UI library
- PostgreSQL for the robust database system
- All open-source contributors who made this project possible
