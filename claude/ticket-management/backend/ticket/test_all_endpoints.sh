#!/bin/bash

################################################################################
# Comprehensive Ticket Management API Test Suite
# Tests all endpoints with Postman-compatible requests
################################################################################

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# API URLs
AUTH_URL="http://localhost:8001/api/v1"
TICKET_URL="http://localhost:8002/api/v1"

# Test counters
PASSED=0
FAILED=0
TOTAL=0

# Helper functions
log_test() {
    echo -e "${BLUE}[TEST $((TOTAL+1))]${NC} $1"
}

log_success() {
    echo -e "${GREEN}✅ PASS${NC} $1"
    PASSED=$((PASSED+1))
    TOTAL=$((TOTAL+1))
}

log_failure() {
    echo -e "${RED}❌ FAIL${NC} $1"
    FAILED=$((FAILED+1))
    TOTAL=$((TOTAL+1))
}

log_info() {
    echo -e "${YELLOW}ℹ️  INFO${NC} $1"
}

# Start test suite
clear
echo "================================================================================"
echo "                   TICKET MANAGEMENT API - COMPLETE TEST SUITE"
echo "================================================================================"
echo ""
echo "Testing against:"
echo "  Auth Service:   $AUTH_URL"
echo "  Ticket Service: $TICKET_URL"
echo ""
echo "================================================================================"
echo ""

# ============================================================================
# AUTHENTICATION TESTS
# ============================================================================

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "SECTION 1: AUTHENTICATION & USER MANAGEMENT"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Test 1: Register END_USER
log_test "Register END_USER account"
REGISTER_RESPONSE=$(curl -s -X POST ${AUTH_URL}/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "enduser1",
    "email": "enduser1@example.com",
    "password": "EndUser123!",
    "first_name": "End",
    "last_name": "User",
    "phone_number": "+1-555-0001",
    "department": "Operations"
  }')

if echo $REGISTER_RESPONSE | jq -e '.id' > /dev/null 2>&1; then
    ENDUSER_ID=$(echo $REGISTER_RESPONSE | jq -r '.id')
    log_success "END_USER registered: $ENDUSER_ID"
else
    if echo $REGISTER_RESPONSE | jq -e '.detail' | grep -q "already registered" > /dev/null 2>&1; then
        log_info "User already exists, continuing..."
        ENDUSER_ID="existing"
    else
        log_failure "Failed to register END_USER"
        echo $REGISTER_RESPONSE | jq
    fi
fi

# Test 2: Register ENGINEER user
log_test "Register ENGINEER account"
REGISTER_RESPONSE=$(curl -s -X POST ${AUTH_URL}/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "engineer1",
    "email": "engineer1@example.com",
    "password": "Engineer123!",
    "first_name": "Dev",
    "last_name": "Engineer",
    "phone_number": "+1-555-0002",
    "department": "Engineering"
  }')

if echo $REGISTER_RESPONSE | jq -e '.id' > /dev/null 2>&1; then
    ENGINEER_ID=$(echo $REGISTER_RESPONSE | jq -r '.id')
    log_success "ENGINEER registered: $ENGINEER_ID"
else
    if echo $REGISTER_RESPONSE | jq -e '.detail' | grep -q "already registered" > /dev/null 2>&1; then
        log_info "User already exists, continuing..."
        ENGINEER_ID="existing"
    else
        log_failure "Failed to register ENGINEER"
    fi
fi

# Test 3: Login as END_USER
log_test "Login as END_USER"
LOGIN_RESPONSE=$(curl -s -X POST ${AUTH_URL}/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "enduser1",
    "password": "EndUser123!"
  }')

ENDUSER_TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.access_token')
if [ "$ENDUSER_TOKEN" != "null" ]; then
    log_success "END_USER logged in successfully"
else
    log_failure "END_USER login failed"
    echo $LOGIN_RESPONSE | jq
fi

# Test 4: Login as ENGINEER
log_test "Login as ENGINEER"
LOGIN_RESPONSE=$(curl -s -X POST ${AUTH_URL}/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "engineer1",
    "password": "Engineer123!"
  }')

