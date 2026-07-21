#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

docker compose ps

printf '\nPrometheus readiness:\n'
curl -fsS http://localhost:9090/-/ready
printf '\n'

printf '\nGrafana health:\n'
curl -fsS http://localhost:3000/api/health
printf '\n'
