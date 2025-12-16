# d33-oss-prod — Phase A Decisions

## Identity
- PoC ID: d33-oss-prod
- Region: ap-south-1
- Namespace: d33-oss-prod
- Domain root: rdhcloudlab.com

## Routing (Default)
- UI:  https://d33-oss.rdhcloudlab.com  -> chat-frontend (Next.js)
- API: https://api.d33-oss.rdhcloudlab.com -> rag-backend (FastAPI)
- Optional later: https://d33-oss.rdhcloudlab.com/api (path-based)

## Services (in-cluster DNS)
- Frontend: http://d33-oss-frontend:3000
- Backend:  http://d33-oss-backend:8000
- Model:    http://d33-oss-model:11434  (Ollama)

## Model
- Default: OLLAMA_MODEL=llama3.2:3b
- Alternatives: phi3:mini, tinyllama:latest
- Ollama must bind to 0.0.0.0 in Kubernetes:
  - OLLAMA_HOST=0.0.0.0:11434

## IaC Boundary
- Terraform: EKS, nodegroups, IRSA, Route53, ACM (+ validation), optional data services
- Helm: Deployments/Services/Ingress/ConfigMaps/HPA; reference Secrets (no secrets in Git)
