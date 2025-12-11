output "db_endpoint" {
  description = "RDS Postgres endpoint (hostname:port)."
  value       = aws_db_instance.this.endpoint
}

output "db_address" {
  description = "RDS Postgres endpoint hostname."
  value       = aws_db_instance.this.address
}

output "db_port" {
  description = "RDS Postgres port."
  value       = aws_db_instance.this.port
}

output "security_group_id" {
  description = "Security group ID for RDS instance."
  value       = aws_security_group.this.id
}
