# Day32 – GenAI Release PoC on AWS EKS (`d32-release`)

Small but realistic **GenAI PoC** deployed on **AWS EKS** with:

- **FastAPI** backend (`api`)  
- **Model service** (OSS/OpenAI switch)  
- **Streamlit UI** (`ui`) with greeting + birthday logic  
- **Redis** cache (ElastiCache in AWS, `redis://` locally)  
- **EKS** with separate node groups (app vs model)  
- **ALB + ACM + Route 53 + your domain**  
- **Terraform IaC** for all AWS resources

> Dev environment is namespaced as:  
> **PoC ID:** `d32-release` · **Env:** `dev` · **Domain root:** `rdhcloudlab.com`

---

## 1. High-Level Overview

### 1.1 What this PoC does

- Exposes a **FastAPI** backend with:
  - `/api/v1/health` – health check
  - `/api/v1/greet` – greeting endpoint:
    - Takes **name + date of birth + provider (openai / oss / mock)**
    - Detects if it’s your **birthday month**
    - Uses **OpenAI or OSS model** (or mock) to generate a greeting
    - Caches responses in **Redis**
- Exposes a **Streamlit UI** that:
  - Lets you enter name + DOB + provider
  - Shows normal + birthday greetings
  - Talks to the FastAPI backend

### 1.2 Infra pieces (dev)

- **VPC** with public + private subnets, NAT, IGW
- **EKS** cluster: `d32-release-dev-eks`
  - Node group for **app**
  - Node group for **model-service** (future GPU-ready)
- **ALB** via **AWS Load Balancer Controller**
- **DNS / TLS**:
  - `d32-release-dev-api.rdhcloudlab.com`
  - `d32-release-dev-model.rdhcloudlab.com`
  - `d32-release-dev-ui.rdhcloudlab.com`
  - Validated **ACM** cert in `ap-south-1`
- **Data**:
  - **ElastiCache Redis** (greetings cache)
  - **RDS Postgres** (optional / minimal for now)
  - **S3** bucket (docs/logs/artefacts)
- **Images & secrets**:
  - **ECR** repos: `d32-release-dev-api`, `...-model`, `...-ui`
  - **AWS Secrets Manager** for LLM keys / DB creds (conceptually; wired via env/IRSA in real prod)

---

## 2. Repository Layout

```text
Day32/terraform-genai-release-topic-poc/
  README.md
  pyproject.toml
  .env.example

  src/
    app/
      __init__.py
      main.py          # FastAPI entrypoint

    core/
      __init__.py
      models.py        # Pydantic request/response models
      services.py      # Business logic (greeting, birthday detection, cache)
      llm_client.py    # LLMClient wrapper (OpenAI / OSS / mock)

    config/
      __init__.py
      settings.py      # Pydantic Settings (env vars: DB, Redis, LLM keys, etc.)

  ui/
    app.py             # Streamlit UI

  terraform/
    day32_release_topic/
      envs/
        dev/
          backend.tf
          main.tf
          variables.tf
          outputs.tf
          locals.tf
          terraform.tfvars   # << your env-specific values (domain, hosted zone, etc.)

      modules/
        vpc/
        eks/
        rds/
        redis/
        s3_docs/
        ecr/
        dns/
        acm_cert/
        secrets_manager/

  k8s/
    base/
      namespace.yaml
      app-configmap.yaml
      api-deployment.yaml
      api-service.yaml
      model-service-deployment.yaml
      model-service.yaml
      ui-deployment.yaml
      ui-service.yaml
      ingress.yaml

  scripts/
    deploy_dev_k8s.sh   # Uses terraform outputs + envsubst + kubectl

  tests/
    test_app.py
````

---

## 3. Prerequisites

* **AWS account** with:

  * IAM user/role able to create EKS, VPC, RDS, ElastiCache, ACM, Route 53, etc.
  * A **Route 53 hosted zone** for `rdhcloudlab.com`.
* **Domain**: `rdhcloudlab.com` purchased + hosted in Route 53.
* **Local tools on EC2 or your workstation**:

  * `aws` CLI (configured with `ap-south-1`)
  * `kubectl`
  * `terraform` (>= 1.5+ recommended)
  * `docker`
  * `python` (3.10+), `pip`
* **Optional:** `helm` if you want to re-install AWS Load Balancer Controller via chart.

> **Region used**: `ap-south-1` (Mumbai) – adjust only if you also change Terraform.

---

## 4. Quickstart TL;DR

From repo root `Day32/terraform-genai-release-topic-poc`:

```bash
# 1. Configure terraform.tfvars (root_domain, hosted_zone_id, etc.)

