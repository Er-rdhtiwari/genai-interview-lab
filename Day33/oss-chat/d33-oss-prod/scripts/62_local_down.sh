#!/usr/bin/env bash
set -euo pipefail
docker compose -f docker-compose.local.yaml down
echo "Stopped."
