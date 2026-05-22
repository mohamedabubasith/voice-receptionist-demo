FROM python:3.12-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Install deps first (cached layer)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Copy source
COPY . .

# Token counter persists here — mount a volume to /app/data in Coolify
ENV TOKEN_COUNTER_DIR=/app/data
RUN mkdir -p /app/data

CMD ["uv", "run", "python", "agent.py", "start"]
