#!/bin/bash

set -e

echo "=========================================="
echo "  Claude Code Automation - AWS Bedrock"
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
    exit 1
fi

echo "[INFO] AWS configuration found"

# Copy AWS credentials to claude-user's home (needed for non-root user)
echo "[INFO] Setting up AWS credentials for claude-user..."
cp -r /root/.aws /home/claude-user/
chown -R claude-user:claude-user /home/claude-user/.aws

# Copy settings to claude-user's home
mkdir -p /home/claude-user/.claude/transcripts
cp /tmp/settings.json /home/claude-user/.claude/settings.json

# Copy custom subagents from /workspace/.claude/agents to claude-user's .claude
if [ -d /workspace/.claude/agents ]; then
    echo "[INFO] Copying custom subagents to claude-user..."
    mkdir -p /home/claude-user/.claude/agents
    cp -f /workspace/.claude/agents/*.md /home/claude-user/.claude/agents/ 2>/dev/null || true
    echo "[INFO] Available custom subagents:"
    ls -1 /home/claude-user/.claude/agents/ 2>/dev/null || echo "  (none)"
fi

# Copy any existing transcripts from root to claude-user (for resume)
if [ -d /root/.claude/transcripts ] && [ "$(ls -A /root/.claude/transcripts 2>/dev/null)" ]; then
    echo "[INFO] Copying existing transcripts to claude-user..."
    cp -f /root/.claude/transcripts/* /home/claude-user/.claude/transcripts/ 2>/dev/null || true
fi

chown -R claude-user:claude-user /home/claude-user/.claude

# Ensure workspace permissions are correct (exclude read-only .claude directory)
chown -R claude-user:claude-user /workspace/.agents 2>/dev/null || true
chown -R claude-user:claude-user /workspace/output 2>/dev/null || true

echo "[INFO] Credentials and settings configured for claude-user"

echo ""
echo "=========================================="
echo "  Starting Claude Code Generation"
echo "=========================================="
echo ""

# Check if master prompt exists
if [ ! -f /workspace/.agents/MASTER_PROMPT.md ]; then
    echo "[ERROR] MASTER_PROMPT.md not found in /workspace/.agents/"
    exit 1
fi

echo "[INFO] Found MASTER_PROMPT.md"
echo "[INFO] Switching to claude-user to run Claude Code with --dangerously-skip-permissions"
echo ""

# Create a script that will run as claude-user
cat > /tmp/run_claude.sh << 'EOFSCRIPT'
#!/bin/bash
set -e

# Set up AWS credentials
export AWS_CONFIG_FILE=/home/claude-user/.aws/config
export AWS_SHARED_CREDENTIALS_FILE=/home/claude-user/.aws/credentials
export AWS_REGION="us-east-1"
export AWS_PROFILE="default"

# Generate Bedrock bearer token
echo "[INFO] Generating Bedrock bearer token as claude-user..."
export AWS_BEARER_TOKEN_BEDROCK="$(python3 /workspace/bedrock.py | jq -r '.bearerToken')"

# Set Claude Code environment variables
export CLAUDE_CODE_USE_BEDROCK=1
export ANTHROPIC_MODEL='us.anthropic.claude-sonnet-4-5-20250929-v1:0'
export CLAUDE_CODE_MAX_OUTPUT_TOKENS=432000

echo "[INFO] Bearer token configured: ${AWS_BEARER_TOKEN_BEDROCK:0:50}..."
echo "[INFO] Working directory: /workspace/.agents"
echo ""

# Agent ID persistence logic
AGENT_ID_FILE="/workspace/output/last_agent_id.txt"
RESUME_AGENT_ID="${RESUME_AGENT_ID:-}"

# Determine if we should resume
if [ -n "$RESUME_AGENT_ID" ]; then
    # Agent ID passed as environment variable
    echo "[INFO] RESUMING agent ID from environment: $RESUME_AGENT_ID"
    AGENT_TO_RESUME="$RESUME_AGENT_ID"
elif [ -f "$AGENT_ID_FILE" ]; then
    # Agent ID from previous run
    AGENT_TO_RESUME=$(cat "$AGENT_ID_FILE")
    echo "[INFO] RESUMING agent ID from previous run: $AGENT_TO_RESUME"
else
    # Fresh start
    echo "[INFO] Starting FRESH (no previous agent ID found)"
    AGENT_TO_RESUME=""
fi

# Determine the prompt to use (priority: CLAUDE_PROMPT > PROMPT_FILE > default)
PROMPT_FILE="${PROMPT_FILE:-MASTER_PROMPT.md}"
CLAUDE_PROMPT="${CLAUDE_PROMPT:-}"

if [ -n "$CLAUDE_PROMPT" ]; then
    echo "[INFO] Using prompt from CLAUDE_PROMPT environment variable"
    PROMPT_TO_USE="$CLAUDE_PROMPT"
elif [ -f "/workspace/.agents/$PROMPT_FILE" ]; then
    echo "[INFO] Using prompt from file: $PROMPT_FILE"
    PROMPT_TO_USE=$(cat "/workspace/.agents/$PROMPT_FILE")
else
    echo "[ERROR] Prompt file not found: $PROMPT_FILE"
    exit 1
fi

echo "=========================================="
echo ""

# Change to .agents directory
cd /workspace/.agents

# Run Claude Code with or without resume
if [ -n "$AGENT_TO_RESUME" ]; then
    echo "[INFO] Running in RESUME mode with agent ID: $AGENT_TO_RESUME"
    echo "[INFO] Agent will continue from previous context"
    echo ""

    # Resume with the agent ID
    # For resume, use a generic continuation prompt unless CLAUDE_PROMPT is specified
    if [ -n "$CLAUDE_PROMPT" ]; then
        echo "[INFO] Using custom resume prompt"
        RESUME_PROMPT="$CLAUDE_PROMPT"
    else
        echo "[INFO] Using default resume prompt"
        RESUME_PROMPT="Continue from where we left off. Process any remaining PROMPT.md files that haven't been completed yet."
    fi

    claude -p "$RESUME_PROMPT" \
          --resume "$AGENT_TO_RESUME" \
          --dangerously-skip-permissions \
          2>&1 | tee /workspace/output/execution.log
else
    echo "[INFO] Running in FRESH mode (first execution)"
    echo "[INFO] Prompt source: ${CLAUDE_PROMPT:+environment variable}${CLAUDE_PROMPT:-file: $PROMPT_FILE}"
    echo ""

    # Fresh start with the determined prompt
    claude -p "$PROMPT_TO_USE" \
          --dangerously-skip-permissions \
          2>&1 | tee /workspace/output/execution.log
fi

CLAUDE_EXIT_CODE=${PIPESTATUS[0]}

# Extract and save agent ID from the output
# Claude Code prints: "agentId: <id>" when a subagent completes
if [ $CLAUDE_EXIT_CODE -eq 0 ]; then
    echo ""
    echo "[INFO] Attempting to extract agent ID from execution log..."

    # Try multiple patterns to find agent ID
    # Pattern 1: "agentId: abc123"
    AGENT_ID=$(grep -oP 'agentId:\s*\K[a-zA-Z0-9]+' /workspace/output/execution.log | tail -1)

    # Pattern 2: "agent ID: abc123" or "Agent ID: abc123"
    if [ -z "$AGENT_ID" ]; then
        AGENT_ID=$(grep -ioP 'agent\s+id:\s*\K[a-zA-Z0-9]+' /workspace/output/execution.log | tail -1)
    fi

    # Pattern 3: Look for agent transcript files that were created
    # Check claude-user's transcript directory (since we run as claude-user)
    if [ -z "$AGENT_ID" ]; then
        echo "[DEBUG] Checking for transcript files in /home/claude-user/.claude/transcripts/"
        ls -la /home/claude-user/.claude/transcripts/ 2>/dev/null || echo "[DEBUG] Transcript directory empty or doesn't exist"

        TRANSCRIPT_FILE=$(ls -t /home/claude-user/.claude/transcripts/agent-*.jsonl 2>/dev/null | head -1)
        if [ -n "$TRANSCRIPT_FILE" ]; then
            AGENT_ID=$(basename "$TRANSCRIPT_FILE" | sed 's/agent-\(.*\)\.jsonl/\1/')
            echo "[DEBUG] Found transcript file: $TRANSCRIPT_FILE"
            echo "[DEBUG] Extracted agent ID: $AGENT_ID"
        else
            echo "[DEBUG] No transcript files found"
        fi
    fi

    # Copy transcripts from claude-user to root (for volume mount persistence)
    if [ -d /home/claude-user/.claude/transcripts ]; then
        TRANSCRIPT_COUNT=$(ls -1 /home/claude-user/.claude/transcripts/agent-*.jsonl 2>/dev/null | wc -l)
        if [ "$TRANSCRIPT_COUNT" -gt 0 ]; then
            echo "[INFO] Copying $TRANSCRIPT_COUNT agent transcript(s) for persistence..."
            cp -f /home/claude-user/.claude/transcripts/agent-*.jsonl /root/.claude/transcripts/ 2>/dev/null || true
        fi
    fi

    if [ -n "$AGENT_ID" ]; then
        echo "$AGENT_ID" > "$AGENT_ID_FILE"
        echo ""
        echo "[SUCCESS] Agent ID saved for future resumption: $AGENT_ID"
        echo "[INFO] Transcript location: /root/.claude/transcripts/agent-$AGENT_ID.jsonl"
        echo "[INFO] To resume this session, run: RESUME_AGENT_ID=$AGENT_ID docker compose up"
        echo "[INFO] Or simply run 'docker compose up' again (auto-resume enabled)"
    else
        echo "[WARN] Could not extract agent ID from execution log"
        echo "[WARN] Resumability will not be available for this run"
        echo "[INFO] This may happen if no subagent was invoked"
        echo "[INFO] Check execution log: cat output/execution.log"
    fi
fi

exit $CLAUDE_EXIT_CODE
EOFSCRIPT

chmod +x /tmp/run_claude.sh

# Run the script as claude-user
su - claude-user -c "bash /tmp/run_claude.sh"

exit_code=${PIPESTATUS[0]}

echo ""
echo "=========================================="

if [ $exit_code -eq 0 ]; then
    echo "[SUCCESS] Code generation completed!"
else
    echo "[ERROR] Code generation failed with exit code: $exit_code"
fi

echo ""
echo "Generated files are in: /workspace/.agents/"
echo "Execution log saved to: /workspace/output/execution.log"
echo ""

# Show summary of generated files (excluding PROMPT.md files)
echo "Summary of generated files:"
find /workspace/.agents -type f ! -name "PROMPT.md" ! -name "MASTER_PROMPT.md" | while read file; do
    echo "  ✓ $file"
done

echo ""
echo "Container exiting..."
exit $exit_code
