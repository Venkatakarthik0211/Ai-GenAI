#!/bin/bash

# User Management Script for Ticket Management System
# This script helps create and delete users via the Auth API

  # Successfully registered users for all role levels using the /auth/register endpoint:
  # - ✓ admin - ADMIN (password: Admin@123)
  # - ✓ manager - MANAGER (password: User@123)
  # - ✓ team.lead - TEAM_LEAD (password: User@123)
  # - ✓ senior.engineer - SENIOR_ENGINEER (password: User@123)
  # - ✓ devops.user - DEVOPS_ENGINEER (password: User@123)

  # All users tested and can login successfully!

  # 3. Created User Management Shell Script

  # Created /backend/manage_users.sh with full functionality:

  # Available Commands:

  # # List all users
  # ./manage_users.sh list

  # # List users by role
  # ./manage_users.sh list -r DEVOPS_ENGINEER

  # # List only active users
  # ./manage_users.sh list -a

  # # Show role hierarchy
  # ./manage_users.sh roles

  # # Create new user
  # ./manage_users.sh create -u username -e email@company.com -f FirstName -l LastName -r ROLE

  # # Delete user (soft delete)
  # ./manage_users.sh delete -u username

  # # Delete user permanently
  # ./manage_users.sh delete -u username --hard

  # # Show help
  # ./manage_users.sh help

set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
BASE_URL="${AUTH_SERVICE_URL:-http://localhost:8001}/api/v1/auth"
ADMIN_USERNAME="${ADMIN_USERNAME:-admin}"
ADMIN_PASSWORD="${ADMIN_PASSWORD:-Admin@123}"

# Function to print usage
usage() {
  cat << EOF
${BLUE}User Management Script for Ticket Management System${NC}

Usage: $0 [command] [options]

Commands:
  create    Create a new user
  delete    Delete a user
  list      List all users
  roles     Show role hierarchy
  help      Show this help message

Examples:
  # Create a new user
  $0 create -u john.doe -e john@example.com -f John -l Doe -r DEVOPS_ENGINEER

  # Delete a user
  $0 delete -u john.doe

  # List all users
  $0 list

  # List users by role
  $0 list -r DEVOPS_ENGINEER

  # Show role hierarchy
  $0 roles

Create Options:
  -u, --username       Username (required)
  -e, --email          Email address (required)
  -f, --first-name     First name (required)
  -l, --last-name      Last name (required)
  -r, --role           Role: END_USER, DEVOPS_ENGINEER, SENIOR_ENGINEER, TEAM_LEAD, MANAGER, ADMIN
                       (default: END_USER)
  -p, --password       Password (default: User@123)
  -d, --department     Department (optional)
  -P, --phone          Phone number (optional)

Delete Options:
  -u, --username       Username to delete (required)
  --hard               Permanently delete from database (default: soft delete)

List Options:
  -r, --role           Filter by role (optional)
  -a, --active         Show only active users (optional)

Environment Variables:
  AUTH_SERVICE_URL     Auth service URL (default: http://localhost:8001)
  ADMIN_USERNAME       Admin username (default: admin)
  ADMIN_PASSWORD       Admin password (default: Admin@123)

EOF
  exit 0
}

# Function to get admin token
get_admin_token() {
  local response
  response=$(curl -s -X POST "$BASE_URL/login" \
    -H "Content-Type: application/json" \
    -d "{\"username\": \"$ADMIN_USERNAME\", \"password\": \"$ADMIN_PASSWORD\"}")

  local token
  token=$(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin).get('access_token', ''))" 2>/dev/null || echo "")

  if [ -z "$token" ]; then
    echo -e "${RED}Failed to authenticate as admin${NC}" >&2
    echo "Response: $response" >&2
    exit 1
  fi

  echo "$token"
}

