provider "aws" {
  region = local.aws_region
}

# VPC: base network
module "vpc" {
  source = "../../modules/vpc"

  name_prefix = local.name_prefix     # e.g. d32-release-dev
  cidr_block  = "10.32.0.0/16"
  az_count    = 2
  tags        = local.tags
}

# S3 docs bucket
module "s3_docs" {
  source = "../../modules/s3_docs"

  name_prefix = local.name_prefix
  root_domain = local.root_domain
  tags        = local.tags
}

# RDS Postgres
module "rds" {
  source = "../../modules/rds"

  name_prefix        = local.name_prefix
  vpc_id             = module.vpc.vpc_id
  vpc_cidr_block     = module.vpc.vpc_cidr_block
  private_subnet_ids = module.vpc.private_subnet_ids

  db_name      = "genai"
  db_username  = "genai"
  db_password  = "ChangeMe123!" # DEV-ONLY
  instance_class    = "db.t3.micro"
  allocated_storage = 20

  tags = local.tags
}

# Redis (ElastiCache)
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

# EKS cluster with two node groups (app + model)
module "eks" {
  source = "../../modules/eks"

  name_prefix        = local.name_prefix
  vpc_id             = module.vpc.vpc_id
  private_subnet_ids = module.vpc.private_subnet_ids
  public_subnet_ids  = module.vpc.public_subnet_ids

  cluster_version = "1.29"

  node_instance_type_app   = "t3.medium"
  node_instance_type_model = "t3.medium"

  min_size_app     = 1
  desired_size_app = 1
  max_size_app     = 2

  min_size_model     = 1
  desired_size_model = 1
  max_size_model     = 2

  tags = local.tags
}

# ECR repositories for app, model service, and UI
module "ecr" {
  source = "../../modules/ecr"

  name_prefix = local.name_prefix
  tags        = local.tags
}


# ACM certificate for API, model, and UI FQDNs (DNS-validated via Route 53)
module "acm_cert" {
  source = "../../modules/acm_cert"

  root_domain = local.root_domain

  api_fqdn   = local.api_fqdn
  model_fqdn = local.model_fqdn
  ui_fqdn    = local.ui_fqdn

  tags = local.tags
}

# Route 53 DNS records mapping FQDNs -> ALB DNS names
# (records are created only when alb_dns_name_* variables are non-empty)
module "dns" {
  source = "../../modules/dns"

  root_domain = local.root_domain

  api_fqdn   = local.api_fqdn
  model_fqdn = local.model_fqdn
  ui_fqdn    = local.ui_fqdn

  alb_dns_name_api   = var.alb_dns_name_api
  alb_dns_name_model = var.alb_dns_name_model
  alb_dns_name_ui    = var.alb_dns_name_ui

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
