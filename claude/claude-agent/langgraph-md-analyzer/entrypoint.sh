#!/bin/bash

set -e

echo "=========================================="
echo "  LANGGRAPH MD ANALYZER - AWS Bedrock"
echo "=========================================="
echo ""

# Check if AWS configuration is mounted
if [ ! -d /root/.aws ]; then
    echo "[ERROR] AWS configuration not mounted!"
    echo "[ERROR] Please mount ~/.aws directory"
    echo "[ERROR] Example: docker compose run --rm analyzer"
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
chown -R claude-user:claude-user /workspace/files 2>/dev/null || true

echo "[INFO] Configuration complete"
echo ""
echo "=========================================="
echo "  Starting LangGraph Analyzer Agent"
echo "=========================================="
echo ""

# Create a script that will run as claude-user
cat > /tmp/run_analyzer.sh << 'EOFSCRIPT'
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

# Run the LangGraph analyzer agent
echo "[INFO] Starting LangGraph MD Analyzer..."
echo ""

python3 md_analyzer_agent.py 2>&1 | tee /workspace/logs/analyzer.log

exit_code=${PIPESTATUS[0]}

if [ $exit_code -eq 0 ]; then
    echo ""
    echo "[SUCCESS] Analyzer agent exited successfully"
else
    echo ""
    echo "[ERROR] Analyzer agent exited with code: $exit_code"
fi

exit $exit_code
EOFSCRIPT

chmod +x /tmp/run_analyzer.sh

# Run the script as claude-user
su - claude-user -c "bash /tmp/run_analyzer.sh"

exit_code=$?

echo ""
echo "=========================================="

if [ $exit_code -eq 0 ]; then
    echo "[SUCCESS] Session completed successfully!"
else
    echo "[ERROR] Session failed with exit code: $exit_code"
fi

echo ""
echo "Log file saved to: /workspace/logs/analyzer.log"
echo "Analysis files saved to: /workspace/logs/"
echo ""
echo "Container exiting..."
exit $exit_code
