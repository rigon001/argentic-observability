#!/usr/bin/env bash
set -euo pipefail

metrics_url="${VLLM_METRICS_URL:-http://localhost:8001/metrics}"

printf 'vLLM metrics from %s\n\n' "$metrics_url"

curl -fsS "$metrics_url" |
  awk '$1 == "#" && $2 == "TYPE" && $3 ~ /^vllm:/ {
    printf "%-60s %s\n", $3, $4
  }' |
  sort -u
