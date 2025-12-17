provider "aws" {
  region = var.aws_region
}

data "aws_availability_zones" "available" {
  state = "available"
}

locals {
  name       = "d33-oss-prod-eks"
  vpc_cidr   = "10.33.0.0/16"
  azs        = slice(data.aws_availability_zones.available.names, 0, 2)
  tags = {
    PoC         = "d33-oss-prod"
    Environment = "prod"
    Terraform   = "true"
  }
}
