output "poc_metadata" {
  description = "Basic metadata for the Day32 d32-release dev environment."
  value = {
    poc_id      = local.poc_id
    day_label   = local.day_label
    environment = local.environment
    aws_region  = local.aws_region
    name_prefix = local.name_prefix
    api_fqdn    = local.api_fqdn
    model_fqdn  = local.model_fqdn
    ui_fqdn     = local.ui_fqdn
  }
}

# VPC
output "vpc_id" {
  description = "ID of the d32-release-dev VPC."
  value       = module.vpc.vpc_id
}

output "vpc_public_subnet_ids" {
  description = "Public subnet IDs."
  value       = module.vpc.public_subnet_ids
}

output "vpc_private_subnet_ids" {
  description = "Private subnet IDs."
  value       = module.vpc.private_subnet_ids
}

output "vpc_cidr_block" {
  description = "CIDR block of the VPC."
  value       = module.vpc.vpc_cidr_block
}

# Data plane
output "s3_docs_bucket_name" {
  description = "Name of the S3 docs bucket."
  value       = module.s3_docs.bucket_name
}

output "rds_endpoint" {
  description = "RDS Postgres endpoint."
  value       = module.rds.db_endpoint
}

output "redis_endpoint" {
  description = "Primary endpoint for Redis."
  value       = module.redis.primary_endpoint
}

# EKS
output "eks_cluster_name" {
  description = "Name of the EKS cluster."
  value       = module.eks.cluster_name
}

output "eks_cluster_endpoint" {
  description = "Endpoint for the EKS cluster."
  value       = module.eks.cluster_endpoint
}

output "eks_app_node_group_name" {
  description = "App node group name."
  value       = module.eks.app_node_group_name
}

output "eks_model_node_group_name" {
  description = "Model node group name."
  value       = module.eks.model_node_group_name
}

# ECR
output "ecr_api_repository_url" {
  description = "ECR URL for the API image."
  value       = module.ecr.api_repository_url
}

output "ecr_model_service_repository_url" {
  description = "ECR URL for the model service image."
  value       = module.ecr.model_service_repository_url
}

output "ecr_ui_repository_url" {
  description = "ECR URL for the UI image."
  value       = module.ecr.ui_repository_url
}
