# syntax=docker/dockerfile:1

# Two stages: Node builds the React app from source, then a slim Python image serves it.
# The host (e.g. Render) runs this on every deploy, so frontend/dist never needs committing.

# ---- Stage 1: build the React frontend ---------------------------------------
FROM node:22-slim AS frontend
WORKDIR /build/frontend
COPY frontend/package.json ./
# --legacy-peer-deps: framer-motion 11 and lucide-react list React 18 as their peer,
# but work with the React 19 this app uses. Without it npm stops with ERESOLVE.
RUN npm install --no-audit --no-fund --legacy-peer-deps
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
    CMD python -c "import urllib.request,os; port=os.environ.get('PORT') or os.environ['LOANWISE_PORT']; urllib.request.urlopen(f'http://127.0.0.1:{port}/api/health', timeout=2)"

# Hosts such as Render set PORT; otherwise LOANWISE_PORT (5000) is used.
# One worker with threads fits small (512 MB) instances; raise GUNICORN_WORKERS on bigger ones.
CMD ["sh", "-c", "exec gunicorn --bind 0.0.0.0:${PORT:-${LOANWISE_PORT}} --workers ${GUNICORN_WORKERS:-1} --threads ${GUNICORN_THREADS:-4} --timeout 60 --access-logfile - wsgi:app"]