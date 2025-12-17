# PostgreSQL Database Dockerfile for Ticket Management System
# Uses official PostgreSQL latest image with custom initialization

FROM postgres:latest

# Set environment labels
LABEL maintainer="Ticket Management System"
LABEL description="PostgreSQL database for ticket management with Flyway migrations"
LABEL version="1.0"

# Environment variables (can be overridden in docker-compose)
ENV POSTGRES_DB=ticket_management
ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=postgres
ENV PGDATA=/var/lib/postgresql/data/pgdata

# Install additional PostgreSQL extensions
RUN apt-get update && apt-get install -y \
    postgresql-contrib \
    && rm -rf /var/lib/apt/lists/*

# Create initialization script directory
RUN mkdir -p /docker-entrypoint-initdb.d

# Copy initialization SQL script
COPY init-db.sh /docker-entrypoint-initdb.d/

# Expose PostgreSQL port
EXPOSE 5432

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB} || exit 1

# Volume for persistent data
VOLUME ["/var/lib/postgresql/data"]

# Default command (inherits from base postgres image)
CMD ["postgres"]
