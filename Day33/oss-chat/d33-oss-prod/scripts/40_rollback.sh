#!/usr/bin/env bash
set -euo pipefail
NAMESPACE="${NAMESPACE:-d33-oss-prod}"

# Roll back each release to previous revision

for r in d33-oss-frontend d33-oss-backend d33-oss-model; do
echo "Rolling back $r ..."
helm rollback "$r" -n "$NAMESPACE" || echo "No previous revision for $r"
done

helm ls -n "$NAMESPACE"
