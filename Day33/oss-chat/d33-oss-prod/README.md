# d33-oss-prod — Production-Grade GenAI OSS PoC (EKS + Helm)
- Namespace: d33-oss-prod
- Frontend: d33-oss-frontend
- Backend: d33-oss-backend
- Model: d33-oss-model (Ollama)
- Domains:
  - https://d33-oss.rdhcloudlab.com
  - https://api.d33-oss.rdhcloudlab.com
## Quick Runbook
### 1) Prereqs
```bash
./scripts/00_prereqs.sh
```

### 2) Create namespace

```bash
make ns
```

### 3) Deploy all (Helm)

```bash
make deploy
```

### 4) Verify

```bash
make verify
```

### 5) Rollback (if needed)

```bash
make rollback
```

### 6) Cleanup

```bash
make cleanup
```

## Notes

* Terraform will create ACM cert in ap-south-1 (currently none).
* Helm will manage app resources (Deployments/Services/Ingress/ConfigMaps/HPA).
* Do not commit secrets.


# Scripts
```
cat > scripts/00_prereqs.sh <<'EOF'
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
EOF
```
```
chmod +x scripts/00_prereqs.sh
```

```
cat > scripts/10_create_namespace.sh <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
NAMESPACE="${NAMESPACE:-d33-oss-prod}"

kubectl get ns "$NAMESPACE" >/dev/null 2>&1 || kubectl create ns "$NAMESPACE"
kubectl get ns "$NAMESPACE"
EOF

```
```
chmod +x scripts/10_create_namespace.sh
```

```
cat > scripts/20_deploy_all.sh <<'EOF'
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
EOF
```
```
chmod +x scripts/20_deploy_all.sh
```

```
cat > scripts/30_verify.sh <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
NAMESPACE="${NAMESPACE:-d33-oss-prod}"

kubectl get ns "$NAMESPACE"
kubectl get deploy,po,svc,ing -n "$NAMESPACE" -o wide || true

echo
echo "Describe ingress (if exists):"
kubectl get ing -n "$NAMESPACE" >/dev/null 2>&1 && kubectl describe ing -n "$NAMESPACE" || echo "No ingress yet (will be added in Phase G)."
EOF
```
```
chmod +x scripts/30_verify.sh
```
```
cat > scripts/40_rollback.sh <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
NAMESPACE="${NAMESPACE:-d33-oss-prod}"

# Roll back each release to previous revision

for r in d33-oss-frontend d33-oss-backend d33-oss-model; do
echo "Rolling back $r ..."
helm rollback "$r" -n "$NAMESPACE" || echo "No previous revision for $r"
done

helm ls -n "$NAMESPACE"
EOF
```
```
chmod +x scripts/40_rollback.sh
```
```
cat > scripts/90_cleanup.sh <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
NAMESPACE="${NAMESPACE:-d33-oss-prod}"

helm uninstall d33-oss-frontend -n "$NAMESPACE" || true
helm uninstall d33-oss-backend -n "$NAMESPACE" || true
helm uninstall d33-oss-model -n "$NAMESPACE" || true

kubectl delete ns "$NAMESPACE" --wait=false || true
echo "Cleanup triggered."
EOF
```
```
chmod +x scripts/90_cleanup.sh
```
# Placeholder app dirs

```
cat > apps/backend/README.md <<'EOF'

# Backend (FastAPI)

Phase C will add source + Dockerfile.
EOF
```
```
cat > apps/frontend/README.md <<'EOF'

# Frontend (Next.js/React)

Phase D will add source + Dockerfile.
EOF
```

# Placeholder Helm charts (skeleton; templates added in later phases)
```
cat > charts/model-service/Chart.yaml <<'EOF'
apiVersion: v2
name: model-service
description: d33-oss-model (Ollama) chart
type: application
version: 0.1.0
appVersion: "1.0"
EOF
```
```
cat > charts/rag-backend/Chart.yaml <<'EOF'
apiVersion: v2
name: rag-backend
description: d33-oss-backend (FastAPI) chart
type: application
version: 0.1.0
appVersion: "1.0"
EOF
```
```

cat > charts/chat-frontend/Chart.yaml <<'EOF'
apiVersion: v2
name: chat-frontend
description: d33-oss-frontend (Next.js) chart
type: application
version: 0.1.0
appVersion: "1.0"
EOF
```

# Values (dev/prod placeholders; we’ll fill real knobs in Phases E/F/G)
```
cat > values/dev/model.yaml <<'EOF'
namespace: d33-oss-prod
image:
repository: ollama/ollama
tag: latest
env:
OLLAMA_HOST: "0.0.0.0:11434"
OLLAMA_MODEL: "llama3.2:3b"
EOF
```
```
cat > values/dev/backend.yaml <<'EOF'
namespace: d33-oss-prod
image:
repository: REPLACE_ME_ECR_BACKEND
tag: dev
env:
OLLAMA_BASE_URL: "[http://d33-oss-model:11434](http://d33-oss-model:11434)"
EOF
```
```
cat > values/dev/frontend.yaml <<'EOF'
namespace: d33-oss-prod
image:
repository: REPLACE_ME_ECR_FRONTEND
tag: dev
env:
NEXT_PUBLIC_API_BASE_URL: "[https://api.d33-oss.rdhcloudlab.com](https://api.d33-oss.rdhcloudlab.com)"
EOF
```
# Prod placeholders
```
cp values/dev/model.yaml values/prod/model.yaml
cp values/dev/backend.yaml values/prod/backend.yaml
cp values/dev/frontend.yaml values/prod/frontend.yaml

echo "Scaffold created."
````

---

## 🧪 Verification commands + expected outputs

```bash
cd d33-oss-prod
./scripts/00_prereqs.sh
````

✅ Expected: prints versions + “OK.”

```bash
find . -maxdepth 3 -type d | sed 's|^\./||' | sort | head
```

✅ Expected: shows `apps/`, `charts/`, `values/`, `scripts/`, `docs/` etc.

(Optional, if you want git now)

```bash
git init
git status
```

✅ Expected: lots of new files staged/unstaged.

---

## 🧯 Common failures + fixes (Phase B)

* **`helm` / `kubectl` not found**

  * Fix: install them on EC2 (we’ll do if you paste the error)
* **Accidentally committing secrets**

  * Fix: keep secrets out; `.gitignore` already blocks common patterns

---

## ✅ Stop here — paste outputs

Check the following :

1. `cd d33-oss-prod && ls -la`
2. `find . -maxdepth 2 -type d | sort`



