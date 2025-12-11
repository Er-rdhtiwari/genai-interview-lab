# DAY_32 Architecture Overview – GenAI Release Notes PoC (`d32-release`)

## 1. High-Level Flow

Goal: Expose a small **GenAI Release Notes API** at:

- `https://d32-release-dev-api.rdhcloudlab.com`

which:
- Accepts a short change description,
- Asks an LLM to draft release notes + 2–3 test scenarios,
- Caches results in Redis,
- (Optionally) persists metadata in Postgres,
- Returns a clean JSON response.

## 2. Traffic & Control Plane

1. Client (browser / curl / Postman) calls:
   `https://d32-release-dev-api.rdhcloudlab.com`.
2. **Route 53** has a DNS record (e.g. A/ALIAS) pointing to an **ALB**.
3. **ACM** provides an SSL certificate for `d32-release-dev-api.rdhcloudlab.com`
   attached to that ALB.
4. ALB forwards HTTPS traffic to the **EKS** cluster via Kubernetes Ingress (managed by
   AWS Load Balancer Controller).
5. In EKS:
   - Requests hit the **FastAPI Release Notes API** service running in a dedicated
     **"app" node group**.

## 3. EKS Cluster & Node Group Separation

- Single **EKS cluster**, e.g. `d32-release-dev-eks`.
- Two managed node groups:

  1. **App node group** (for FastAPI / lightweight services)
     - Name example: `d32-release-dev-ng-app`
     - Labeled: `role=app`
     - Taints: optional (e.g. no taints, or `workload=app:NoSchedule`)

  2. **Model node group** (for GenAI model-serving pods)
     - Name example: `d32-release-dev-ng-model`
     - Labeled: `role=model`
     - Can use taints like `workload=model:NoSchedule`

- Kubernetes workloads use:
  - `nodeSelector` or `nodeAffinity` to pin:
    - API pods to `role=app`,
    - Model pods to `role=model`.
  - Optionally `tolerations` if node groups are tainted.
- This separation allows:
  - Independent scaling (more model nodes without touching API nodes),
  - Different instance types in the future (e.g., GPU for model, CPU for app).

> For this PoC, the "model service" may still call external LLMs (OpenAI).
> The key is the **infra pattern** of separate node groups for app vs model workloads.

## 4. Data Plane (RDS, Redis, S3, Secrets, ECR)

- **RDS Postgres** (db.t3.micro):
  - Stores structured release metadata (future),
  - Lives in private subnets.

- **ElastiCache Redis** (cache.t3.micro):
  - Holds short-lived cache entries for identical LLM requests.

- **S3 docs bucket**:
  - Name: `d32-release-dev-docs` (or similar),
  - Future use: exporting release notes, logs, or artifacts.

- **ECR repo**:
  - Name: `d32-release-dev-genai-api`,
  - Stores container images for:
    - FastAPI Release Notes API,
    - Model service image (later).

- **Secrets Manager**:
  - Stores OpenAI API key, DB password, maybe Redis auth tokens.
  - Accessed via **IRSA** (IAM roles for service accounts) in EKS,
    not via hard-coded keys or `.env` files in the cluster.

## 5. VPC and Networking

- VPC CIDR: `10.32.0.0/16` (dedicated to this PoC's dev environment).
- Subnets:
  - 2x **public subnets** for NAT/ALB.
  - 2x **private subnets** for EKS nodes, RDS, and Redis.

- Routing:
  - Public subnets route to Internet via IGW.
  - Private subnets route outbound via NAT Gateway.

## 6. Logical View (Text Diagram)

```text
Client (curl / browser)
     |
     v
Route 53  (d32-release-dev-api.rdhcloudlab.com)
     |
     v
ALB (HTTPS, ACM cert)
     |
     v
EKS (d32-release-dev-eks)
   |--------------------------|
   | Node group: APP          |
   |  - FastAPI Release API   |
   |                          |
   | Node group: MODEL        |
   |  - GenAI Model Service   |
   |--------------------------|
     |      |        |
     |      |        +--> S3 (d32-release-dev-docs)
     |      +--> Redis (ElastiCache)
     +--> RDS Postgres

Secrets Manager (OpenAI key, DB creds) --> accessed via IRSA from pods
ECR (d32-release-dev-genai-api)        --> stores app + model images
```

## 7. Key Design Decision – Separate Node Groups for App vs Model

We explicitly separate EKS node groups into **app** and **model** workloads to:

- Allow independent autoscaling (e.g., more model pods for heavy LLM traffic).
- Use different instance families later (e.g., GPU for model, CPU-only for app).
- Isolate noisy model workloads from lighter API workloads.
- Introduce different pod disruption budgets, rollout strategies, and resource
  requests/limits per node group.

Implementation-wise this uses:
- Dedicated managed node groups per role,
- Node labels (`role=app` / `role=model`),
- nodeSelector / affinity and optional taints + tolerations.
