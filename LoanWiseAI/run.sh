#!/usr/bin/env bash
# =============================================================================
# LoanWise AI — one-command launcher (macOS / Linux)
#
# Usage:
#   ./run.sh              Set up (first run only) and start the app
#   ./run.sh --retrain    Retrain the model before starting
#   ./run.sh --test       Run the test suite and exit
#   ./run.sh --help       Show this help
#
# Environment overrides:
#   LOANWISE_PORT   Port to serve on (default: 5000, falls back to 8000 if busy)
#   LOANWISE_HOST   Host to bind     (default: 127.0.0.1)
#   PYTHON          Python interpreter to use (default: python3)
# =============================================================================
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

VENV_DIR="$ROOT_DIR/.venv"
PYTHON="${PYTHON:-python3}"
MODEL_FILE="$ROOT_DIR/artifacts/models/loan_model.pkl"
FRONTEND_DIST="$ROOT_DIR/frontend/dist/index.html"
STAMP_FILE="$VENV_DIR/.requirements.sha"

# --- pretty output -----------------------------------------------------------
if [[ -t 1 ]]; then
  BOLD=$'\033[1m'; GREEN=$'\033[32m'; YELLOW=$'\033[33m'; RED=$'\033[31m'; RESET=$'\033[0m'
else
  BOLD=""; GREEN=""; YELLOW=""; RED=""; RESET=""
fi
step() { printf '%s==>%s %s\n' "$BOLD$GREEN" "$RESET" "$*"; }
warn() { printf '%s!!%s  %s\n' "$BOLD$YELLOW" "$RESET" "$*"; }
die()  { printf '%sxx%s  %s\n' "$BOLD$RED" "$RESET" "$*" >&2; exit 1; }

usage() { sed -n '2,16p' "$0" | sed 's/^# \{0,1\}//'; }

# --- arguments ---------------------------------------------------------------
RETRAIN=0; RUN_TESTS=0
for arg in "$@"; do
  case "$arg" in
    --retrain) RETRAIN=1 ;;
    --test)    RUN_TESTS=1 ;;
    -h|--help) usage; exit 0 ;;
    *) die "Unknown option: $arg (try --help)" ;;
  esac
done

# --- 1. Python ---------------------------------------------------------------
command -v "$PYTHON" >/dev/null 2>&1 \
  || die "Python 3 is not installed. Install Python 3.10+ from https://www.python.org/downloads/ and try again."
"$PYTHON" - <<'EOF' || die "Python 3.10 or newer is required."
import sys
sys.exit(0 if sys.version_info >= (3, 10) else 1)
EOF

# --- 2. Virtual environment + dependencies ----------------------------------
if [[ ! -x "$VENV_DIR/bin/python" ]]; then
  step "Creating virtual environment in .venv (first run only)"
  "$PYTHON" -m venv "$VENV_DIR"
fi
VPY="$VENV_DIR/bin/python"

REQ_HASH="$(cat requirements.txt pyproject.toml 2>/dev/null | shasum | awk '{print $1}')"
if [[ ! -f "$STAMP_FILE" || "$(cat "$STAMP_FILE")" != "$REQ_HASH" ]]; then
  step "Installing Python dependencies"
  "$VPY" -m pip install --quiet --upgrade pip
  "$VPY" -m pip install --quiet setuptools wheel
  "$VPY" -m pip install --quiet -r requirements.txt
  "$VPY" -m pip install --quiet -e . --no-deps --no-build-isolation
  echo "$REQ_HASH" > "$STAMP_FILE"
fi

# --- 3. Tests (optional) -----------------------------------------------------
if [[ $RUN_TESTS -eq 1 ]]; then
  step "Running tests"
  exec "$VPY" -m unittest discover -s tests -t . -v
fi

# --- 4. Model ----------------------------------------------------------------
if [[ $RETRAIN -eq 1 || ! -f "$MODEL_FILE" ]]; then
  step "Training the model (about a minute)"
  "$VPY" scripts/train_model.py
fi

# --- 5. Frontend -------------------------------------------------------------
NEED_FRONTEND_BUILD=0
if [[ ! -f "$FRONTEND_DIST" ]]; then
  NEED_FRONTEND_BUILD=1
elif [[ $(find frontend/src -type f -newer "$FRONTEND_DIST" 2>/dev/null | wc -l) -gt 0 ]]; then
  NEED_FRONTEND_BUILD=1
fi

if [[ $NEED_FRONTEND_BUILD -eq 1 ]]; then
  if command -v npm >/dev/null 2>&1; then
    step "Building the frontend"
    (cd frontend && npm install --no-audit --no-fund && npm run build)
  else
    warn "frontend/dist is missing and npm is not installed. The API will run, but the website won't."
    warn "Install Node.js 18+ from https://nodejs.org and run ./run.sh again."
  fi
fi

# --- 6. Pick a free port -----------------------------------------------------
# Uses the same check as the server itself (bind + loopback listener probe, IPv4/IPv6)
port_busy() {
  PYTHONPATH="$ROOT_DIR/src" "$VPY" -c "
import sys
from loanwise.api.dev_server import _is_port_available
sys.exit(1 if _is_port_available(sys.argv[1], int(sys.argv[2])) else 0)
" "${LOANWISE_HOST:-127.0.0.1}" "$1" 2>/dev/null
}

server_up() {
  "$VPY" -c "
import socket, sys
s = socket.socket()
s.settimeout(0.3)
res = s.connect_ex(('127.0.0.1', int(sys.argv[1])))
s.close()
sys.exit(0 if res == 0 else 1)
" "$1" 2>/dev/null
}

export LOANWISE_HOST="${LOANWISE_HOST:-127.0.0.1}"
if [[ -z "${LOANWISE_PORT:-}" ]]; then
  LOANWISE_PORT=5000
  if port_busy 5000; then
    warn "Port 5000 is in use (on a Mac this is usually AirPlay Receiver). Using 8000 instead."
    LOANWISE_PORT=8000
  fi
fi
export LOANWISE_PORT
if port_busy "$LOANWISE_PORT"; then
  warn "Port $LOANWISE_PORT is in use. Using 8080 instead."
  LOANWISE_PORT=8080
fi

URL="http://$LOANWISE_HOST:$LOANWISE_PORT"

# --- 7. Open browser once the server is up ----------------------------------
(
  for _ in $(seq 1 40); do
    if server_up "$LOANWISE_PORT"; then
      if command -v open >/dev/null 2>&1; then open "$URL"
      elif command -v xdg-open >/dev/null 2>&1; then xdg-open "$URL" >/dev/null 2>&1
      fi
      exit 0
    fi
    sleep 0.5
  done
) &

# --- 8. Run ------------------------------------------------------------------
step "Starting LoanWise AI at ${BOLD}$URL${RESET}  (press Ctrl+C to stop)"
exec "$VPY" scripts/run_server.py
