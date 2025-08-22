#!/usr/bin/env bash
set -euo pipefail

echo ">> Editable install (SDK + dev extras)"
pip install -e ".[dev]"

echo ">> Running mypy"
mypy devnotify

echo ">> Running black (format in place)"
black .

echo ">> Running ruff"
ruff check .

echo ">> Tests with coverage (only src)"
coverage run --source=devnotify -m pytest -q

echo ">> Coverage report (enforce 100%)"
if coverage report --fail-under=100; then
  echo "✅ Coverage is 100%"
else
  echo "❌ Coverage below 100% — generating HTML report..."
  coverage html
  echo "Open: htmlcov/index.html"
  exit 1
fi
