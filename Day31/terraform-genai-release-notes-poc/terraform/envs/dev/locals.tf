// Common naming and tagging conventions for the dev environment.

locals {
  name_prefix = "llm-${var.env}"

  common_tags = {
    app         = "terraform-genai-llm-poc"
    environment = var.env
    owner       = "platform-team" // change to your team/name if you like
  }
}