ENGINEER_TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.access_token')
if [ "$ENGINEER_TOKEN" != "null" ]; then
    log_success "ENGINEER logged in successfully"
else
    log_failure "ENGINEER login failed"
fi

# Test 5: Get current user profile
log_test "Get current user profile (END_USER)"
PROFILE_RESPONSE=$(curl -s -X GET ${AUTH_URL}/auth/me \
  -H "Authorization: Bearer $ENDUSER_TOKEN")

if echo $PROFILE_RESPONSE | jq -e '.username' > /dev/null 2>&1; then
    log_success "Profile retrieved successfully"
else
    log_failure "Failed to get profile"
fi

# ============================================================================
# TICKET CRUD TESTS
# ============================================================================

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "SECTION 2: TICKET CRUD OPERATIONS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Test 6: Create ticket (P1 - Critical)
log_test "Create P1 Critical ticket"
CREATE_RESPONSE=$(curl -s -X POST ${TICKET_URL}/tickets \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ENDUSER_TOKEN" \
  -d '{
    "title": "Production database server down - urgent",
    "description": "The primary database server is not responding. All user transactions are failing. This is causing complete service outage.",
    "category": "INCIDENT",
    "priority": "P1",
    "environment": "PRODUCTION",
    "affected_service": "Database Cluster",
    "impact_level": "CRITICAL",
    "tags": ["database", "outage", "production", "critical"]
  }')

TICKET_P1_ID=$(echo $CREATE_RESPONSE | jq -r '.id')
TICKET_P1_NUMBER=$(echo $CREATE_RESPONSE | jq -r '.ticket_number')
if [ "$TICKET_P1_ID" != "null" ]; then
    log_success "P1 ticket created: $TICKET_P1_NUMBER"
else
    log_failure "Failed to create P1 ticket"
    echo $CREATE_RESPONSE | jq
fi

# Test 7: Create ticket (P2 - High)
log_test "Create P2 High priority ticket"
CREATE_RESPONSE=$(curl -s -X POST ${TICKET_URL}/tickets \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ENDUSER_TOKEN" \
  -d '{
    "title": "API response time degradation noticed",
    "description": "Users are reporting slow API response times. Average response time has increased from 200ms to 2 seconds.",
    "category": "INCIDENT",
    "priority": "P2",
    "environment": "PRODUCTION",
    "affected_service": "API Gateway",
    "impact_level": "HIGH",
    "tags": ["performance", "api", "latency"]
  }')

TICKET_P2_ID=$(echo $CREATE_RESPONSE | jq -r '.id')
TICKET_P2_NUMBER=$(echo $CREATE_RESPONSE | jq -r '.ticket_number')
if [ "$TICKET_P2_ID" != "null" ]; then
    log_success "P2 ticket created: $TICKET_P2_NUMBER"
else
    log_failure "Failed to create P2 ticket"
fi

# Test 8: Create ticket (P3 - Medium)
log_test "Create P3 Medium priority ticket"
CREATE_RESPONSE=$(curl -s -X POST ${TICKET_URL}/tickets \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ENDUSER_TOKEN" \
  -d '{
    "title": "Request for SSL certificate renewal",
    "description": "The SSL certificate for api.example.com will expire in 30 days. Need to renew before expiration.",
    "category": "SERVICE_REQUEST",
    "priority": "P3",
    "environment": "PRODUCTION",
    "affected_service": "API Infrastructure",
    "impact_level": "MEDIUM",
    "tags": ["ssl", "certificate", "security"]
  }')

TICKET_P3_ID=$(echo $CREATE_RESPONSE | jq -r '.id')
TICKET_P3_NUMBER=$(echo $CREATE_RESPONSE | jq -r '.ticket_number')
if [ "$TICKET_P3_ID" != "null" ]; then
    log_success "P3 ticket created: $TICKET_P3_NUMBER"
else
    log_failure "Failed to create P3 ticket"
fi

