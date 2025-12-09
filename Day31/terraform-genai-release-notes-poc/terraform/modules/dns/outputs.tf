// Outputs for DNS (Route 53) module.

output "zone_id" {
  description = "The ID of the Route 53 hosted zone."
  value       = data.aws_route53_zone.this.zone_id
}

output "zone_name" {
  description = "The name of the Route 53 hosted zone."
  value       = data.aws_route53_zone.this.name
}

output "api_fqdn" {
  description = "The FQDN of the API endpoint (logical), even if not created yet."
  value       = "api.${var.root_domain}"
}