# Function to show role hierarchy
show_roles() {
  cat << EOF
${BLUE}=== Ticket Escalation Role Hierarchy ===${NC}

Level 5: ${YELLOW}ADMIN${NC}
         └─ Final escalation level
         └─ System administration
         └─ Cannot escalate further

Level 4: ${YELLOW}MANAGER${NC}
         └─ Senior management
         └─ Can escalate to ADMIN

Level 3: ${YELLOW}TEAM_LEAD${NC}
         └─ Team leadership
         └─ Can escalate to MANAGER

Level 2: ${YELLOW}SENIOR_ENGINEER${NC}
         └─ Senior technical staff
         └─ Can escalate to TEAM_LEAD

Level 1: ${YELLOW}DEVOPS_ENGINEER${NC}
         └─ First level ticket assignment
         └─ Can escalate to SENIOR_ENGINEER

Level 0: ${YELLOW}END_USER${NC}
         └─ Ticket creators
         └─ Tickets auto-assigned to DEVOPS_ENGINEER

${GREEN}Escalation Flow:${NC}
END_USER creates ticket → Auto-assigned to DEVOPS_ENGINEER
DEVOPS_ENGINEER → SENIOR_ENGINEER → TEAM_LEAD → MANAGER → ADMIN
Each level can either RESOLVE or ESCALATE the ticket.

EOF
}

# Function to list users
list_users() {
  local role=""
  local active=""

  while [[ $# -gt 0 ]]; do
    case $1 in
      -r|--role)
        role="$2"
        shift 2
        ;;
      -a|--active)
        active="true"
        shift
        ;;
      *)
        echo -e "${RED}Unknown option: $1${NC}"
        exit 1
        ;;
    esac
  done

  echo -e "${BLUE}=== Fetching users ===${NC}"

  local token
  token=$(get_admin_token)

  local url="$BASE_URL/admin/users?"
  [ -n "$role" ] && url="${url}role=$role&"
  [ -n "$active" ] && url="${url}is_active=$active&"

  # Fetch users
  curl -s -X GET "$url" -H "Authorization: Bearer $token" > /tmp/users_list.json

  if [ ! -s /tmp/users_list.json ]; then
    echo -e "${RED}Failed to fetch users${NC}"
    exit 1
  fi

  # Parse and display
  python3 << 'PYTHON_EOF'
import sys
import json

try:
    with open('/tmp/users_list.json', 'r') as f:
        users = json.load(f)

    if not users:
        print("No users found")
        sys.exit(0)

    # Print header
    print(f"\n{'Username':<20} {'Email':<30} {'Role':<20} {'Active':<8} {'Name':<30}")
    print("=" * 108)

    # Print users
    for user in users:
        username = user.get('username', '')[:19]
        email = user.get('email', '')[:29]
        role = user.get('role', '')[:19]
        active = 'Yes' if user.get('is_active') else 'No'
        name = f"{user.get('first_name', '')} {user.get('last_name', '')}"[:29]

        print(f"{username:<20} {email:<30} {role:<20} {active:<8} {name:<30}")

    print(f"\nTotal users: {len(users)}")
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)
PYTHON_EOF
}

