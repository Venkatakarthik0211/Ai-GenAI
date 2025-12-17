#!/bin/bash

set -e

echo "=========================================="
echo "  CALCULATOR AGENT - AWS Bedrock"
echo "=========================================="
echo ""

# Function to set up AWS Bedrock credentials
set_aws_bedrock_creds() {
    echo "[INFO] Setting up AWS Bedrock credentials..."

    export AWS_REGION="us-east-1"
    export AWS_PROFILE="default"

    # Test AWS access with mounted credentials
    echo "[INFO] Verifying AWS credentials..."
    if ! aws sts get-caller-identity >/dev/null 2>&1; then
        echo "[ERROR] AWS authentication failed!"
        echo "[ERROR] Please check your ~/.aws/credentials file"
        return 1
    fi

    echo "[SUCCESS] AWS authentication verified"
    aws sts get-caller-identity

    # Generate Bedrock bearer token using existing credentials
    echo "[INFO] Generating Bedrock bearer token..."
    export AWS_BEARER_TOKEN_BEDROCK="$(python3 /workspace/bedrock.py)"
    export AWS_BEARER_TOKEN_BEDROCK="$(echo ${AWS_BEARER_TOKEN_BEDROCK} | jq -r '.bearerToken')"

    # Set Claude Code environment variables for Bedrock
    export CLAUDE_CODE_USE_BEDROCK=1
    export ANTHROPIC_MODEL='us.anthropic.claude-sonnet-4-5-20250929-v1:0'
    export CLAUDE_CODE_MAX_OUTPUT_TOKENS=432000

    echo "[SUCCESS] Bedrock credentials configured"
    echo "[INFO] Bearer token: ${AWS_BEARER_TOKEN_BEDROCK:0:50}..."
}

# Check if AWS configuration is mounted
if [ ! -d /root/.aws ]; then
    echo "[ERROR] AWS configuration not mounted!"
    echo "[ERROR] Please mount ~/.aws directory"
    echo "[ERROR] Example: docker-compose up"
    exit 1
fi

echo "[INFO] AWS configuration found"

# Copy AWS credentials to claude-user's home (needed for non-root user)
echo "[INFO] Setting up AWS credentials for claude-user..."
cp -r /root/.aws /home/claude-user/
chown -R claude-user:claude-user /home/claude-user/.aws

# Copy settings to claude-user's home
echo "[INFO] Setting up Claude Code configuration..."
mkdir -p /home/claude-user/.claude/transcripts
cp /tmp/settings.json /home/claude-user/.claude/settings.json
chown -R claude-user:claude-user /home/claude-user/.claude

# Ensure workspace permissions are correct
chown -R claude-user:claude-user /workspace/logs 2>/dev/null || true

echo "[INFO] Configuration complete"
echo ""
echo "=========================================="
echo "  Starting Calculator Agent"
echo "=========================================="
echo ""

# Create a script that will run as claude-user
cat > /tmp/run_calculator.sh << 'EOFSCRIPT'
#!/bin/bash
set -e

# Set up AWS credentials
export AWS_CONFIG_FILE=/home/claude-user/.aws/config
export AWS_SHARED_CREDENTIALS_FILE=/home/claude-user/.aws/credentials
export AWS_REGION="us-east-1"
export AWS_PROFILE="default"

# Verify Claude Code is installed
if ! command -v claude &> /dev/null; then
    echo "[ERROR] Claude Code CLI not found!"
    echo "[ERROR] Please ensure @anthropic-ai/claude-code is installed"
    exit 1
fi

# Generate Bedrock bearer token as claude-user
echo "[INFO] Generating Bedrock bearer token as claude-user..."
export AWS_BEARER_TOKEN_BEDROCK="$(python3 /workspace/bedrock.py | jq -r '.bearerToken')"

# Set Claude Code environment variables
export CLAUDE_CODE_USE_BEDROCK=1
export ANTHROPIC_MODEL='us.anthropic.claude-sonnet-4-5-20250929-v1:0'
export CLAUDE_CODE_MAX_OUTPUT_TOKENS=432000

echo "[INFO] Bearer token configured: ${AWS_BEARER_TOKEN_BEDROCK:0:50}..."
echo "[INFO] Claude Code CLI found: $(which claude)"
echo "[INFO] Working directory: /workspace"
echo ""

# Change to workspace directory
cd /workspace

# Run the calculator agent
echo "[INFO] Starting interactive calculator agent..."
echo ""

python3 calculator_agent.py 2>&1 | tee /workspace/logs/calculator.log

exit_code=${PIPESTATUS[0]}

if [ $exit_code -eq 0 ]; then
    echo ""
    echo "[SUCCESS] Calculator agent exited successfully"
else
    echo ""
    echo "[ERROR] Calculator agent exited with code: $exit_code"
fi

exit $exit_code
EOFSCRIPT

chmod +x /tmp/run_calculator.sh

# Run the script as claude-user
su - claude-user -c "bash /tmp/run_calculator.sh"

exit_code=$?

echo ""
echo "=========================================="

if [ $exit_code -eq 0 ]; then
    echo "[SUCCESS] Session completed successfully!"
else
    echo "[ERROR] Session failed with exit code: $exit_code"
fi

echo ""
echo "Log file saved to: /workspace/logs/calculator.log"
echo ""
echo "Container exiting..."
exit $exit_code
