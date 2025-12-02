FROM python:3.11-slim

WORKDIR /app

COPY . .

# Copy dependency files first for caching
COPY pyproject.toml uv.lock ./

# Install dependencies
# --frozen: ensure we use the exact versions from uv.lock
# --no-dev: do not install development dependencies
RUN uv sync --frozen --no-dev

EXPOSE 8501

ENTRYPOINT ["streamlit", "run", "app/main.py", "--server.port=8501", "--server.address=0.0.0.0"]