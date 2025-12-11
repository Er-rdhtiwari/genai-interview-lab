locals {
  # Core identity
  poc_id      = "d32-release"
  day_label   = "DAY_32"
  environment = var.env_name

  aws_region = var.aws_region

  # Name prefix for all resources in this PoC + env
  # Example: d32-release-dev
  name_prefix = "${local.poc_id}-${local.environment}"

  # Standard tags applied to all resources
  tags = {
    app         = "genai-release-notes"
    component   = "day32-release-topic"
    poc         = local.poc_id
    environment = local.environment
    owner       = var.poc_owner
    day_label   = local.day_label
  }

  # DNS / FQDNs (non-optional for this PoC)
  root_domain = var.root_domain

  # We expose 3 externally reachable hostnames:
  # - API (FastAPI release-notes + greeting service)
  # - Model service (OSS model node group)
  # - UI (Streamlit front-end)
  api_subdomain   = "d32-release-${local.environment}-api"
  model_subdomain = "d32-release-${local.environment}-model"
  ui_subdomain    = "d32-release-${local.environment}-ui"

  api_fqdn   = "${local.api_subdomain}.${local.root_domain}"
  model_fqdn = "${local.model_subdomain}.${local.root_domain}"
  ui_fqdn    = "${local.ui_subdomain}.${local.root_domain}"
}
