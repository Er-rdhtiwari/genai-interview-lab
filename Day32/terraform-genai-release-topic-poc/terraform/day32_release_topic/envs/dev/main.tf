provider "aws" {
  region = local.aws_region
}

# This file will wire together all modules for the Day32 dev environment:
# - VPC (public/private subnets, NAT/IGW)
# - EKS (cluster + 2 node groups: app + model)
# - RDS Postgres (for future metadata)
# - ElastiCache Redis (non-optional cache)
# - S3 docs bucket
# - ECR repositories
# - Route 53 records (api/model/ui)
# - ACM certificate for the FQDNs
# - Secrets Manager (logical secrets for LLM/API/DB)

# In later parts we will add module blocks such as:
#
# module "vpc" {
#   source = "../../modules/vpc"
#   # ...
# }
#
# module "eks" {
#   source = "../../modules/eks"
#   # ...
# }
#
# module "rds" { ... }
# module "redis" { ... }
# module "s3_docs" { ... }
# module "ecr" { ... }
# module "dns" { ... }
# module "acm_cert" { ... }
# module "secrets_manager" { ... }
#
# For now, this file just ensures the AWS provider + locals/variables are wired correctly.
