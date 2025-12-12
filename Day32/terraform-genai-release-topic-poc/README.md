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

Tthis is exactly the right moment to do a **“no-bill, no-surprise” sanity check** ✅

Below is a **checkpoint playbook** you can literally run line-by-line to confirm that **all Day32 (`d32-release-dev`) resources are gone**.

I’ll assume:

* Region: `ap-south-1`
* PoC prefix in names/tags: `d32-release` / `d32-release-dev`

---

## 0. Setup

On your EC2 (or wherever `aws` CLI is configured):

```bash
export AWS_REGION=ap-south-1
export POC_PREFIX=d32-release
```

If you’re still in the Terraform env folder, you can also quickly confirm state:

```bash
cd ~/poc/genai-interview-lab/Day32/terraform-genai-release-topic-poc/terraform/day32_release_topic/envs/dev

# If destroy completed, this should show either no state or an empty list
terraform state list
```

* If you see `No state file was found` or **no resources listed** → good sign.

---

## 1️⃣ Kubernetes (EKS cluster namespace)

You already did:

```bash
kubectl get ns
```

Expected for **clean**:

```text
default
kube-node-lease
kube-public
kube-system
```

No `d32-release-dev` namespace → ✔️ workloads removed from EKS.

---

## 2️⃣ EKS Cluster & Node Groups

### Check clusters

```bash
aws eks list-clusters \
  --region "$AWS_REGION" \
  --query "clusters[]" \
  --output text
```

* ✅ Clean if there is **no** `d32-release-dev-eks` in the output.

### (Optional) Check for any leftover nodegroups

If cluster is deleted, nodegroups should already be gone, but you can double-check **before** cluster deletion next time:

```bash
aws eks list-nodegroups \
  --cluster-name d32-release-dev-eks \
  --region "$AWS_REGION" \
  --query "nodegroups[]" \
  --output text || echo "Cluster not found (good)"
```

---

## 3️⃣ VPC, Subnets, NAT, IGW, Security Groups

If you tagged resources with `poc = d32-release`, these commands will show leftovers.

### VPCs

```bash
aws ec2 describe-vpcs \
  --region "$AWS_REGION" \
  --filters "Name=tag:poc,Values=$POC_PREFIX" \
  --query "Vpcs[].{VpcId:VpcId,Name:Tags[?Key=='Name']|[0].Value}" \
  --output table
```

* ✅ Clean if output is `None` / empty table.

### Subnets

```bash
aws ec2 describe-subnets \
  --region "$AWS_REGION" \
  --filters "Name=tag:poc,Values=$POC_PREFIX" \
  --query "Subnets[].{SubnetId:SubnetId,Name:Tags[?Key=='Name']|[0].Value}" \
  --output table
```

### NAT Gateways

```bash
aws ec2 describe-nat-gateways \
  --region "$AWS_REGION" \
  --filter "Name=tag:poc,Values=$POC_PREFIX" \
  --query "NatGateways[].{NatGatewayId:NatGatewayId,State:State}" \
  --output table
```

### Internet Gateways

```bash
aws ec2 describe-internet-gateways \
  --region "$AWS_REGION" \
  --filters "Name=tag:poc,Values=$POC_PREFIX" \
  --query "InternetGateways[].{IgId:InternetGatewayId}" \
  --output table
```

### Security Groups

```bash
aws ec2 describe-security-groups \
  --region "$AWS_REGION" \
  --filters "Name=tag:poc,Values=$POC_PREFIX" \
  --query "SecurityGroups[].{GroupId:GroupId,GroupName:GroupName}" \
  --output table
```

* All of the above should return **empty** → no Day32 networking infra left.

---

## 4️⃣ Load Balancers (ALB) & Target Groups

### ALBs (ELBv2)

```bash
aws elbv2 describe-load-balancers \
  --region "$AWS_REGION" \
  --query "LoadBalancers[?contains(LoadBalancerName, 'd32') || contains(DNSName, 'd32-release')].{Name:LoadBalancerName,DNS:DNSName}" \
  --output table
```

### Target Groups

```bash
aws elbv2 describe-target-groups \
  --region "$AWS_REGION" \
  --query "TargetGroups[?contains(TargetGroupName, 'd32')].{Name:TargetGroupName,Arn:TargetGroupArn}" \
  --output table
```

* ✅ Clean if these tables are empty.

---

## 5️⃣ RDS (Postgres) + Snapshots

### DB instances

```bash
aws rds describe-db-instances \
  --region "$AWS_REGION" \
  --query "DBInstances[?contains(DBInstanceIdentifier, 'd32-release')].DBInstanceIdentifier" \
  --output text
```

* ✅ Clean if output is empty.

### Optional: Snapshots (if final snapshot was created)

```bash
aws rds describe-db-snapshots \
  --region "$AWS_REGION" \
  --query "DBSnapshots[?contains(DBSnapshotIdentifier, 'd32-release')].DBSnapshotIdentifier" \
  --output text
```

