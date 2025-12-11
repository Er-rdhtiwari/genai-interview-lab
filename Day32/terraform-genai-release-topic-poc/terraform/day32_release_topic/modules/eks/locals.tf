locals {
  cluster_name = "${var.name_prefix}-eks"

  tags = merge(
    var.tags,
    {
      component = "eks"
    }
  )
}
