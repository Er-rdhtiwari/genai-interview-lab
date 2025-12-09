// Root module for the dev environment.
// Wires providers and (in later parts) calls the S3, RDS, and DNS modules.

terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region

  # Credentials are picked up from your environment or shared config:
  # - AWS_PROFILE
  # - AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY
  # - ~/.aws/credentials, etc.
}
