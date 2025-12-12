#!/usr/bin/env bash
set -euo pipefail

# Go to repo root
cd "$(dirname "$0")/.."

# 1. Get AWS account ID from the IAM role / creds configured on this EC2
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# 2. Get Terraform outputs for Redis endpoint & ACM cert
cd terraform/day32_release_topic/envs/dev

export REDIS_ENDPOINT=$(terraform output -raw redis_endpoint)
export ACM_CERT_ARN=$(terraform output -raw acm_certificate_arn)

# Optional: debug print
echo "AWS_ACCOUNT_ID=${AWS_ACCOUNT_ID}"
echo "REDIS_ENDPOINT=${REDIS_ENDPOINT}"
echo "ACM_CERT_ARN=${ACM_CERT_ARN}"

# 3. Update kubeconfig using EKS cluster from Terraform
export EKS_CLUSTER_NAME=$(terraform output -raw eks_cluster_name)
aws eks update-kubeconfig --name "$EKS_CLUSTER_NAME" --region ap-south-1

# 4. Apply templated manifests using envsubst
cd ../../../..

# Namespace + config first
envsubst < k8s/base/namespace.yaml     | kubectl apply -f -
envsubst < k8s/base/app-configmap.yaml | kubectl apply -f -

# Workloads
envsubst < k8s/base/api-deployment.yaml          | kubectl apply -f -
envsubst < k8s/base/model-service-deployment.yaml | kubectl apply -f -
envsubst < k8s/base/ui-deployment.yaml           | kubectl apply -f -

# Ingress (after ACM exists)
envsubst < k8s/base/ingress.yaml | kubectl apply -f -

# 5. Check status
kubectl get pods -n d32-release-dev
kubectl get svc -n d32-release-dev
kubectl get ingress -n d32-release-dev