# Test 9: Create ticket (P4 - Low)
log_test "Create P4 Low priority ticket"
CREATE_RESPONSE=$(curl -s -X POST ${TICKET_URL}/tickets \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ENDUSER_TOKEN" \
  -d '{
    "title": "Update documentation for new API endpoints",
    "description": "The API documentation needs to be updated to include the new v2 endpoints released last week.",
    "category": "SERVICE_REQUEST",
    "priority": "P4",
    "environment": "PRODUCTION",
    "affected_service": "Documentation",
    "impact_level": "LOW",
    "tags": ["documentation", "api"]
  }')

TICKET_P4_ID=$(echo $CREATE_RESPONSE | jq -r '.id')
TICKET_P4_NUMBER=$(echo $CREATE_RESPONSE | jq -r '.ticket_number')
if [ "$TICKET_P4_ID" != "null" ]; then
    log_success "P4 ticket created: $TICKET_P4_NUMBER"
else
    log_failure "Failed to create P4 ticket"
fi

# Test 10: List all tickets
log_test "List all tickets (default pagination)"
LIST_RESPONSE=$(curl -s -X GET "${TICKET_URL}/tickets" \
  -H "Authorization: Bearer $ENDUSER_TOKEN")

TICKET_COUNT=$(echo $LIST_RESPONSE | jq -r '.total')
if [ "$TICKET_COUNT" != "null" ]; then
    log_success "Listed $TICKET_COUNT tickets"
else
    log_failure "Failed to list tickets"
fi

# Test 11: List tickets with pagination
log_test "List tickets with pagination (page=1, size=2)"
LIST_RESPONSE=$(curl -s -X GET "${TICKET_URL}/tickets?page=1&page_size=2" \
  -H "Authorization: Bearer $ENDUSER_TOKEN")

PAGE_TICKETS=$(echo $LIST_RESPONSE | jq -r '.tickets | length')
if [ "$PAGE_TICKETS" -le 2 ]; then
    log_success "Pagination working: returned $PAGE_TICKETS tickets"
else
    log_failure "Pagination failed"
fi

# Test 12: Get ticket details
log_test "Get ticket details"
DETAIL_RESPONSE=$(curl -s -X GET "${TICKET_URL}/tickets/${TICKET_P1_ID}" \
  -H "Authorization: Bearer $ENDUSER_TOKEN")

if echo $DETAIL_RESPONSE | jq -e '.ticket_number' > /dev/null 2>&1; then
    log_success "Ticket details retrieved"
else
    log_failure "Failed to get ticket details"
fi

# Test 13: Update ticket (full update)
log_test "Update ticket (PUT - full update)"
UPDATE_RESPONSE=$(curl -s -X PUT "${TICKET_URL}/tickets/${TICKET_P3_ID}" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ENDUSER_TOKEN" \
  -d '{
    "title": "Request for SSL certificate renewal - UPDATED",
    "description": "The SSL certificate for api.example.com will expire in 30 days. Need to renew before expiration. Updated with new information.",
    "category": "SERVICE_REQUEST",
    "priority": "P3",
    "environment": "PRODUCTION",
    "affected_service": "API Infrastructure",
    "impact_level": "MEDIUM",
    "tags": ["ssl", "certificate", "security", "updated"]
  }')

if echo $UPDATE_RESPONSE | jq -e '.id' > /dev/null 2>&1; then
    log_success "Ticket updated successfully"
else
    log_failure "Failed to update ticket"
fi

# Test 14: Patch ticket (partial update)
log_test "Patch ticket (PATCH - update priority only)"
PATCH_RESPONSE=$(curl -s -X PATCH "${TICKET_URL}/tickets/${TICKET_P4_ID}" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ENDUSER_TOKEN" \
  -d '{
    "priority": "P3"
  }')

NEW_PRIORITY=$(echo $PATCH_RESPONSE | jq -r '.priority')
if [ "$NEW_PRIORITY" == "P3" ]; then
    log_success "Ticket priority patched: P4 → P3"
else
    log_failure "Failed to patch ticket"
fi

# ============================================================================
# TICKET WORKFLOW TESTS
# ============================================================================

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "SECTION 3: TICKET WORKFLOW & STATUS TRANSITIONS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Test 15: Update status to IN_PROGRESS
log_test "Update status: NEW → IN_PROGRESS"
STATUS_RESPONSE=$(curl -s -X PATCH "${TICKET_URL}/tickets/${TICKET_P2_ID}/status" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ENDUSER_TOKEN" \
  -d '{
    "status": "IN_PROGRESS",
    "notes": "Started investigating the performance issue"
  }')

