// Outputs for the RDS Postgres module.

output "db_endpoint" {
  description = "The connection endpoint for the RDS instance."
  value       = aws_db_instance.this.address
}

output "db_name" {
  description = "The initial database name."
  value       = aws_db_instance.this.db_name
}

output "db_username" {
  description = "The master username for the RDS instance."
  value       = aws_db_instance.this.username
}
