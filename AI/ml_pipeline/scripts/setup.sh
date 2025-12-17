#!/bin/bash

###############################################################################
# ML Pipeline Setup Script
###############################################################################
# This script initializes the ML Pipeline environment with all required services:
# - PostgreSQL (prompt storage + MLflow backend)
# - MinIO (S3-compatible storage for prompts/artifacts)
# - MLflow Tracking Server
# - FastAPI Backend
# - Streamlit Frontend
###############################################################################

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

###############################################################################
# Helper Functions
###############################################################################

print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

check_command() {
    if command -v "$1" &> /dev/null; then
        print_success "$1 is installed"
        return 0
    else
        print_error "$1 is not installed"
        return 1
    fi
}

###############################################################################
# Prerequisites Check
###############################################################################

check_prerequisites() {
    print_header "Checking Prerequisites"

    local all_ok=true

    # Check Docker
    if check_command "docker"; then
        docker_version=$(docker --version)
        print_info "Version: $docker_version"
    else
        all_ok=false
        print_error "Please install Docker: https://docs.docker.com/get-docker/"
    fi

    # Check Docker Compose
    if docker compose version &> /dev/null; then
        print_success "docker compose is available"
        compose_version=$(docker compose version)
        print_info "Version: $compose_version"
    elif check_command "docker-compose"; then
        print_warning "Using legacy docker-compose command"
        compose_version=$(docker-compose --version)
        print_info "Version: $compose_version"
    else
        all_ok=false
        print_error "Please install Docker Compose"
    fi

    # Check if Docker daemon is running
    if docker info &> /dev/null; then
        print_success "Docker daemon is running"
    else
        all_ok=false
        print_error "Docker daemon is not running. Please start Docker."
    fi

    if [ "$all_ok" = false ]; then
        print_error "Prerequisites check failed. Please install missing dependencies."
        exit 1
    fi

    print_success "All prerequisites met!"
}

###############################################################################
# Environment Setup
###############################################################################

setup_environment() {
    print_header "Setting Up Environment"

    cd "$PROJECT_ROOT"

    # Check if .env exists
    if [ -f ".env" ]; then
        print_warning ".env file already exists"
        read -p "Do you want to overwrite it? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_info "Keeping existing .env file"
            return 0
        fi
    fi

    # Check if .env.template exists
    if [ ! -f ".env.template" ]; then
        print_error ".env.template not found!"
        exit 1
    fi

    # Copy template
    print_info "Creating .env from .env.template"
    cp .env.template .env
    print_success ".env file created"

    print_warning "IMPORTANT: Edit .env file with your credentials before continuing!"
    print_info "Required changes:"
    echo "  1. Update PostgreSQL password (POSTGRES_PASSWORD)"
    echo "  2. Update MinIO credentials (MINIO_ROOT_USER, MINIO_ROOT_PASSWORD)"
    echo "  3. Add AWS credentials (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)"
    echo "  4. Review and adjust other settings as needed"
    echo ""

    read -p "Have you configured the .env file? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_warning "Please edit .env file and run this script again"
        exit 0
    fi

    print_success "Environment configuration complete"
}

###############################################################################
# Docker Setup
###############################################################################

setup_docker() {
    print_header "Setting Up Docker Environment"

    cd "$PROJECT_ROOT"

    # Create necessary directories
    print_info "Creating necessary directories..."
    mkdir -p data/raw data/processed data/external
    mkdir -p outputs/models outputs/metrics outputs/plots outputs/reports outputs/logs
    mkdir -p mlruns mlartifacts
    print_success "Directories created"

    # Stop any existing containers
    print_info "Stopping existing containers (if any)..."
    docker compose down 2>/dev/null || docker-compose down 2>/dev/null || true
    print_success "Existing containers stopped"

    # Build images
    print_info "Building Docker images..."
    if docker compose version &> /dev/null; then
        docker compose build --no-cache
    else
        docker-compose build --no-cache
    fi
    print_success "Docker images built"
}

###############################################################################
# Service Startup
###############################################################################

