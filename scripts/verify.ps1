$ErrorActionPreference = "Stop"

python -m ruff check .
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

python -m pytest -q
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

python -m bandit -q -r src/platform_guard
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }