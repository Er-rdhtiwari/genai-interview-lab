#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

AWS_REGION="ap-south-1"

echo "[*] Ensuring Terraform dev env is applied..."
cd terraform/day32_release_topic/envs/dev
terraform init -input=false
terraform apply -auto-approve

echo "[*] Fetching AWS account ID & ECR URLs..."
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
export ECR_API_REPO=$(terraform output -raw ecr_api_repository_url)
export ECR_MODEL_REPO=$(terraform output -raw ecr_model_service_repository_url)
export ECR_UI_REPO=$(terraform output -raw ecr_ui_repository_url)
export REDIS_ENDPOINT=$(terraform output -raw redis_endpoint)
export ACM_CERT_ARN=$(terraform output -raw acm_certificate_arn)
export EKS_CLUSTER_NAME=$(terraform output -raw eks_cluster_name)

echo "AWS_ACCOUNT_ID=${AWS_ACCOUNT_ID}"
echo "ECR_API_REPO=${ECR_API_REPO}"
echo "ECR_MODEL_REPO=${ECR_MODEL_REPO}"
echo "ECR_UI_REPO=${ECR_UI_REPO}"

echo "[*] Updating kubeconfig for EKS..."
aws eks update-kubeconfig --name "$EKS_CLUSTER_NAME" --region "$AWS_REGION"

echo "[*] Logging into ECR..."
aws ecr get-login-password --region "$AWS_REGION" \
  | docker login --username AWS --password-stdin "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"

cd "$REPO_ROOT"

echo "[*] Building Docker images..."
docker build -f Dockerfile.api   -t d32-api:dev           .
docker build -f Dockerfile.model -t d32-model-service:dev .
docker build -f Dockerfile.ui    -t d32-ui:dev            .

echo "[*] Tagging & pushing to ECR..."
docker tag d32-api:dev           "${ECR_API_REPO}:dev"
docker tag d32-model-service:dev "${ECR_MODEL_REPO}:dev"
docker tag d32-ui:dev            "${ECR_UI_REPO}:dev"

docker push "${ECR_API_REPO}:dev"
docker push "${ECR_MODEL_REPO}:dev"
docker push "${ECR_UI_REPO}:dev"

echo "[*] Applying Kubernetes manifests..."
envsubst < k8s/base/namespace.yaml           | kubectl apply -f -
envsubst < k8s/base/app-configmap.yaml       | kubectl apply -f -
envsubst < k8s/base/api-deployment.yaml      | kubectl apply -f -
envsubst < k8s/base/model-service-deployment.yaml | kubectl apply -f -
envsubst < k8s/base/ui-deployment.yaml       | kubectl apply -f -
envsubst < k8s/base/ingress.yaml             | kubectl apply -f -

echo "[*] Current status:"
kubectl get pods -n d32-release-dev
kubectl get svc -n d32-release-dev
kubectl get ingress -n d32-release-dev

echo "[✓] Build + Push + Deploy completed."
