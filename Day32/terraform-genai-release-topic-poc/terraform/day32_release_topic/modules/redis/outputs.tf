output "primary_endpoint" {
  description = "Primary endpoint for the Redis cluster."
  value       = "${aws_elasticache_cluster.this.cache_nodes[0].address}:${aws_elasticache_cluster.this.cache_nodes[0].port}"
}

output "port" {
  description = "Redis port."
  value       = aws_elasticache_cluster.this.port
}

output "security_group_id" {
  description = "Security group ID for Redis."
  value       = aws_security_group.this.id
}
