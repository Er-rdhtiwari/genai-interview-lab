// Outputs for the dev environment.
// In later parts, we will expose:
// - docs_bucket_name (from S3 module)
// - db_endpoint, db_name (from RDS module)
// - api_fqdn (from DNS module)

// Outputs for the dev environment.

output "docs_bucket_name" {
  description = "Name of the S3 docs bucket."
  value       = module.s3_docs.bucket_name
}

output "db_endpoint" {
  description = "Endpoint of the dev Postgres RDS instance."
  value       = module.rds.db_endpoint
}

output "db_name" {
  description = "Database name of the dev Postgres RDS instance."
  value       = module.rds.db_name
}

output "db_username" {
  description = "Master username of the dev Postgres RDS instance."
  value       = module.rds.db_username
}
