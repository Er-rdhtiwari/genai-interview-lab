# Terraform + GenAI Release Note Helper (PoC)

## Problem & Use Case

Platform and DevOps teams frequently roll out infrastructure changes (Terraform modules, AWS/EKS/RDS/S3 tweaks, networking updates) and need to communicate these changes clearly to engineering stakeholders. Writing short, consistent, human-friendly release notes manually is repetitive and error-prone.

This PoC provides a tiny internal tool where an engineer can paste a short description of an infrastructure change and receive a concise, LLM-generated release note sentence suitable for changelogs or deployment summaries.

## Goals of This PoC

- Build a **small FastAPI service** that exposes a single endpoint:
  - `POST /api/v1/release-note` → returns one short release note sentence.
- Wrap LLM access behind an **LLM client abstraction**:
  - Use **OpenAI** when an API key is configured.
  - Fall back to a **deterministic mock** response when no key is set.
- Use **Terraform** to provision a minimal but realistic AWS footprint:
  - An **S3 bucket** for storing docs or infra-related artifacts.
  - A small **RDS Postgres** instance for future persistence practice.
  - A **Route 53 hosted zone** and `api.<root_domain>` DNS record (pointing to localhost for now).
- Follow **industry-style structure** for both application and infrastructure:
  - Clear Python packages: `app/`, `core/`, `config/`, `tests/`.
  - Terraform layout with `terraform/envs/dev` and `terraform/modules/*`.
- Keep the PoC **cost-aware and easy to tear down**:
  - Use dev-sized AWS resources only.
  - Ensure everything is managed by Terraform and can be destroyed safely.

## What We Will Build (App vs. Infra)

**Application (FastAPI + LLM):**

- A small FastAPI service with:
  - `/health` – basic health check.
  - `/api/v1/release-note` – accepts a short infra change description and returns an LLM-generated release note.
- `LLMClient` abstraction that:
  - Uses OpenAI Chat Completions if `OPENAI_API_KEY` is present.
  - Otherwise returns a deterministic `MOCK_LLM_RESPONSE` for the given prompt.
- A service layer that converts raw descriptions into structured prompts and trims the LLM output into a single clean sentence.

**Infrastructure (Terraform + AWS):**

- Terraform root module under `terraform/envs/dev` and reusable modules under `terraform/modules`.
- AWS resources:
  - **S3** bucket for docs or infra-related artifacts.
  - **RDS** Postgres (small dev instance) to practice DB provisioning.
  - **Route 53** hosted zone and `api.<root_domain>` A record (currently pointing to `127.0.0.1` to remind us that DNS should be code-driven).
- Local Terraform state for the PoC, with a clear path to migrate to **S3 + DynamoDB** remote state in a real setup.

## High-Level Architecture

At a high level, this PoC has two layers:

1. **Application layer (FastAPI + LLM client)**  
   - A FastAPI service exposes:
     - `GET /health` for basic health checks.
     - `POST /api/v1/release-note` for generating release notes.
   - A service layer builds a structured prompt from a short infra change description.
   - An `LLMClient` abstraction calls OpenAI Chat Completions when an API key is present, and falls back to a deterministic mock response when no provider is configured.

2. **Infrastructure layer (Terraform + AWS)**  
   - Terraform root module under `terraform/envs/dev` wires together:
     - `modules/s3_docs` → one S3 bucket for infra docs or artifacts.
     - `modules/rds` → a small Postgres RDS instance (db.t3.micro) for future persistence.
     - `modules/dns` → a Route 53 hosted zone and `api.<root_domain>` A record.
   - For this PoC, the FastAPI app runs locally on `http://localhost:8000`, while the AWS resources are provisioned via Terraform for infra practice and future integration.
   - Terraform uses a **dev environment** layout, with a clear path to adding `stage` and `prod` as separate env folders and state files.
### Request Flow (Conceptual)

```text
Client (curl / browser)
        |
        v
FastAPI app (local)
  - /health
  - /api/v1/release-note
        |
        v
LLMClient
  - OpenAI Chat Completions (if OPENAI_API_KEY is set)
  - MOCK_LLM_RESPONSE (if no key is configured)

Terraform-managed AWS (dev)
  - S3 bucket (docs / artifacts)
  - RDS Postgres instance (db.t3.micro)
  - Route 53 hosted zone + api.<root_domain> A record

```

