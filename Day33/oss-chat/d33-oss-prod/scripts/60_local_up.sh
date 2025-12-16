#!/usr/bin/env bash
set -euo pipefail

docker compose -f docker-compose.local.yaml up -d ollama

echo "Waiting for Ollama..."
for i in {1..30}; do
  if curl -s http://localhost:11434/api/version >/dev/null 2>&1; then
    echo "Ollama is up."
    break
  fi
  sleep 1
done

echo "Pulling model (first time can take a while)..."
# NOTE: pulling requires ollama server running :contentReference[oaicite:2]{index=2}
docker compose -f docker-compose.local.yaml exec -T ollama ollama pull llama3.2:3b || true

docker compose -f docker-compose.local.yaml up -d --build backend

echo "Services:"
docker compose -f docker-compose.local.yaml ps
