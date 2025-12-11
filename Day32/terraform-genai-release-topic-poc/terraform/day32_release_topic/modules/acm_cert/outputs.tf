output "certificate_arn" {
  description = "ARN of the validated ACM certificate."
  value       = aws_acm_certificate_validation.this.certificate_arn
}

output "route53_zone_id" {
  description = "ID of the Route 53 hosted zone used for validation."
  value       = data.aws_route53_zone.root.zone_id
}
