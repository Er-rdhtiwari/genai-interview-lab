#!/usr/bin/env bash
set -euo pipefail
NAMESPACE="${NAMESPACE:-d33-oss-prod}"

helm uninstall d33-oss-frontend -n "$NAMESPACE" || true
helm uninstall d33-oss-backend -n "$NAMESPACE" || true
helm uninstall d33-oss-model -n "$NAMESPACE" || true

kubectl delete ns "$NAMESPACE" --wait=false || true
echo "Cleanup triggered."
