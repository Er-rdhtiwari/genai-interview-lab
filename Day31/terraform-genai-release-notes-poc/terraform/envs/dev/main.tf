// Root module for the dev environment.
// Wires providers and modules for S3, and later RDS + Route 53.

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
}

# Used to make S3 bucket names globally unique per AWS account.
data "aws_caller_identity" "current" {}

module "s3_docs" {
  source = "../../modules/s3_docs"

  # Example: llm-dev-123456789012-docs
  bucket_name = "${local.name_prefix}-${data.aws_caller_identity.current.account_id}-docs"
  tags        = local.common_tags
}

module "rds" {
  source = "../../modules/rds"

  name_prefix = local.name_prefix
  db_name     = var.db_name
  db_username = var.db_username
  db_password = var.db_password

  instance_class    = "db.t3.micro"
  allocated_storage = 20

  tags = local.common_tags
}