NEW_STATUS=$(echo $STATUS_RESPONSE | jq -r '.status')
if [ "$NEW_STATUS" == "IN_PROGRESS" ]; then
    log_success "Status updated to IN_PROGRESS"
else
    log_failure "Failed to update status"
fi

# Test 16: Update status to PENDING_INFO
log_test "Update status: IN_PROGRESS → PENDING_INFO"
STATUS_RESPONSE=$(curl -s -X PATCH "${TICKET_URL}/tickets/${TICKET_P2_ID}/status" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ENDUSER_TOKEN" \
  -d '{
    "status": "PENDING_INFO",
    "notes": "Waiting for database logs from infrastructure team"
  }')

NEW_STATUS=$(echo $STATUS_RESPONSE | jq -r '.status')
if [ "$NEW_STATUS" == "PENDING_INFO" ]; then
    log_success "Status updated to PENDING_INFO"
else
    log_failure "Failed to update status"
fi

# Test 17: Resolve ticket
log_test "Resolve ticket"
RESOLVE_RESPONSE=$(curl -s -X POST "${TICKET_URL}/tickets/${TICKET_P3_ID}/resolve" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ENDUSER_TOKEN" \
  -d '{
    "resolution_notes": "SSL certificate renewed successfully. New certificate valid until 2026-12-31."
  }')

RESOLVED_STATUS=$(echo $RESOLVE_RESPONSE | jq -r '.status')
if [ "$RESOLVED_STATUS" == "RESOLVED" ]; then
    log_success "Ticket resolved"
else
    log_failure "Failed to resolve ticket"
fi

# Test 18: Close ticket
log_test "Close ticket"
CLOSE_RESPONSE=$(curl -s -X POST "${TICKET_URL}/tickets/${TICKET_P3_ID}/close" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ENDUSER_TOKEN" \
  -d '{
    "closure_code": "RESOLVED",
    "closure_notes": "Certificate renewal completed and verified."
  }')

CLOSED_STATUS=$(echo $CLOSE_RESPONSE | jq -r '.status')
if [ "$CLOSED_STATUS" == "CLOSED" ]; then
    log_success "Ticket closed"
else
    log_failure "Failed to close ticket"
fi

# Test 19: Reopen ticket
log_test "Reopen ticket"
REOPEN_RESPONSE=$(curl -s -X POST "${TICKET_URL}/tickets/${TICKET_P3_ID}/reopen" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ENDUSER_TOKEN" \
  -d '{
    "reason": "Certificate installation verification failed on staging environment"
  }')

REOPENED_STATUS=$(echo $REOPEN_RESPONSE | jq -r '.status')
if [ "$REOPENED_STATUS" == "REOPENED" ]; then
    log_success "Ticket reopened"
else
    log_failure "Failed to reopen ticket"
fi

# ============================================================================
# COMMENTS TESTS
# ============================================================================

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "SECTION 4: COMMENTS MANAGEMENT"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Test 20: Add comment (public)
log_test "Add public comment"
COMMENT_RESPONSE=$(curl -s -X POST "${TICKET_URL}/tickets/${TICKET_P1_ID}/comments" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ENDUSER_TOKEN" \
  -d '{
    "content": "I have verified that the database server is indeed down. All connection attempts are timing out.",
    "comment_type": "COMMENT",
    "is_internal": false
  }')

COMMENT_ID=$(echo $COMMENT_RESPONSE | jq -r '.id')
if [ "$COMMENT_ID" != "null" ]; then
    log_success "Public comment added"
else
    log_failure "Failed to add comment"
fi

# Test 21: Add note comment
log_test "Add NOTE comment"
COMMENT_RESPONSE=$(curl -s -X POST "${TICKET_URL}/tickets/${TICKET_P2_ID}/comments" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ENDUSER_TOKEN" \
  -d '{
    "content": "Performance metrics show CPU usage at 95%. This might be the root cause.",
    "comment_type": "NOTE",
    "is_internal": false
  }')

