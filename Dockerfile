FROM python:3.11-slim

# uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# (많이들 여기서 실패) 빌드에 필요한 최소 도구들
RUN apt-get update && apt-get install -y --no-install-recommends \
    git build-essential \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 의존성 파일 먼저(캐시)
COPY pyproject.toml uv.lock ./

# 로컬 패키지 의존성이 있으면, sync 전에 복사되어 있어야 함
COPY packages/local-pykospacing ./packages/local-pykospacing

# deps 설치
RUN uv sync --frozen --no-dev

ENV PATH="/app/.venv/bin:$PATH"

# 앱 소스 복사
COPY . /app

# entrypoint
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

EXPOSE 8501
ENTRYPOINT ["/app/entrypoint.sh"]
