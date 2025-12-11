output "zone_id" {
  description = "ID of the Route 53 hosted zone."
  value       = data.aws_route53_zone.root.zone_id
}

output "api_record_fqdn" {
  description = "FQDN of the API DNS record, if created."
  value       = try(aws_route53_record.api[0].fqdn, null)
}

output "model_record_fqdn" {
  description = "FQDN of the model-service DNS record, if created."
  value       = try(aws_route53_record.model[0].fqdn, null)
}

output "ui_record_fqdn" {
  description = "FQDN of the UI DNS record, if created."
  value       = try(aws_route53_record.ui[0].fqdn, null)
}
