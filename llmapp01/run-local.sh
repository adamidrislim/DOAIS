#!/bin/bash
set -euo pipefail
APP_DIR="$(cd "$(dirname "$0")" && pwd)"
PYTHON="$APP_DIR/.venv/bin/python"
export OLLAMA_MODEL="${OLLAMA_MODEL:-gemma2:2b}"
export BACKEND_URL="http://127.0.0.1:8080"
backend_pid=""
frontend_pid=""
cleanup() {
  [ -z "$frontend_pid" ] || kill "$frontend_pid" 2>/dev/null || true
  [ -z "$backend_pid" ] || kill "$backend_pid" 2>/dev/null || true
}
trap cleanup EXIT
trap 'exit 130' INT TERM
cd "$APP_DIR/llm-python"
"$PYTHON" -m uvicorn app.main:app --host 127.0.0.1 --port 8080 &
backend_pid=$!
cd "$APP_DIR/llm-frontend-python"
"$PYTHON" -m flask --app app run --host 127.0.0.1 --port 5002 --no-debugger --no-reload &
frontend_pid=$!
echo "App: http://127.0.0.1:5002   API docs: http://127.0.0.1:8080/swagger-ui.html"
echo "Press Ctrl+C to stop both app services."
while kill -0 "$backend_pid" 2>/dev/null && kill -0 "$frontend_pid" 2>/dev/null; do
  sleep 1
done
exit 1