* If any remain and you don’t need them, you can delete via console or CLI.

---

## 6️⃣ ElastiCache (Redis)

```bash
aws elasticache describe-replication-groups \
  --region "$AWS_REGION" \
  --query "ReplicationGroups[?contains(ReplicationGroupId, 'd32-release')].ReplicationGroupId" \
  --output text
```

and/or

```bash
aws elasticache describe-cache-clusters \
  --region "$AWS_REGION" \
  --query "CacheClusters[?contains(CacheClusterId, 'd32-release')].CacheClusterId" \
  --output text
```

* ✅ Empty output → Redis cluster cleared.

---

## 7️⃣ S3 Buckets

```bash
aws s3api list-buckets \
  --query "Buckets[?contains(Name, 'd32-release')].Name" \
  --output text
```

* ✅ Clean if nothing listed.
* If a bucket is still there but destroy failed because it wasn’t empty:

  * Manually **empty** it in S3 console,
  * Then re-run `terraform destroy`.

---

## 8️⃣ ECR Repositories

You just hit the error here, so this is important.

```bash
aws ecr describe-repositories \
  --region "$AWS_REGION" \
  --query "repositories[?contains(repositoryName, 'd32-release')].repositoryName" \
  --output text
```

* ✅ Clean if nothing listed.

If some are left (e.g. `d32-release-dev-api`, `d32-release-dev-ui`):

1. List images:

   ```bash
   aws ecr list-images \
     --region "$AWS_REGION" \
     --repository-name d32-release-dev-api \
     --query 'imageIds[*]' \
     --output table
   ```

2. Delete images with `batch-delete-image` (as in previous message) and then either:

   * Remove the repo manually in console, or
   * Re-run `terraform destroy`.

---

## 9️⃣ Route 53 (records for your PoC)

Get hosted zone ID for `rdhcloudlab.com`:

```bash
HZ_ID=$(aws route53 list-hosted-zones-by-name \
  --dns-name rdhcloudlab.com \
  --query "HostedZones[0].Id" \
  --output text | sed 's|/hostedzone/||')

echo "$HZ_ID"
```

List any Day32-related records:

```bash
aws route53 list-resource-record-sets \
  --hosted-zone-id "$HZ_ID" \
  --query "ResourceRecordSets[?contains(Name, 'd32-release-dev')]" \
  --output table
```

* ✅ Clean if table is empty.

(You should no longer see `d32-release-dev-api.rdhcloudlab.com`, `...-model`, `...-ui`.)

---

## 🔟 ACM Certificates

```bash
aws acm list-certificates \
  --region "$AWS_REGION" \
  --query "CertificateSummaryList[?contains(DomainName, 'd32-release-dev')].{Arn:CertificateArn,Domain:DomainName}" \
  --output table
```

* ✅ Empty → no Day32-only ACM certs hanging around.

*(You might have other ACM certs for your root domain — don’t delete those unless you’re sure.)*

---

## 1️⃣1️⃣ Secrets Manager (if you created PoC-specific secrets)

```bash
aws secretsmanager list-secrets \
  --region "$AWS_REGION" \
  --query "SecretList[?contains(Name, 'd32-release')].Name" \
  --output text
```

* ✅ Empty output → no Day32-specific secrets.

---

## 1️⃣2️⃣ CloudWatch Logs (optional cleanup)

These are usually cheap, but you can check:

```bash
aws logs describe-log-groups \
  --region "$AWS_REGION" \
  --log-group-name-prefix "/aws/eks/d32-release-dev-eks" \
  --query "logGroups[].logGroupName" \
  --output text
```

and similar for RDS/ALB if you configured logging.

If any left and you want to be super-clean:

```bash
aws logs delete-log-group \
  --region "$AWS_REGION" \
  --log-group-name "<LOG_GROUP_NAME>"
```

---

## 1️⃣3️⃣ IAM Roles (optional, but good verification)

Check for PoC-specific roles:

```bash
aws iam list-roles \
  --query "Roles[?contains(RoleName, 'd32-release')].RoleName" \
  --output text
```

* Things like `AmazonEKSLoadBalancerControllerRole-d32-release-dev` should be gone after destroy.

If something still shows up and you know Terraform created it, either:

* Run `terraform destroy` again after fixing errors, or
* Manually delete role in IAM console if you are sure it’s no longer needed.

---

### ✅ Final “All Clean” Criteria

You’re fully safe when:

* `terraform state list` shows nothing for Day32 dev.
* All the AWS CLI checks above return **empty** for `d32-release` / `d32-release-dev`.
* No `d32-release-*` resources are visible in:

  * **VPC**
  * **EKS**
  * **EC2 → Load Balancers**
  * **RDS**
  * **ElastiCache**
  * **S3**
  * **ECR**
  * **Route 53**
  * **ACM**
  * **Secrets Manager**
  * (**Optional**) CloudWatch Logs, IAM roles

If you run any of these commands and see a leftover resource you’re unsure about, paste the output and I can tell you whether it’s safe to delete and how.