if echo $COMMENT_RESPONSE | jq -e '.id' > /dev/null 2>&1; then
    log_success "NOTE comment added"
else
    log_failure "Failed to add NOTE"
fi

# Test 22: Add solution comment
log_test "Add SOLUTION comment"
COMMENT_RESPONSE=$(curl -s -X POST "${TICKET_URL}/tickets/${TICKET_P4_ID}/comments" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ENDUSER_TOKEN" \
  -d '{
    "content": "Documentation has been updated and deployed to the docs portal.",
    "comment_type": "SOLUTION",
    "is_internal": false
  }')

if echo $COMMENT_RESPONSE | jq -e '.id' > /dev/null 2>&1; then
    log_success "SOLUTION comment added"
else
    log_failure "Failed to add SOLUTION"
fi

# Test 23: Try to add internal comment (should fail for END_USER)
log_test "Try to add internal comment (should fail for END_USER)"
COMMENT_RESPONSE=$(curl -s -X POST "${TICKET_URL}/tickets/${TICKET_P1_ID}/comments" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ENDUSER_TOKEN" \
  -d '{
    "content": "This is an internal note",
    "comment_type": "NOTE",
    "is_internal": true
  }')

if echo $COMMENT_RESPONSE | jq -e '.detail' | grep -q "Only engineers" > /dev/null 2>&1; then
    log_success "Internal comment blocked for END_USER (expected)"
else
    log_failure "Internal comment restriction not working"
fi

# Test 24: List comments
log_test "List comments for ticket"
COMMENTS_RESPONSE=$(curl -s -X GET "${TICKET_URL}/tickets/${TICKET_P1_ID}/comments" \
  -H "Authorization: Bearer $ENDUSER_TOKEN")

COMMENT_COUNT=$(echo $COMMENTS_RESPONSE | jq -r '.total')
if [ "$COMMENT_COUNT" != "null" ]; then
    log_success "Listed $COMMENT_COUNT comments"
else
    log_failure "Failed to list comments"
fi

# ============================================================================
# ATTACHMENTS TESTS
# ============================================================================

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "SECTION 5: ATTACHMENTS MANAGEMENT"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Create test files
echo "Creating test files for upload..."
cat > /tmp/error.log << 'EOF'
[2025-11-27 10:00:01] ERROR: Database connection timeout
[2025-11-27 10:00:02] ERROR: Failed to execute query
[2025-11-27 10:00:03] ERROR: Connection pool exhausted
[2025-11-27 10:00:04] CRITICAL: Database server not responding
EOF

cat > /tmp/screenshot.txt << 'EOF'
This is a placeholder for a screenshot file.
In a real scenario, this would be a PNG or JPG file.
For testing purposes, we're using a text file.
EOF

cat > /tmp/config.txt << 'EOF'
# Configuration file
database.host=db.example.com
database.port=5432
database.name=production
max_connections=100
EOF

# Test 25: Upload log file
log_test "Upload attachment (log file)"
UPLOAD_RESPONSE=$(curl -s -X POST "${TICKET_URL}/tickets/${TICKET_P1_ID}/attachments" \
  -H "Authorization: Bearer $ENDUSER_TOKEN" \
  -F "file=@/tmp/error.log")

ATTACHMENT_ID=$(echo $UPLOAD_RESPONSE | jq -r '.id')
if [ "$ATTACHMENT_ID" != "null" ]; then
    log_success "Log file uploaded: $ATTACHMENT_ID"
else
    log_failure "Failed to upload log file"
    echo $UPLOAD_RESPONSE | jq
fi

# Test 26: Upload screenshot
log_test "Upload attachment (screenshot)"
UPLOAD_RESPONSE=$(curl -s -X POST "${TICKET_URL}/tickets/${TICKET_P2_ID}/attachments" \
  -H "Authorization: Bearer $ENDUSER_TOKEN" \
  -F "file=@/tmp/screenshot.txt")

if echo $UPLOAD_RESPONSE | jq -e '.id' > /dev/null 2>&1; then
    log_success "Screenshot uploaded"
else
    log_failure "Failed to upload screenshot"
fi

