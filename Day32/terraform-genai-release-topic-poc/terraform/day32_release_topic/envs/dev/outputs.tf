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

output "vpc_id" {
  description = "ID of the d32-release-dev VPC."
  value       = module.vpc.vpc_id
}

output "vpc_public_subnet_ids" {
  description = "Public subnet IDs for ALB / NAT / public-facing components."
  value       = module.vpc.public_subnet_ids
}

output "vpc_private_subnet_ids" {
  description = "Private subnet IDs for EKS nodes, RDS, Redis, etc."
  value       = module.vpc.private_subnet_ids
}

output "vpc_cidr_block" {
  description = "CIDR block of the d32-release-dev VPC."
  value       = module.vpc.vpc_cidr_block
}

output "s3_docs_bucket_name" {
  description = "Name of the S3 docs bucket."
  value       = module.s3_docs.bucket_name
}

output "rds_endpoint" {
  description = "RDS Postgres endpoint (hostname:port)."
  value       = module.rds.db_endpoint
}

output "redis_endpoint" {
  description = "Primary endpoint for Redis."
  value       = module.redis.primary_endpoint
}
