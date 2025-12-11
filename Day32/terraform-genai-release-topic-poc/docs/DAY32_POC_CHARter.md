# DAY_32 – GenAI Release Notes Assistant PoC (`d32-release`)

## Problem / Use Case

Teams ship frequent changes but struggle to write clear, consistent release notes and test scenarios.
This PoC builds a small **GenAI Release Notes Assistant** that converts a short change description
into:
- A concise, user-facing release note, and
- 2–3 suggested test scenarios.

The goal is to showcase how a **FastAPI + LLM backend** can sit on top of a minimal AWS data plane
(VPC, RDS, Redis, S3, ECR, Secrets Manager) provisioned via **Terraform**.

## PoC Identity

- **Day label:** `DAY_32`
- **PoC ID:** `d32-release`
- **Full PoC name:** `day32-release-topic`
- **Root domain (global lab, not necessarily used in this PoC):** `rdhcloudlab.com`

## High-Level Goals

- Keep the app intentionally small: 1 main POST endpoint + 1 health endpoint.
- Make infra minimal but realistic: VPC, RDS Postgres, Redis, S3, ECR, Secrets Manager.
- Follow clean naming/tagging so Day 32 does not conflict with other PoCs.
- Ensure everything can be:
  1. **Built** (Python + Terraform),
  2. **Run & tested** locally,
  3. **Provisioned & destroyed** safely in AWS within ~2 days of usage.
# DAY_32 Naming & Isolation Rules (`d32-release`)

## Terraform / Infrastructure

- Use `d32-release` as the **PoC ID**.
- Use `d32-release-<env>` as the **name prefix**, e.g.:
  - `d32-release-dev` for this PoC's dev environment.
- All AWS resources created by Terraform must include:
  - `poc = "d32-release"`
  - `environment = "dev"`
  - `day_label = "DAY_32"`

**Resource name examples:**

- VPC: `d32-release-dev-vpc`
- RDS instance: `d32-release-dev-postgres`
- Redis: `d32-release-dev-redis`
- S3 bucket: `d32-release-dev-docs`
- ECR repo: `d32-release-dev-genai-api`

## Terraform Layout

- All Terraform for this PoC lives under:
  - `terraform/day32_release_topic/...`
- Do **not** reuse state or folders from other days
  (e.g. Day 31, other experiments).

## Application Code

- Root path for this PoC:
  - `Day32/terraform-genai-release-topic-poc/`
- Any app-level names that might collide should include:
  - `d32-release` or `DAY_32` (e.g. log messages, metrics prefixes).

## DNS / Domains (Conceptual)

- Global lab domain: `rdhcloudlab.com`.
- PoC-specific subdomains for this PoC, if/when needed:
  - `d32-release-dev-api.rdhcloudlab.com`
- These names must **not** be reused by other PoCs.