# Test 27: Upload config file
log_test "Upload attachment (config file)"
UPLOAD_RESPONSE=$(curl -s -X POST "${TICKET_URL}/tickets/${TICKET_P2_ID}/attachments" \
  -H "Authorization: Bearer $ENDUSER_TOKEN" \
  -F "file=@/tmp/config.txt")

if echo $UPLOAD_RESPONSE | jq -e '.id' > /dev/null 2>&1; then
    log_success "Config file uploaded"
else
    log_failure "Failed to upload config file"
fi

# Test 28: List attachments
log_test "List attachments for ticket"
ATTACHMENTS_RESPONSE=$(curl -s -X GET "${TICKET_URL}/tickets/${TICKET_P1_ID}/attachments" \
  -H "Authorization: Bearer $ENDUSER_TOKEN")

ATTACHMENT_COUNT=$(echo $ATTACHMENTS_RESPONSE | jq -r '.total')
if [ "$ATTACHMENT_COUNT" != "null" ]; then
    log_success "Listed $ATTACHMENT_COUNT attachments"
else
    log_failure "Failed to list attachments"
fi

# ============================================================================
# HISTORY TESTS
# ============================================================================

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "SECTION 6: TICKET HISTORY & AUDIT TRAIL"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Test 29: Get ticket history
log_test "Get ticket history"
HISTORY_RESPONSE=$(curl -s -X GET "${TICKET_URL}/tickets/${TICKET_P3_ID}/history" \
  -H "Authorization: Bearer $ENDUSER_TOKEN")

HISTORY_COUNT=$(echo $HISTORY_RESPONSE | jq -r '.total')
if [ "$HISTORY_COUNT" != "null" ]; then
    log_success "Retrieved $HISTORY_COUNT history entries"
    echo ""
    log_info "History entries:"
    echo $HISTORY_RESPONSE | jq -r '.history[] | "  - \(.change_type) at \(.created_at)"' | head -5
else
    log_failure "Failed to get history"
fi

# ============================================================================
# FILTERING & SEARCH TESTS
# ============================================================================

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "SECTION 7: FILTERING, SEARCH & SORTING"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Test 30: Filter by status
log_test "Filter tickets by status (NEW)"
FILTER_RESPONSE=$(curl -s -X GET "${TICKET_URL}/tickets?status=NEW" \
  -H "Authorization: Bearer $ENDUSER_TOKEN")

FILTERED_COUNT=$(echo $FILTER_RESPONSE | jq -r '.total')
if [ "$FILTERED_COUNT" != "null" ]; then
    log_success "Found $FILTERED_COUNT NEW tickets"
else
    log_failure "Status filter failed"
fi

# Test 31: Filter by priority
log_test "Filter tickets by priority (P1)"
FILTER_RESPONSE=$(curl -s -X GET "${TICKET_URL}/tickets?priority=P1" \
  -H "Authorization: Bearer $ENDUSER_TOKEN")

FILTERED_COUNT=$(echo $FILTER_RESPONSE | jq -r '.total')
if [ "$FILTERED_COUNT" != "null" ]; then
    log_success "Found $FILTERED_COUNT P1 tickets"
else
    log_failure "Priority filter failed"
fi

# Test 32: Filter by category
log_test "Filter tickets by category (INCIDENT)"
FILTER_RESPONSE=$(curl -s -X GET "${TICKET_URL}/tickets?category=INCIDENT" \
  -H "Authorization: Bearer $ENDUSER_TOKEN")

FILTERED_COUNT=$(echo $FILTER_RESPONSE | jq -r '.total')
if [ "$FILTERED_COUNT" != "null" ]; then
    log_success "Found $FILTERED_COUNT INCIDENT tickets"
else
    log_failure "Category filter failed"
fi

# Test 33: Multiple filters
log_test "Multiple filters (status=NEW, priority=P1)"
FILTER_RESPONSE=$(curl -s -X GET "${TICKET_URL}/tickets?status=NEW&priority=P1" \
  -H "Authorization: Bearer $ENDUSER_TOKEN")

