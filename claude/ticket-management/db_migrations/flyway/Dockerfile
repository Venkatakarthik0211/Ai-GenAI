# Flyway Database Migration Dockerfile
# Uses official Flyway latest image for automated database migrations

FROM flyway/flyway:latest

# Set environment labels
LABEL maintainer="Ticket Management System"
LABEL description="Flyway migration runner for ticket management database"
LABEL version="1.0"

# Set working directory
WORKDIR /flyway

# Copy migration SQL scripts
# These will be mounted from the host in docker-compose
# Directory structure: /flyway/sql/*.sql

# Copy Flyway configuration
COPY flyway.conf /flyway/conf/

# Create necessary directories
USER root
RUN mkdir -p /flyway/sql /flyway/conf /flyway/jars

# Set proper permissions
RUN chmod -R 755 /flyway

# Run as root (Flyway base image doesn't have flyway user)
# USER root is already set above

# Health check - verify Flyway can connect
HEALTHCHECK --interval=30s --timeout=10s --retries=5 \
    CMD flyway info || exit 1

# Default command: run migrations
CMD ["migrate"]