# 2. Provision AWS infra (dev env)
cd terraform/day32_release_topic/envs/dev
terraform init
terraform apply

# 3. Build & push Docker images to ECR
cd ../../../..
./scripts/build_and_push_dev.sh   # If you create this (see below), or follow section 6.

# 4. Deploy to EKS
./scripts/deploy_dev_k8s.sh

# 5. Test via domain
curl -k https://d32-release-dev-api.rdhcloudlab.com/api/v1/health

# 6. Open Streamlit UI in browser
https://d32-release-dev-ui.rdhcloudlab.com/

# 7. Cleanup when done
kubectl delete namespace d32-release-dev
cd terraform/day32_release_topic/envs/dev
terraform destroy
```

---

## 5. Configure Terraform (envs/dev)

Go to:

```bash
cd terraform/day32_release_topic/envs/dev
```

Edit `terraform.tfvars` (create if missing):

```hcl
# Your root domain and hosted zone
root_domain    = "rdhcloudlab.com"
hosted_zone_id = "<YOUR_ROUTE53_ZONE_ID>"

# (Optional) tags
environment = "dev"
owner       = "radheshyam"
poc_id      = "d32-release"
```

> All resource names will be prefixed with `d32-release-dev-*` so they don’t collide with any other PoCs.

---

## 6. Provision AWS Infra (VPC, EKS, Redis, RDS, DNS, ACM, ECR)

From `envs/dev`:

```bash
terraform init
terraform plan
terraform apply
```

What this will create (high-level):

* **Core infra**:

  * VPC, subnets, route tables, NAT, IGW
* **Compute**:

  * EKS cluster `d32-release-dev-eks` + node groups:

    * `d32-release-dev-app-ng`
    * `d32-release-dev-model-ng`
* **Data**:

  * RDS Postgres `d32-release-dev-postgres`
  * ElastiCache Redis `d32-release-dev-redis`
* **Networking / edge**:

  * ACM certificate for:

    * `rdhcloudlab.com`
    * `d32-release-dev-api.rdhcloudlab.com`
    * `d32-release-dev-model.rdhcloudlab.com`
    * `d32-release-dev-ui.rdhcloudlab.com`
* **Others**:

  * ECR repositories for api/model/ui
  * Route 53 records for `d32-release-dev-*` (wired to ALB after ALB exists)
  * IAM roles (including for AWS Load Balancer Controller via IRSA)
  * (Conceptual) Secrets in Secrets Manager

After apply, note the outputs:

```bash
terraform output
```

Pay attention to:

* `eks_cluster_name`
* `redis_endpoint`
* `acm_certificate_arn`
* ECR repo URLs (if exposed)
* Domain outputs for API/UI

---

## 7. Build & Push Docker Images to ECR

From repo root:

```bash
cd ~/poc/genai-interview-lab/Day32/terraform-genai-release-topic-poc
```

### 7.1 Login to ECR

```bash
AWS_REGION=ap-south-1
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

aws ecr get-login-password --region "$AWS_REGION" \
  | docker login \
    --username AWS \
    --password-stdin "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
```

### 7.2 Build images

```bash
docker build -f Dockerfile.api   -t d32-release-dev-api:latest   .
docker build -f Dockerfile.model -t d32-release-dev-model:latest .
docker build -f Dockerfile.ui    -t d32-release-dev-ui:latest    .
```

### 7.3 Tag & push

Assuming Terraform created repos:

* `d32-release-dev-api`
* `d32-release-dev-model`
* `d32-release-dev-ui`

```bash
docker tag d32-release-dev-api:latest   ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/d32-release-dev-api:latest
docker tag d32-release-dev-model:latest ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/d32-release-dev-model:latest
docker tag d32-release-dev-ui:latest    ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/d32-release-dev-ui:latest

docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/d32-release-dev-api:latest
docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/d32-release-dev-model:latest
docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/d32-release-dev-ui:latest
```

> You can wrap this into `scripts/build_and_push_dev.sh` for convenience.

---

## 8. Deploy to EKS (Kubernetes manifests)

From repo root:

```bash
./scripts/deploy_dev_k8s.sh
```

This script:

1. Goes to Terraform dev env and reads outputs:

   * `AWS_ACCOUNT_ID` via `aws sts`
   * `REDIS_ENDPOINT` via `terraform output -raw redis_endpoint`
   * `ACM_CERT_ARN` via `terraform output -raw acm_certificate_arn`
   * `EKS_CLUSTER_NAME` via `terraform output -raw eks_cluster_name`

2. Updates kubeconfig:

   ```bash
   aws eks update-kubeconfig --name "$EKS_CLUSTER_NAME" --region ap-south-1
   ```

3. Uses `envsubst` to template + apply K8s manifests:

   ```bash
   envsubst < k8s/base/namespace.yaml           | kubectl apply -f -
   envsubst < k8s/base/app-configmap.yaml       | kubectl apply -f -
   envsubst < k8s/base/api-deployment.yaml      | kubectl apply -f -
   envsubst < k8s/base/model-service-deployment.yaml | kubectl apply -f -
   envsubst < k8s/base/ui-deployment.yaml       | kubectl apply -f -
   envsubst < k8s/base/ingress.yaml             | kubectl apply -f -
   ```

4. Shows status:

   ```bash
   kubectl get pods -n d32-release-dev
   kubectl get svc -n d32-release-dev
   kubectl get ingress -n d32-release-dev
   ```

You should see:

* 3 pods running (api, model-service, ui)
* 3 ClusterIP services
* 1 Ingress with `IngressClass` = `alb`

---

## 9. Verify via Domain Name (HTTPS)

### 9.1 Check Ingress & ALB

```bash
kubectl get ingress d32-release-dev-ingress -n d32-release-dev
```

You want:

* `CLASS` = `alb`
* `HOSTS` = `d32-release-dev-api.rdhcloudlab.com, ...-model, ...-ui`
* `ADDRESS` = `k8s-...ap-south-1.elb.amazonaws.com`

If `ADDRESS` is empty:

* Check `kubectl describe ingress ...` for events.
* Common issues:

  * **IAM** for AWS Load Balancer Controller (e.g. missing `ec2:DescribeRouteTables`)
  * **Subnet tags** missing (`kubernetes.io/cluster/d32-release-dev-eks`, `kubernetes.io/role/elb`)

Once ALB is there, Route 53 records (from Terraform `dns` module) should point to it.

### 9.2 Test API via domain

```bash
# Health
curl -k https://d32-release-dev-api.rdhcloudlab.com/api/v1/health

# Greeting
curl -k -X POST https://d32-release-dev-api.rdhcloudlab.com/api/v1/greet \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Radhe",
    "date_of_birth": "1995-12-05",
    "provider": "mock"
  }'
```

### 9.3 Test Streamlit UI via browser

Open:

```text
https://d32-release-dev-ui.rdhcloudlab.com/
```

In the Greeting tab:

* Enter name + DOB
* Select provider (OpenAI / OSS / Mock)
* Confirm:

  * Normal greeting in non-birthday month
  * Birthday-month special message during birthday month
  * Proper LLM provider label in response

---

## 10. Local Dev (Optional, No AWS)

Run everything locally:

```bash
cd ~/poc/genai-interview-lab/Day32/terraform-genai-release-topic-poc

python -m venv .venv
source .venv/bin/activate
pip install .
cp .env.example .env

# Start local Redis
docker run --name d32-redis-local -p 6379:6379 -d redis:7

# FastAPI
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Streamlit UI
streamlit run ui/app.py
```

Then:

* API: `http://localhost:8000/api/v1/health`
* UI: `http://localhost:8501/`

---

## 11. Cost Awareness (2-Day PoC)

