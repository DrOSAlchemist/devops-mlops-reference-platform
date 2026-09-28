#!/usr/bin/env bash
set -euo pipefail

python -m ruff check .
python -m pytest -q
python -m bandit -q -r src/platform_guard