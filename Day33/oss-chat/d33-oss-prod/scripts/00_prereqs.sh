#!/usr/bin/env bash
set -euo pipefail

echo "Checking tools..."
for bin in kubectl helm aws; do
command -v "$bin" >/dev/null 2>&1 || { echo "Missing: $bin"; exit 1; }
done

echo "kubectl:"; kubectl version --client --short || true
echo "helm:"; helm version --short || true
echo "aws:"; aws --version || true

echo "OK."
