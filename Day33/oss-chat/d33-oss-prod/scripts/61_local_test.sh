#!/usr/bin/env bash
set -euo pipefail

echo "Ollama version:"
curl -s http://localhost:11434/api/version || true
echo

echo "Backend health:"
curl -s http://localhost:8000/healthz
echo
echo "Backend ready:"
curl -s http://localhost:8000/readyz
echo
echo "Backend chat:"
curl -s http://localhost:8000/api/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"hello from phase H"}'
echo
