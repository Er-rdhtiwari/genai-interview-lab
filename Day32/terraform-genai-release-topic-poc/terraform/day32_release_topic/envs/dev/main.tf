provider "aws" {
  region = local.aws_region
}

# Day32 d32-release VPC: base network for EKS, RDS, Redis, ALB, etc.
module "vpc" {
  source = "../../modules/vpc"

  name_prefix = local.name_prefix     # e.g. d32-release-dev
  cidr_block  = "10.32.0.0/16"
  az_count    = 2
  tags        = local.tags
}

# S3 docs bucket for release notes / artifacts
module "s3_docs" {
  source = "../../modules/s3_docs"

  name_prefix = local.name_prefix
  root_domain = local.root_domain
  tags        = local.tags
}

# RDS Postgres (dev-scale)
module "rds" {
  source = "../../modules/rds"

  name_prefix       = local.name_prefix
  vpc_id            = module.vpc.vpc_id
  vpc_cidr_block    = module.vpc.vpc_cidr_block
  private_subnet_ids = module.vpc.private_subnet_ids

  db_name      = "genai"
  db_username  = "genai"
  db_password  = "ChangeMe123!" # DEV-ONLY, short-lived. In prod use Secrets Manager.
  instance_class   = "db.t3.micro"
  allocated_storage = 20

  tags = local.tags
}



# Redis (ElastiCache) – non-optional cache for this PoC
module "redis" {
  source = "../../modules/redis"

  name_prefix        = local.name_prefix
  vpc_id             = module.vpc.vpc_id
  vpc_cidr_block     = module.vpc.vpc_cidr_block
  private_subnet_ids = module.vpc.private_subnet_ids

  node_type      = "cache.t3.micro"
  engine_version = "7.0"

  tags = local.tags
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
