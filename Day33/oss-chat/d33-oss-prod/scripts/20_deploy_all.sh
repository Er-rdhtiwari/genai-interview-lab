#!/usr/bin/env bash
set -euo pipefail
NAMESPACE="${NAMESPACE:-d33-oss-prod}"

# Deploy order: model -> backend -> frontend (ingress comes with charts later)

helm upgrade --install d33-oss-model ./charts/model-service 
-n "$NAMESPACE" 
-f values/dev/model.yaml

helm upgrade --install d33-oss-backend ./charts/rag-backend 
-n "$NAMESPACE" 
-f values/dev/backend.yaml

helm upgrade --install d33-oss-frontend ./charts/chat-frontend 
-n "$NAMESPACE" 
-f values/dev/frontend.yaml

echo "Helm releases:"
helm ls -n "$NAMESPACE"
