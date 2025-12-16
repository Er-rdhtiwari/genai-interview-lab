#!/usr/bin/env bash
set -euo pipefail
NAMESPACE="${NAMESPACE:-d33-oss-prod}"

kubectl get ns "$NAMESPACE"
kubectl get deploy,po,svc,ing -n "$NAMESPACE" -o wide || true

echo
echo "Describe ingress (if exists):"
kubectl get ing -n "$NAMESPACE" >/dev/null 2>&1 && kubectl describe ing -n "$NAMESPACE" || echo "No ingress yet (will be added in Phase G)."
