# Multi-stage Dockerfile for React + TypeScript + Vite Application
# Stage 1: Build the application
# Stage 2: Serve with Nginx

# ============================================
# Stage 1: Build Stage
# ============================================
FROM node:20-alpine AS builder

# Set working directory
WORKDIR /app

# Add metadata labels
LABEL maintainer="Ticket Management System"
LABEL description="Frontend application for Ticket Management System"
LABEL version="1.0.0"

# Install build dependencies
RUN apk add --no-cache \
    git \
    python3 \
    make \
    g++

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install --prefer-offline --no-audit --progress=false

# Copy application source code
COPY . .

# Build arguments for environment configuration
ARG VITE_API_BASE_URL=http://localhost:8001/api/v1
ARG VITE_APP_NAME="Ticket Management System"
ARG NODE_ENV=production

# Set environment variables for build
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}
ENV VITE_APP_NAME=${VITE_APP_NAME}
ENV NODE_ENV=${NODE_ENV}

# Build the application
RUN npm run build

# Remove development dependencies to reduce image size
RUN npm prune --production

# ============================================
# Stage 2: Production Stage with Nginx
# ============================================
FROM nginx:1.25-alpine AS production

# Add metadata labels
LABEL maintainer="Ticket Management System"
LABEL description="Production-ready frontend with Nginx"
LABEL version="1.0.0"

# Install runtime dependencies
RUN apk add --no-cache \
    curl \
    tzdata \
    ca-certificates

# Set timezone
ENV TZ=UTC
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Remove default nginx configuration
RUN rm -rf /etc/nginx/conf.d/*

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Copy built application from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Create necessary directories with proper permissions
RUN mkdir -p /var/cache/nginx/client_temp \
    && mkdir -p /var/log/nginx \
    && mkdir -p /tmp \
    && chmod -R 755 /var/cache/nginx \
    && chmod -R 755 /var/log/nginx \
    && chmod -R 755 /usr/share/nginx/html \
    && chmod 777 /tmp

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost/health || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