# Function to create user
create_user() {
  local username="" email="" first_name="" last_name="" role="END_USER" password="User@123"
  local department="" phone=""

  while [[ $# -gt 0 ]]; do
    case $1 in
      -u|--username)
        username="$2"
        shift 2
        ;;
      -e|--email)
        email="$2"
        shift 2
        ;;
      -f|--first-name)
        first_name="$2"
        shift 2
        ;;
      -l|--last-name)
        last_name="$2"
        shift 2
        ;;
      -r|--role)
        role="$2"
        shift 2
        ;;
      -p|--password)
        password="$2"
        shift 2
        ;;
      -d|--department)
        department="$2"
        shift 2
        ;;
      -P|--phone)
        phone="$2"
        shift 2
        ;;
      *)
        echo -e "${RED}Unknown option: $1${NC}"
        exit 1
        ;;
    esac
  done

  # Validate required fields
  if [ -z "$username" ] || [ -z "$email" ] || [ -z "$first_name" ] || [ -z "$last_name" ]; then
    echo -e "${RED}Error: username, email, first-name, and last-name are required${NC}"
    echo "Use: $0 create -u USERNAME -e EMAIL -f FIRSTNAME -l LASTNAME [-r ROLE]"
    exit 1
  fi

  # Validate role
  local valid_roles=("END_USER" "DEVOPS_ENGINEER" "SENIOR_ENGINEER" "TEAM_LEAD" "MANAGER" "ADMIN")
  if [[ ! " ${valid_roles[@]} " =~ " ${role} " ]]; then
    echo -e "${RED}Invalid role: $role${NC}"
    echo "Valid roles: ${valid_roles[*]}"
    exit 1
  fi

  echo -e "${BLUE}Creating user: $username ($role)${NC}"

  # Register user
  local register_data="{\"username\": \"$username\", \"email\": \"$email\", \"first_name\": \"$first_name\", \"last_name\": \"$last_name\", \"password\": \"$password\""
  [ -n "$department" ] && register_data="$register_data, \"department\": \"$department\""
  [ -n "$phone" ] && register_data="$register_data, \"phone_number\": \"$phone\""
  register_data="$register_data}"

  local response
  response=$(curl -s -X POST "$BASE_URL/register" \
    -H "Content-Type: application/json" \
    -d "$register_data")

  local user_id
  user_id=$(echo "$response" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('id', ''))" 2>/dev/null || echo "")

  if [ -z "$user_id" ]; then
    echo -e "${RED}Failed to register user${NC}"
    echo "Response: $response"
    exit 1
  fi

  echo -e "${GREEN}User registered with ID: $user_id${NC}"

  # Update role if not END_USER
  if [ "$role" != "END_USER" ]; then
    echo "Updating role to $role..."

    local token
    token=$(get_admin_token)

    local role_response
    role_response=$(curl -s -X PATCH "$BASE_URL/admin/users/$user_id/role" \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer $token" \
      -d "{\"role\": \"$role\"}")

    local updated_role
    updated_role=$(echo "$role_response" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('role', ''))" 2>/dev/null || echo "")

    if [ "$updated_role" == "$role" ]; then
      echo -e "${GREEN}Role updated successfully${NC}"
    else
      echo -e "${RED}Failed to update role${NC}"
      echo "Response: $role_response"
      exit 1
    fi
  fi

  echo -e "\n${GREEN}✓ User created successfully${NC}"
  echo "  Username: $username"
  echo "  Email: $email"
  echo "  Role: $role"
  echo "  Password: $password"
}

# Function to delete user
delete_user() {
  local username=""
  local hard_delete=false

  while [[ $# -gt 0 ]]; do
    case $1 in
      -u|--username)
        username="$2"
        shift 2
        ;;
      --hard)
        hard_delete=true
        shift
        ;;
      *)
        echo -e "${RED}Unknown option: $1${NC}"
        exit 1
        ;;
    esac
  done

  if [ -z "$username" ]; then
    echo -e "${RED}Error: username is required${NC}"
    echo "Use: $0 delete -u USERNAME [--hard]"
    exit 1
  fi

  echo -e "${YELLOW}Deleting user: $username${NC}"

  local token
  token=$(get_admin_token)

  # Get user ID
  local response
  response=$(curl -s -X GET "$BASE_URL/admin/users?search=$username" \
    -H "Authorization: Bearer $token")

  local user_id
  user_id=$(echo "$response" | python3 -c "import sys, json; users=json.load(sys.stdin); print(users[0]['id'] if users and users[0]['username']=='$username' else '')" 2>/dev/null || echo "")

  if [ -z "$user_id" ]; then
    echo -e "${RED}User not found: $username${NC}"
    exit 1
  fi

  if [ "$hard_delete" = true ]; then
    echo -e "${RED}WARNING: Hard delete will permanently remove user from database${NC}"
    read -p "Are you sure? (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
      echo "Cancelled"
      exit 0
    fi

    # Hard delete via database
    docker exec ticket_db psql -U postgres -d ticket_management -c "DELETE FROM users WHERE id = '$user_id';" >/dev/null 2>&1
    echo -e "${GREEN}User permanently deleted${NC}"
  else
    # Soft delete via API
    local delete_response
    delete_response=$(curl -s -X DELETE "$BASE_URL/admin/users/$user_id" \
      -H "Authorization: Bearer $token")

    echo -e "${GREEN}User soft-deleted (deactivated)${NC}"
  fi

  echo -e "${GREEN}✓ User deleted: $username${NC}"
}

# Main script logic
case "${1:-help}" in
  create)
    shift
    create_user "$@"
    ;;
  delete)
    shift
    delete_user "$@"
    ;;
  list)
    shift
    list_users "$@"
    ;;
  roles)
    show_roles
    ;;
  help|--help|-h)
    usage
    ;;
  *)
    echo -e "${RED}Unknown command: $1${NC}"
    echo "Use '$0 help' for usage information"
    exit 1
    ;;
esac