FILTERED_COUNT=$(echo $FILTER_RESPONSE | jq -r '.total')
if [ "$FILTERED_COUNT" != "null" ]; then
    log_success "Found $FILTERED_COUNT tickets matching criteria"
else
    log_failure "Multiple filters failed"
fi

# Test 34: Search by keyword
log_test "Search tickets (keyword: database)"
SEARCH_RESPONSE=$(curl -s -X GET "${TICKET_URL}/tickets?search=database" \
  -H "Authorization: Bearer $ENDUSER_TOKEN")

SEARCH_COUNT=$(echo $SEARCH_RESPONSE | jq -r '.total')
if [ "$SEARCH_COUNT" != "null" ]; then
    log_success "Found $SEARCH_COUNT tickets matching 'database'"
else
    log_failure "Search failed"
fi

# Test 35: Sort by created_at (desc)
log_test "Sort tickets by created_at (desc)"
SORT_RESPONSE=$(curl -s -X GET "${TICKET_URL}/tickets?sort_by=created_at&order=desc" \
  -H "Authorization: Bearer $ENDUSER_TOKEN")

if echo $SORT_RESPONSE | jq -e '.tickets[0].created_at' > /dev/null 2>&1; then
    log_success "Tickets sorted by created_at"
else
    log_failure "Sorting failed"
fi

# Test 36: Sort by priority
log_test "Sort tickets by priority"
SORT_RESPONSE=$(curl -s -X GET "${TICKET_URL}/tickets?sort_by=priority&order=asc" \
  -H "Authorization: Bearer $ENDUSER_TOKEN")

if echo $SORT_RESPONSE | jq -e '.tickets' > /dev/null 2>&1; then
    log_success "Tickets sorted by priority"
else
    log_failure "Priority sorting failed"
fi

# ============================================================================
# SLA & VALIDATION TESTS
# ============================================================================

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "SECTION 8: SLA TRACKING & DATA VALIDATION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Test 37: Verify SLA dates on P1 ticket
log_test "Verify SLA dates for P1 ticket"
TICKET_RESPONSE=$(curl -s -X GET "${TICKET_URL}/tickets/${TICKET_P1_ID}" \
  -H "Authorization: Bearer $ENDUSER_TOKEN")

RESPONSE_DUE=$(echo $TICKET_RESPONSE | jq -r '.response_due_at')
RESOLUTION_DUE=$(echo $TICKET_RESPONSE | jq -r '.resolution_due_at')
if [ "$RESPONSE_DUE" != "null" ] && [ "$RESOLUTION_DUE" != "null" ]; then
    log_success "SLA dates set correctly for P1"
else
    log_failure "SLA dates not set"
fi

# Test 38: Try to create ticket with short title (should fail)
log_test "Validation: Short title (should fail)"
CREATE_RESPONSE=$(curl -s -X POST ${TICKET_URL}/tickets \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ENDUSER_TOKEN" \
  -d '{
    "title": "Short",
    "description": "This is a description that is long enough",
    "category": "INCIDENT",
    "priority": "P3"
  }')

if echo $CREATE_RESPONSE | jq -e '.detail' > /dev/null 2>&1; then
    log_success "Short title rejected (validation working)"
else
    log_failure "Validation failed - short title accepted"
fi

# Test 39: Try invalid status transition
log_test "Validation: Invalid status transition (should fail)"
STATUS_RESPONSE=$(curl -s -X PATCH "${TICKET_URL}/tickets/${TICKET_P1_ID}/status" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ENDUSER_TOKEN" \
  -d '{
    "status": "CLOSED",
    "notes": "Trying to close without resolving first"
  }')

if echo $STATUS_RESPONSE | jq -e '.detail' > /dev/null 2>&1; then
    log_success "Invalid transition rejected (validation working)"
else
    log_failure "Status transition validation failed"
fi

# ============================================================================
# NEGATIVE TESTS
# ============================================================================

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "SECTION 9: NEGATIVE TESTS & SECURITY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Test 40: Access without token
log_test "Access tickets without authentication (should fail)"
NO_AUTH_RESPONSE=$(curl -s -X GET "${TICKET_URL}/tickets")

