#!/usr/bin/env bash
set -euo pipefail

APP_ENTRY="${APP_ENTRY:-}"
echo "Launcher: detecting project type..."

run_and_exit() {
  "$@"
  exit $?
}

# 1) Explicit launcher override
if [ -n "$APP_ENTRY" ]; then
  echo "Launching via APP_ENTRY: $APP_ENTRY"
  run_and_exit bash -lc "$APP_ENTRY" "$@"
fi

## Python-first for Python projects (preserve openclaw and py-based entrypoints)
if [ -f "pyproject.toml" ] || [ -f "setup.py" ]; then
  # Try OpenClaw first if available
  if [ -d "openclaw" ] && [ -f "openclaw/__main__.py" ]; then
    echo "Running Python entrypoint: openclaw (python -m openclaw)"
    if python3 -m openclaw "$@"; then
      exit 0
    else
      echo "openclaw entrypoint failed; continuing..."
    fi
  fi
  # Fallback to common Python entrypoints
  if [ -f "main.py" ]; then
    echo "Running Python entrypoint: main.py"
    if python3 main.py "$@"; then
      exit 0
    else
      echo "main.py failed; continuing..."
    fi
  fi
  if [ -f "app.py" ]; then
    echo "Running Python entrypoint: app.py"
    if python3 app.py "$@"; then
      exit 0
    else
      echo "app.py failed; continuing..."
    fi
  fi
  # If a standalone OpenClaw UI is present, try launching it directly (streamlit-based UI)
  if [ -f "openclaw_app.py" ]; then
    echo "Detected openclaw_app.py; attempting to launch UI via streamlit..."
    if command -v streamlit >/dev/null 2>&1; then
      streamlit run openclaw_app.py --server.port=8501
      exit $?
    else
      echo "Streamlit not found; trying to run Python entry directly..."
      if python3 openclaw_app.py; then
        exit 0
      fi
    fi
  fi
  if [ -f "openclaw_exe_entry.py" ]; then
    echo "Detected openclaw_exe_entry.py; attempting to launch UI wrapper..."
    if python3 openclaw_exe_entry.py; then
      exit 0
    fi
  fi
  echo "No Python entrypoint succeeded; continuing to Node/Go paths..."
fi

echo "No Python entrypoint found; trying to launch OpenClaw UI if present..."
## Try OpenClaw UI entry points directly (unconditionally)
if [ -f "openclaw_app.py" ]; then
  echo "Detected openclaw_app.py; attempting to launch UI via streamlit..."
  if command -v streamlit >/dev/null 2>&1; then
    streamlit run openclaw_app.py --server.port=8501
    exit $?
  else
    echo "Streamlit not found; trying to run Python entry directly..."
    if python3 openclaw_app.py; then
      exit 0
    fi
  fi
fi
if [ -f "openclaw_exe_entry.py" ]; then
  echo "Detected openclaw_exe_entry.py; attempting to launch UI wrapper..."
  if command -v streamlit >/dev/null 2>&1; then
    streamlit run openclaw_exe_entry.py --server.port=8501
    exit $?
  else
    if python3 openclaw_exe_entry.py; then
      exit 0
    fi
  fi
fi
## fall through to Node/Go/Makefile paths

## Node.js
if [ -f "package.json" ]; then
  if grep -q '"start"' package.json || grep -q '\"start\"' package.json; then
    echo "Starting via npm start..."
    npm run start "$@"
    exit $?
  else
    if [ -f "index.js" ]; then
      echo "Running Node.js entrypoint: index.js"
      node index.js "$@"
      exit $?
    elif [ -f "dist/index.js" ]; then
      echo "Running Node.js entrypoint: dist/index.js"
      node dist/index.js "$@"
      exit $?
    fi
  fi
  echo "No suitable Node entrypoint found."
fi

## Python (existing module/tablet entrypoints handled above; this section is intentionally left minimal)

## Go
if [ -f "go.mod" ]; then
  if [ -f "app-bin" ]; then
    echo "Running Go binary: ./app-bin"
    ./app-bin "$@"
    exit $?
  else
    if go build -o app-bin ./...; then
      echo "Running Go binary: ./app-bin"
      ./app-bin "$@"
      exit $?
    else
      echo "Go build failed."
    fi
  fi
fi

## Makefile helpers
if [ -f "Makefile" ]; then
  if make start 2>/dev/null; then exit 0; fi
  if make run 2>/dev/null; then exit 0; fi
fi

echo "No recognizable entrypoint found in this repository."
exit 1
