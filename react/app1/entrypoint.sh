#!/bin/bash
set -e

echo "Starting React Admin App..."
echo "Environment: ${NODE_ENV:-production}"
echo "Available at: http://localhost/admin/"

# Execute the main command
exec "$@"