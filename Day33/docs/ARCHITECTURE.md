# d33-oss-prod — Architecture

[Browser]
  |
  | HTTPS (ACM cert on ALB)
  v
[ALB Ingress]
  | host: d33-oss.rdhcloudlab.com   -> svc/d33-oss-frontend:3000
  | host: api.d33-oss.rdhcloudlab.com -> svc/d33-oss-backend:8000
  v
[Kubernetes Namespace: d33-oss-prod]
  - d33-oss-frontend (Next.js)
  - d33-oss-backend  (FastAPI)
  - d33-oss-model    (Ollama + PVC model cache)

Backend flow:
Frontend -> /api/chat -> Backend -> Ollama POST /api/chat -> response -> Frontend
