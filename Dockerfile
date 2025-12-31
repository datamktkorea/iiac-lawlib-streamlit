FROM python:3.11-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install git for git dependencies
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependency files first for caching
COPY pyproject.toml uv.lock ./

# Install dependencies
# --frozen: ensure we use the exact versions from uv.lock
# --no-dev: do not install development dependencies
COPY packages ./packages
RUN uv sync --frozen --no-dev

# Add .venv/bin to PATH
ENV PATH="/app/.venv/bin:$PATH"

COPY . .

EXPOSE 8501

ENTRYPOINT ["streamlit", "run", "app/main.py", "--server.port=8501", "--server.address=0.0.0.0"]
