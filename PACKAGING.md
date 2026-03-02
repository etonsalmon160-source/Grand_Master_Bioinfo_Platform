- Packaging Guide (Python-first)
==============================
- Core focus: OpenClaw Python entry points; launcher prioritizes Python first to preserve科研 workflows.
- Primary Python entry path:
  - If openclaw/__main__.py exists, use python -m openclaw
  - Else, fall back to main.py or app.py
- Container strategy: use Dockerfile.python for a Python-only container with launcher.sh as the entry point
- CI strategy: Python CI workflow builds wheels and can publish to PyPI (token-based uploads)
- Back-compat: a multi-language Dockerfile remains as a fallback for mixed-language repos
- Usage:
  - Build Python-only image: docker build -f Dockerfile.python -t myapp-python:latest .
  - Run: docker run --rm -p 8080:8080 myapp-python:latest
- Launcher override: APP_ENTRY can override default path, e.g. APP_ENTRY="python3 -m openclaw".

OpenClaw API docs
- See docs/openclaw_api.md for a skeleton API/documentation plan.

Next steps
- Fill docs/openclaw_api.md with actual interface details.
- Optional: tighten launcher.sh to a fully bound OpenClaw entry point (Option A refinement).
- PyPI Release Strategy:
  - Test PyPI: use PYPI_TEST_API_TOKEN in CI Secrets to upload a wheel/sdist for testing
  - Production: when tokens are available, publish to PyPI using PYPI_API_TOKEN
