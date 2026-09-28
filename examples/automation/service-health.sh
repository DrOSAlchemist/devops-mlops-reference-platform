#!/usr/bin/env bash
set -euo pipefail

url="${1:-http://127.0.0.1:8080/health}"
status="$(curl --silent --show-error --output /dev/null --write-out '%{http_code}' --max-time 5 "$url")"
printf 'url=%s status=%s\n' "$url" "$status"
[[ "$status" =~ ^2[0-9][0-9]$ ]]