start_services() {
    print_header "Starting Services"

    cd "$PROJECT_ROOT"

    print_info "Starting all services in detached mode..."
    if docker compose version &> /dev/null; then
        docker compose up -d
    else
        docker-compose up -d
    fi

    print_success "Services started"

    # Wait for services to be healthy
    print_info "Waiting for services to become healthy (this may take 2-3 minutes)..."
    echo ""

    local max_wait=180  # 3 minutes
    local elapsed=0
    local interval=5

    while [ $elapsed -lt $max_wait ]; do
        # Check service health
        local postgres_healthy=false
        local minio_healthy=false
        local mlflow_healthy=false
        local backend_healthy=false
        local frontend_healthy=false

        if docker compose version &> /dev/null; then
            postgres_status=$(docker compose ps postgres --format json 2>/dev/null | grep -o '"Health":"[^"]*"' | cut -d'"' -f4 || echo "starting")
            minio_status=$(docker compose ps minio --format json 2>/dev/null | grep -o '"Health":"[^"]*"' | cut -d'"' -f4 || echo "starting")
            mlflow_status=$(docker compose ps mlflow --format json 2>/dev/null | grep -o '"Health":"[^"]*"' | cut -d'"' -f4 || echo "starting")
            backend_status=$(docker compose ps backend --format json 2>/dev/null | grep -o '"Health":"[^"]*"' | cut -d'"' -f4 || echo "starting")
            frontend_status=$(docker compose ps frontend --format json 2>/dev/null | grep -o '"Health":"[^"]*"' | cut -d'"' -f4 || echo "starting")
        else
            postgres_status=$(docker inspect --format='{{.State.Health.Status}}' ml-pipeline-postgres 2>/dev/null || echo "starting")
            minio_status=$(docker inspect --format='{{.State.Health.Status}}' ml-pipeline-minio 2>/dev/null || echo "starting")
            mlflow_status=$(docker inspect --format='{{.State.Health.Status}}' mlflow-server 2>/dev/null || echo "starting")
            backend_status=$(docker inspect --format='{{.State.Health.Status}}' ml-pipeline-backend 2>/dev/null || echo "starting")
            frontend_status=$(docker inspect --format='{{.State.Health.Status}}' ml-pipeline-frontend 2>/dev/null || echo "starting")
        fi

        # Display status
        echo -ne "\r  PostgreSQL: $postgres_status | MinIO: $minio_status | MLflow: $mlflow_status | Backend: $backend_status | Frontend: $frontend_status  "

        # Check if all healthy
        if [ "$postgres_status" = "healthy" ] && \
           [ "$minio_status" = "healthy" ] && \
           [ "$mlflow_status" = "healthy" ] && \
           [ "$backend_status" = "healthy" ] && \
           [ "$frontend_status" = "healthy" ]; then
            echo ""
            print_success "All services are healthy!"
            return 0
        fi

        sleep $interval
        elapsed=$((elapsed + interval))
    done

    echo ""
    print_error "Timeout waiting for services to become healthy"
    print_info "Check logs with: docker compose logs"
    exit 1
}

###############################################################################
# Database Initialization
###############################################################################

initialize_database() {
    print_header "Initializing Database"

    cd "$PROJECT_ROOT"

    print_info "Checking PostgreSQL schema..."

    # PostgreSQL automatically runs scripts in /docker-entrypoint-initdb.d on first start
    # Check if database was initialized
    if docker compose version &> /dev/null; then
        db_status=$(docker compose exec -T postgres psql -U ml_pipeline_user -d ml_pipeline -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public';" 2>/dev/null || echo "0")
    else
        db_status=$(docker-compose exec -T postgres psql -U ml_pipeline_user -d ml_pipeline -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public';" 2>/dev/null || echo "0")
    fi

    if [[ $db_status =~ [0-9]+ ]] && [ "$db_status" -gt 0 ]; then
        print_success "Database schema initialized"
    else
        print_warning "Database schema may not be initialized properly"
        print_info "Check logs: docker compose logs postgres"
    fi
}

###############################################################################
# MinIO Bucket Verification
###############################################################################

verify_minio_buckets() {
    print_header "Verifying MinIO Buckets"

    cd "$PROJECT_ROOT"

    print_info "Checking MinIO buckets..."

    # The minio-setup container should have created the buckets
    sleep 5  # Give it a moment to complete

    if docker compose version &> /dev/null; then
        bucket_list=$(docker compose exec -T minio mc ls minio/ 2>/dev/null || echo "")
    else
        bucket_list=$(docker-compose exec -T minio mc ls minio/ 2>/dev/null || echo "")
    fi

    if echo "$bucket_list" | grep -q "ml-pipeline-prompts"; then
        print_success "Bucket 'ml-pipeline-prompts' exists"
    else
        print_warning "Bucket 'ml-pipeline-prompts' may not exist"
    fi

    if echo "$bucket_list" | grep -q "mlflow-artifacts"; then
        print_success "Bucket 'mlflow-artifacts' exists"
    else
        print_warning "Bucket 'mlflow-artifacts' may not exist"
    fi
}

###############################################################################
# Health Check
###############################################################################

run_health_checks() {
    print_header "Running Health Checks"

    # Check PostgreSQL
    print_info "Checking PostgreSQL..."
    if docker compose version &> /dev/null; then
        if docker compose exec -T postgres pg_isready -U ml_pipeline_user &>/dev/null; then
            print_success "PostgreSQL is ready"
        else
            print_error "PostgreSQL is not responding"
        fi
    else
        if docker-compose exec -T postgres pg_isready -U ml_pipeline_user &>/dev/null; then
            print_success "PostgreSQL is ready"
        else
            print_error "PostgreSQL is not responding"
        fi
    fi

    # Check MinIO
    print_info "Checking MinIO..."
    if curl -sf http://localhost:9000/minio/health/live &>/dev/null; then
        print_success "MinIO is healthy"
    else
        print_error "MinIO is not responding"
    fi

    # Check MLflow
    print_info "Checking MLflow..."
    if curl -sf http://localhost:5000/health &>/dev/null; then
        print_success "MLflow is healthy"
    else
        print_warning "MLflow health check returned non-success (may still be starting)"
    fi

    # Check Backend API
    print_info "Checking Backend API..."
    if curl -sf http://localhost:8000/health &>/dev/null; then
        print_success "Backend API is healthy"
    else
        print_error "Backend API is not responding"
    fi

    # Check Frontend
    print_info "Checking Streamlit Frontend..."
    if curl -sf http://localhost:8501/_stcore/health &>/dev/null; then
        print_success "Frontend is healthy"
    else
        print_warning "Frontend health check returned non-success (may still be starting)"
    fi
}

###############################################################################
# Display Access Information
###############################################################################

display_access_info() {
    print_header "Setup Complete!"

    echo -e "${GREEN}All services are running. Access URLs:${NC}\n"
    echo -e "  ${BLUE}Streamlit Frontend:${NC}    http://localhost:8501"
    echo -e "  ${BLUE}FastAPI Backend:${NC}       http://localhost:8000"
    echo -e "  ${BLUE}API Documentation:${NC}     http://localhost:8000/docs"
    echo -e "  ${BLUE}MLflow UI:${NC}             http://localhost:5000"
    echo -e "  ${BLUE}MinIO Console:${NC}         http://localhost:9001"
    echo -e "  ${BLUE}PostgreSQL:${NC}            localhost:5432"
    echo ""

    print_info "Useful Commands:"
    echo "  View logs:           docker compose logs -f"
    echo "  Stop services:       docker compose down"
    echo "  Restart services:    docker compose restart"
    echo "  View service status: docker compose ps"
    echo ""

    print_info "Next Steps:"
    echo "  1. Open Streamlit UI: http://localhost:8501"
    echo "  2. Try natural language configuration (e.g., 'Classify iris dataset with high accuracy')"
    echo "  3. Monitor experiments in MLflow UI: http://localhost:5000"
    echo "  4. Check API documentation: http://localhost:8000/docs"
    echo ""

    print_warning "To stop all services, run: docker compose down"
}

###############################################################################
# Main Execution
###############################################################################

main() {
    print_header "ML Pipeline Setup"
    print_info "This script will set up the complete ML Pipeline environment"
    echo ""

    # Run setup steps
    check_prerequisites
    setup_environment
    setup_docker
    start_services
    initialize_database
    verify_minio_buckets
    run_health_checks
    display_access_info

    print_success "Setup completed successfully!"
}

# Run main function
main "$@"
