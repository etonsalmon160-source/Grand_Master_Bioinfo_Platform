#!/usr/bin/env bash
set -euo pipefail

# Deployment helper for OpenClaw (Python-first) to GHCR and PyPI
#  - Tokens/credentials should be provided via environment variables or CI secrets
#  - This script is designed for CI or controlled environments, not exposed in repo

# Required inputs (env vars or defaults)
VERSION=${VERSION:-v0.1.0}
GHCR_REPO=${GHCR_REPO:-ghcr.io/your-org/openclaw-python}
GHCR_USERNAME=${GHCR_USERNAME:-${USER:-}}
GHCR_TOKEN=${GHCR_TOKEN:-}
PYPI_TEST_TOKEN=${PYPI_TEST_API_TOKEN:-}
PYPI_TOKEN=${PYPI_API_TOKEN:-}
DOCKERFILE=${DOCKERFILE_PYTHON:-Dockerfile.python}

echo "== OpenClaw Deploy: v=${VERSION} =="

# 1) Build wheel/sdist
echo "[Step 1] Build Python distributions..."
python -m pip install --upgrade pip build
python -m build

# 2) Upload to Test PyPI (if token provided)
if [ -n "$PYPI_TEST_TOKEN" ]; then
  echo "[Step 2] Upload to Test PyPI..."
  python -m pip install --upgrade pip setuptools wheel twine
  twine upload dist/* --repository-url https://test.pypi.org/legacy/ -u __token__ -p "$PYPI_TEST_TOKEN" || true
else
  echo "[Step 2] No Test PyPI token provided, skipping."
fi

# 3) Upload to Production PyPI (if token provided)
if [ -n "$PYPI_TOKEN" ]; then
  echo "[Step 3] Upload to PyPI Production..."
  python -m pip install --upgrade pip setuptools wheel twine
  twine upload dist/* --repository-url https://upload.pypi.org/legacy/ -u __token__ -p "$PYPI_TOKEN" || true
else
  echo "[Step 3] No Production PyPI token provided, skipping."
fi

# 4) Build and push GHCR image
if [ -n "$GHCR_TOKEN" ] && [ -n "$GHCR_USERNAME" ]; then
  echo "[Step 4] Login to GHCR..."
  echo "$GHCR_TOKEN" | docker login ghcr.io -u "$GHCR_USERNAME" --password-stdin
fi
echo "[Step 5] Build and push GHCR image..."
docker build -f "$DOCKERFILE" -t "$GHCR_REPO:$VERSION" .
docker push "$GHCR_REPO:$VERSION"

echo "Deployment finished. Image: $GHCR_REPO:$VERSION"
echo "Note: If you are running this locally, ensure Docker is running and you have permission to push to GHCR."