Approximate **2-day dev run** (EKS + NAT + ALB + RDS + Redis + S3 + ECR):

* ~**$13–15 USD** (~₹1,200–₹1,400) for 48 hours, depending on instance sizes.
* Biggest contributors:

  * **EKS control plane**
  * **EC2 worker nodes**
  * **NAT Gateway**
  * **ALB**
  * **RDS** + **ElastiCache**

**Tips:**

* Use **smallest** instance types allowed (e.g. `t3.small` / `t3.micro`).
* **Destroy infra** as soon as testing is done.
* Use **mock LLM mode** or Redis cache to reduce LLM API cost.
* Keep PoC limited to **dev env**, don’t run 24/7.

---

## 12. Cleanup & Destroy All Resources

### 12.1 Cleanup inside Kubernetes

Delete the whole namespace:

```bash
kubectl delete namespace d32-release-dev
kubectl get ns
```

You should only see:

* `default`, `kube-system`, `kube-public`, `kube-node-lease`.

> This removes all **pods, services, ingress, configmaps** for this PoC.

### 12.2 Destroy AWS infra (Terraform)

From dev env folder:

```bash
cd ~/poc/genai-interview-lab/Day32/terraform-genai-release-topic-poc/terraform/day32_release_topic/envs/dev

terraform destroy
# or
terraform destroy -auto-approve
```

If you see errors like:

* **S3 bucket not empty** → empty bucket in S3 console, re-run destroy.
* **ECR repo not empty** → delete images in ECR console, re-run destroy.

### 12.3 AWS Console sanity checklist

Verify **no `d32-release-*` resources remain**:

* **VPC**: VPC + subnets + route tables + NAT + IGW
* **EKS**: cluster `d32-release-dev-eks` and node groups
* **EC2 → Load Balancers**: ALB for this PoC
* **EC2 → Security Groups**: SGs with `d32-release-*`
* **RDS**: DB instance + subnet group
* **ElastiCache**: Redis cluster
* **S3**: buckets with `d32-release-*`
* **ECR**: repos `d32-release-dev-api`, `...-model`, `...-ui`
* **Route 53**: records `d32-release-dev-*.rdhcloudlab.com`
* **ACM**: certs created for these subdomains (if Terraform-managed)
* **Secrets Manager**: secrets with `d32-release-*` (if created)
* **CloudWatch Logs**: log groups for EKS/RDS/ALB for this PoC (optional to delete, but tidy)

Once this checklist is clean → **no ongoing AWS cost** for Day32.

---

## 13. Notes & Gotchas

* **LLM keys**:

  * Never commit real keys to git.
  * Use `.env` for local dev, AWS **Secrets Manager** for cloud.
* **Redis endpoint format**:

  * If Terraform outputs `host:port`, don’t append another `:6379` in `ConfigMap`.
  * Example safe `REDIS_URL`: `redis://d32-release-dev-redis.xxxxxx.aps1.cache.amazonaws.com:6379/0`
* **AWS Load Balancer Controller IAM**:

  * Must allow at least:

    * `ec2:DescribeSubnets`
    * `ec2:DescribeSecurityGroups`
    * `ec2:DescribeRouteTables`
    * and other standard actions from official AWS policy.
  * Missing `ec2:DescribeRouteTables` → ingress events will show **UnauthorizedOperation**.
* **Subnet tagging**:

  * Public subnets must be tagged with:

    * `kubernetes.io/cluster/d32-release-dev-eks = shared`
    * `kubernetes.io/role/elb = 1`

---

## 14. How to Use This PoC in Interviews

You can describe this as:

> “I designed and implemented a GenAI PoC with a FastAPI backend, a model-serving microservice, and a Streamlit UI. It runs on EKS with separate node groups for app and model workloads, uses ElastiCache Redis for caching, and maps to my own domain via ALB + ACM + Route 53. All infra is defined in Terraform, and I have a clear cost and cleanup story to avoid unnecessary AWS spend.”

That hits:

* **App design**
* **GenAI integration (OpenAI/OSS)**
* **Kubernetes + EKS**
* **Terraform / IaC**
* **Networking (ALB, TLS, DNS)**
* **Cost awareness and lifecycle management**

---

```
