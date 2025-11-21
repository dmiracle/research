# Use Ubuntu 24.04 (Noble Numbat) as the base image
FROM ubuntu:24.04

# Set environment to non-interactive to avoid prompts during build
ENV DEBIAN_FRONTEND=noninteractive

# 1. Install system dependencies
# - curl, git: required for uv and nvm
# - build-essential, libssl-dev: often needed for building python/node extensions
RUN apt-get update && apt-get install -y \
    curl \
    git \
    ca-certificates \
    unzip \
    build-essential \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# -----------------------------------------------------------------------------
# 2. Install uv and Python versions
# -----------------------------------------------------------------------------

# Copy uv binary from the official image (Best Practice)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Configure uv to install Python versions
# Python 3.13 is the current stable; 3.14 is the preview/dev version.
# uv handles the downloading and management of these specific versions.
RUN uv python install 3.13 3.14

# -----------------------------------------------------------------------------
# 3. Install NVM and Node.js (LTS)
# -----------------------------------------------------------------------------

# Set NVM environment variables
ENV NVM_DIR="/usr/local/nvm"
ENV NVM_VERSION="0.40.1"

# Create the directory for NVM
RUN mkdir -p "$NVM_DIR"

# Install NVM
RUN curl -o- "https://raw.githubusercontent.com/nvm-sh/nvm/v${NVM_VERSION}/install.sh" | bash

# Install the latest LTS version of Node.js
# We define a shell alias/symlink strategy here so 'node' and 'npm' are available
# globally without having to source nvm.sh in every subsequent RUN instruction.
RUN . "$NVM_DIR/nvm.sh" && \
    nvm install --lts && \
    nvm use --lts && \
    nvm alias default lts/* && \
    # Create symlinks to /usr/local/bin for global availability
    ln -s "$(nvm which current)" /usr/local/bin/node && \
    ln -s "$(nvm which current | sed 's/bin\/node/bin\/npm/')" /usr/local/bin/npm && \
    ln -s "$(nvm which current | sed 's/bin\/node/bin\/npx/')" /usr/local/bin/npx

# -----------------------------------------------------------------------------
# 4. Verification & Placeholders
# -----------------------------------------------------------------------------

# Verify installations
RUN echo "--- Environment Versions ---" && \
    uv --version && \
    echo "Managed Python Versions:" && uv python list && \
    echo "Node Version:" && node --version && \
    echo "NPM Version:" && npm --version

# [PLACEHOLDER] Additional NPM Global Installs
# Example: RUN npm install -g typescript yarn pnpm
RUN npm install -g @openai/codex @anthropic-ai/claude-code && \
    ln -s "$(npm prefix -g)/bin/claude" /usr/local/bin/claude && \
    ln -s "$(npm prefix -g)/bin/codex" /usr/local/bin/codex
# [PLACEHOLDER] Project Setup
# Example:
# WORKDIR /app
# COPY package.json package-lock.json ./
# RUN npm install
# COPY . .

# Default command
CMD ["/bin/bash"]

# -----------------------------------------------------------------------------
# 5. User Setup & Final Configuration
# -----------------------------------------------------------------------------

# Create a non-root user 'appuser'
RUN groupadd -r appuser && useradd -r -g appuser -s /bin/bash -m appuser

# Add aliases to appuser's .bashrc
RUN echo "alias clauded='claude update && claude --dangerously-skip-permissions'" >> /home/appuser/.bashrc && \
    echo "alias codexed='codex update && codex --dangerously-bypass-approvals-and-sandbox'" >> /home/appuser/.bashrc

# Ensure appuser owns the home directory (already done by -m but good to be sure if we copy things)
# and any other necessary directories.
# If we were to create /app, we should do it here and chown it.
RUN mkdir -p /app && chown appuser:appuser /app

# Create mount points for .claude and .codex to ensure ownership
RUN mkdir -p /home/appuser/.claude /home/appuser/.codex && \
    chown -R appuser:appuser /home/appuser/.claude /home/appuser/.codex

# Switch to non-root user
USER appuser
WORKDIR /app