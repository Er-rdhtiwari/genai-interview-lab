module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 21.0"

  name               = local.name
  kubernetes_version = "1.29"

  endpoint_public_access                   = true
  enable_cluster_creator_admin_permissions = true

  vpc_id     = module.vpc.vpc_id
  # before
  subnet_ids = module.vpc.private_subnets
  # after (temporary)
  subnet_ids = module.vpc.public_subnets

  eks_managed_node_groups = {
    core = {
      ami_type       = "AL2023_x86_64_STANDARD"
      instance_types = ["t3.medium"]
      min_size       = 1
      max_size       = 3
      desired_size   = 2
      labels         = { pool = "core" }
    }

    model = {
      ami_type       = "AL2_x86_64"
      instance_types = ["m5.xlarge"]
      min_size       = 0
      max_size       = 2
      desired_size   = 1
      labels         = { pool = "model" }
    }
  }

  tags = local.tags
}
