FROM node:20-slim

# Install dependencies in a single layer and clean up
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    jq \
    python3 \
    python3-pip \
    awscli \
    sudo \
    && pip3 install --no-cache-dir --break-system-packages boto3 botocore \
    && npm install -g @anthropic-ai/claude-code \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Create non-root user for running Claude Code
RUN useradd -m -s /bin/bash claude-user && \
    echo "claude-user ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Set working directory
WORKDIR /workspace

# Copy scripts and config
COPY bedrock.py /workspace/bedrock.py
COPY entrypoint.sh /entrypoint.sh
COPY settings.json /tmp/settings.json

# Create directories and set permissions
RUN mkdir -p /workspace/.agents /workspace/output && \
    chown -R claude-user:claude-user /workspace && \
    chmod +x /entrypoint.sh

# Note: entrypoint runs as root to copy AWS creds, then switches to claude-user
ENTRYPOINT ["/entrypoint.sh"]
