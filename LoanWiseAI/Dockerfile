# syntax=docker/dockerfile:1

# ---- Stage 1: build the React frontend ---------------------------------------
FROM node:20-slim AS frontend
WORKDIR /build/frontend
COPY frontend/package*.json ./
RUN npm install --no-audit --no-fund
COPY frontend/ ./
RUN npm run build

# ---- Stage 2: Python runtime --------------------------------------------------
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    LOANWISE_ROOT=/app \
    LOANWISE_LOG_FORMAT=json \
    LOANWISE_PORT=5000

WORKDIR /app

# Dependencies first for better layer caching.
COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY pyproject.toml ./
COPY src/ ./src/
RUN pip install --no-deps .

COPY wsgi.py ./
COPY artifacts/models/ ./artifacts/models/
COPY data/raw/test.csv ./data/raw/test.csv
COPY --from=frontend /build/frontend/dist ./frontend/dist

RUN useradd --system --uid 10001 --home-dir /app loanwise \
    && mkdir -p /app/instance \
    && chown -R loanwise:loanwise /app/instance
USER loanwise

EXPOSE 5000
HEALTHCHECK --interval=30s --timeout=3s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request,os; urllib.request.urlopen(f'http://127.0.0.1:{os.environ[\"LOANWISE_PORT\"]}/api/health', timeout=2)"

CMD ["sh", "-c", "exec gunicorn --bind 0.0.0.0:${LOANWISE_PORT} --workers ${GUNICORN_WORKERS:-2} --access-logfile - wsgi:app"]
