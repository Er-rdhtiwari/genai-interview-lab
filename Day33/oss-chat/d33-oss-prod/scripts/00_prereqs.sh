cat > scripts/00_prereqs.sh <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

echo "Checking tools..."
for bin in kubectl helm aws; do
  command -v "$bin" >/dev/null 2>&1 || { echo "Missing: $bin"; exit 1; }
done

echo "kubectl:"
# Newer kubectl may not support --short
kubectl version --client=true 2>/dev/null || kubectl version --client 2>/dev/null || true

echo "helm:"
helm version --short 2>/dev/null || helm version || true

echo "aws:"
aws --version || true

echo "kube context (optional):"
kubectl config current-context 2>/dev/null || echo "No kubeconfig context set yet."

echo "OK."
EOF

chmod +x scripts/00_prereqs.sh
./scripts/00_prereqs.sh
