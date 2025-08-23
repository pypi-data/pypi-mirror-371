# Multi-stage build for efficient image size
FROM python:3.12-slim as builder

# Install uv for fast dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock* ./

# Install dependencies into the system
RUN uv sync --frozen --no-install-project --no-dev --system

# Production stage
FROM python:3.12-slim as production

# Create non-root user for security
RUN groupadd --gid 1000 mcpuser && \
    useradd --uid 1000 --gid mcpuser --shell /bin/bash --create-home mcpuser

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Set working directory
WORKDIR /app

# Copy application code
COPY src/ ./src/
COPY pyproject.toml ./

# Install the package
RUN pip install -e .

# Switch to non-root user
USER mcpuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "from keenmail_mcp.config import KeenMailConfig; KeenMailConfig()" || exit 1

# Default command
CMD ["python", "-m", "keenmail_mcp"]

# Metadata
LABEL org.opencontainers.image.title="KeenMail MCP Server"
LABEL org.opencontainers.image.description="Model Context Protocol server for KeenMail API integration"
LABEL org.opencontainers.image.version="0.1.0"
LABEL org.opencontainers.image.source="https://github.com/yourusername/keenmail-mcp-server"