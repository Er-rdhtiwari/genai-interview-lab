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

  # Credentials are picked up from your environment or shared config:
  # - IAM role attached to this EC2 instance
  # - AWS_PROFILE
  # - AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY
  # - ~/.aws/credentials, etc.
}

# Used to make S3 bucket names globally unique per AWS account.
data "aws_caller_identity" "current" {}

module "s3_docs" {
  source = "../../modules/s3_docs"

  # Example: llm-dev-123456789012-docs
  bucket_name = "${local.name_prefix}-${data.aws_caller_identity.current.account_id}-docs"
  tags        = local.common_tags
}
