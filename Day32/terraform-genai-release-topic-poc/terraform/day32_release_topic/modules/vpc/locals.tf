locals {
  # Use the first `az_count` AZs in the region.
  # Example in ap-south-1: ap-south-1a, ap-south-1b, ...
  azs = slice(data.aws_availability_zones.available.names, 0, var.az_count)

  # Derive subnet CIDRs using cidrsubnet.
  # We split the /16 into 4 /20s:
  # - 0,1 -> public
  # - 2,3 -> private
  # cidrsubnet("10.32.0.0/16", 4, 0) -> 10.32.0.0/20
  # cidrsubnet("10.32.0.0/16", 4, 1) -> 10.32.16.0/20
  public_subnet_cidrs = [
    cidrsubnet(var.cidr_block, 4, 0),
    cidrsubnet(var.cidr_block, 4, 1),
  ]

  private_subnet_cidrs = [
    cidrsubnet(var.cidr_block, 4, 2),
    cidrsubnet(var.cidr_block, 4, 3),
  ]

  common_tags = merge(
    var.tags,
    {
      component = "vpc"
    }
  )
}
