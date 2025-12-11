terraform {
  required_version = ">= 1.6.0"

  # Local backend for this PoC.
  # State file path is namespaced under terraform/day32_release_topic/state/dev.
  backend "local" {
    path = "../state/dev/terraform.tfstate"
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}
