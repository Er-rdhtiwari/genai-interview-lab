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
