#!/bin/bash
echo "=== Testing All User Logins ==="
for user in "admin:Admin@123" "devops.user:User@123" "senior.engineer:User@123" "team.lead:User@123" "manager:User@123"; do
  username="${user%%:*}"
  password="${user##*:}"
  result=$(curl -s -X POST http://localhost:8001/api/v1/auth/login -H "Content-Type: application/json" -d "{\"username\": \"$username\", \"password\": \"$password\"}" | python3 -c "import sys, json; data=json.load(sys.stdin); print('SUCCESS' if 'access_token' in data else data.get('detail', 'FAILED'))")
  printf "%-20s : %s\n" "$username" "$result"
done