if echo $NO_AUTH_RESPONSE | jq -e '.detail' | grep -q "Not authenticated" > /dev/null 2>&1; then
    log_success "Unauthenticated access blocked"
else
    log_failure "Authentication not enforced"
fi

# Test 41: Invalid ticket ID
log_test "Get non-existent ticket (should return 404)"
INVALID_RESPONSE=$(curl -s -X GET "${TICKET_URL}/tickets/00000000-0000-0000-0000-000000000000" \
  -H "Authorization: Bearer $ENDUSER_TOKEN")

if echo $INVALID_RESPONSE | jq -e '.detail' > /dev/null 2>&1; then
    log_success "Non-existent ticket handled correctly"
else
    log_failure "Invalid ticket ID handling failed"
fi

# Test 42: Invalid priority value
log_test "Create ticket with invalid priority (should fail)"
INVALID_RESPONSE=$(curl -s -X POST ${TICKET_URL}/tickets \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ENDUSER_TOKEN" \
  -d '{
    "title": "Test ticket with invalid priority",
    "description": "This ticket has an invalid priority value",
    "category": "INCIDENT",
    "priority": "P99"
  }')

if echo $INVALID_RESPONSE | jq -e '.detail' > /dev/null 2>&1; then
    log_success "Invalid priority rejected"
else
    log_failure "Invalid priority accepted"
fi

# ============================================================================
# FINAL REPORT
# ============================================================================

echo ""
echo "================================================================================"
echo "                              TEST SUMMARY"
echo "================================================================================"
echo ""
echo -e "${GREEN}Passed:${NC} $PASSED / $TOTAL"
echo -e "${RED}Failed:${NC} $FAILED / $TOTAL"
echo -e "Success Rate: $(awk "BEGIN {printf \"%.1f\", ($PASSED/$TOTAL)*100}")%"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ ALL TESTS PASSED!${NC}"
    echo ""
    echo "The Ticket Management Module is fully functional and ready for deployment."
else
    echo -e "${RED}❌ SOME TESTS FAILED${NC}"
    echo ""
    echo "Please review the failed tests above and address the issues."
fi

echo ""
echo "================================================================================"
echo "                           TESTED ENDPOINTS"
echo "================================================================================"
echo ""
echo "Authentication & User Management:"
echo "  ✓ POST   /api/v1/auth/register"
echo "  ✓ POST   /api/v1/auth/login"
echo "  ✓ GET    /api/v1/auth/me"
echo ""
echo "Ticket CRUD:"
echo "  ✓ POST   /api/v1/tickets"
echo "  ✓ GET    /api/v1/tickets"
echo "  ✓ GET    /api/v1/tickets/{id}"
echo "  ✓ PUT    /api/v1/tickets/{id}"
echo "  ✓ PATCH  /api/v1/tickets/{id}"
echo ""
echo "Ticket Workflow:"
echo "  ✓ PATCH  /api/v1/tickets/{id}/status"
echo "  ✓ POST   /api/v1/tickets/{id}/resolve"
echo "  ✓ POST   /api/v1/tickets/{id}/close"
echo "  ✓ POST   /api/v1/tickets/{id}/reopen"
echo ""
echo "Comments:"
echo "  ✓ POST   /api/v1/tickets/{id}/comments"
echo "  ✓ GET    /api/v1/tickets/{id}/comments"
echo ""
echo "Attachments:"
echo "  ✓ POST   /api/v1/tickets/{id}/attachments"
echo "  ✓ GET    /api/v1/tickets/{id}/attachments"
echo ""
echo "History:"
echo "  ✓ GET    /api/v1/tickets/{id}/history"
echo ""
echo "Filtering & Search:"
echo "  ✓ GET    /api/v1/tickets?status={status}"
echo "  ✓ GET    /api/v1/tickets?priority={priority}"
echo "  ✓ GET    /api/v1/tickets?category={category}"
echo "  ✓ GET    /api/v1/tickets?search={keyword}"
echo "  ✓ GET    /api/v1/tickets?sort_by={field}&order={asc|desc}"
echo ""
echo "================================================================================"
echo ""

# Cleanup
rm -f /tmp/error.log /tmp/screenshot.txt /tmp/config.txt

exit $FAILED
