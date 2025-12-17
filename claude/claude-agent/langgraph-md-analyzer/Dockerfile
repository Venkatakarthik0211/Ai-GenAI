FROM node:20-slim

# Install system dependencies including graphviz for pygraphviz
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    jq \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    awscli \
    sudo \
    graphviz \
    graphviz-dev \
    build-essential \
    pkg-config \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Install Claude Code CLI globally
RUN npm install -g @anthropic-ai/claude-code

# Create non-root user for running Claude Code
RUN useradd -m -s /bin/bash claude-user && \
    echo "claude-user ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Set working directory
WORKDIR /workspace

# Copy application files
COPY md_analyzer_agent.py /workspace/md_analyzer_agent.py
COPY bedrock.py /workspace/bedrock.py
COPY requirements.txt /workspace/requirements.txt
COPY entrypoint.sh /entrypoint.sh
COPY config/settings.json /tmp/settings.json

# Install Python dependencies (boto3, botocore for Bedrock + app requirements)
RUN pip3 install --no-cache-dir --break-system-packages boto3 botocore && \
    pip3 install --no-cache-dir --break-system-packages -r /workspace/requirements.txt

# Create directories and set permissions
RUN mkdir -p /workspace/logs /workspace/files && \
    chown -R claude-user:claude-user /workspace && \
    chmod +x /entrypoint.sh

# Switch to non-root user for setup
USER claude-user

# Set up Claude Code home directory
RUN mkdir -p /home/claude-user/.claude

# Switch back to root for entrypoint (will switch to claude-user inside)
USER root

ENTRYPOINT ["/entrypoint.sh"]
