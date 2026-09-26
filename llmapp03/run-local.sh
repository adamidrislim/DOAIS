#!/bin/bash
set -euo pipefail
APP_DIR="$(cd "$(dirname "$0")" && pwd)"
PYTHON="$APP_DIR/.venv/bin/python"
if [ -z "${OLLAMA_API_KEY:-}" ]; then
  read -r -s -p "Ollama API key: " OLLAMA_API_KEY
  echo
fi
if [ -z "$OLLAMA_API_KEY" ]; then
  echo "An Ollama API key is required."
  exit 1
fi
export OLLAMA_API_KEY
export OLLAMA_BASE_URL="https://ollama.com"
export BACKEND_URL="http://127.0.0.1:8082"
export PYTHONDONTWRITEBYTECODE=1
backend_pid=""
frontend_pid=""
cleanup() {
  [ -z "$frontend_pid" ] || kill "$frontend_pid" 2>/dev/null || true
  [ -z "$backend_pid" ] || kill "$backend_pid" 2>/dev/null || true
}
trap cleanup EXIT
trap 'exit 130' INT TERM
cd "$APP_DIR/llm-multiroute"
"$PYTHON" -m uvicorn app.main:app --host 127.0.0.1 --port 8082 &
backend_pid=$!
unset OLLAMA_API_KEY
cd "$APP_DIR/llm-frontend-python"
"$PYTHON" -m flask --app app run --host 127.0.0.1 --port 5004 --no-debugger --no-reload &
frontend_pid=$!
echo "App: http://127.0.0.1:5004   API docs: http://127.0.0.1:8082/swagger-ui.html"
echo "Press Ctrl+C to stop both app services."
while kill -0 "$backend_pid" 2>/dev/null && kill -0 "$frontend_pid" 2>/dev/null; do
  sleep 1
done
exit 1
