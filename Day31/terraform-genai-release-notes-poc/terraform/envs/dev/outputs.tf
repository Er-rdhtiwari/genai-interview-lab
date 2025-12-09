// Outputs for the dev environment.
// In later parts, we will expose:
// - docs_bucket_name (from S3 module)
// - db_endpoint, db_name (from RDS module)
// - api_fqdn (from DNS module)

output "docs_bucket_name" {
  description = "Name of the S3 docs bucket."
  value       = module.s3_docs.bucket_name
}
