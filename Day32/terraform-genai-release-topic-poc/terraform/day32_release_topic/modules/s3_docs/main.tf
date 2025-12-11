locals {
  # S3 bucket names must be globally unique and only allow lowercase + '-'.
  # We derive a name from root_domain + name_prefix:
  # e.g. rdhcloudlab-com-d32-release-dev-docs
  bucket_name = lower(
    replace("${var.root_domain}-${var.name_prefix}-docs", ".", "-")
  )

  tags = merge(
    var.tags,
    {
      component = "s3-docs"
    }
  )
}

resource "aws_s3_bucket" "this" {
  bucket = local.bucket_name

  tags = merge(
    local.tags,
    {
      Name = "${var.name_prefix}-docs-bucket"
    }
  )
}

resource "aws_s3_bucket_versioning" "this" {
  bucket = aws_s3_bucket.this.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_public_access_block" "this" {
  bucket = aws_s3_bucket.this.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
