# IAM role for EKS cluster
resource "aws_iam_role" "cluster" {
  name = "${var.name_prefix}-eks-cluster-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "eks.amazonaws.com"
      }
    }]
  })

  tags = local.tags
}

resource "aws_iam_role_policy_attachment" "cluster_policy" {
  role       = aws_iam_role.cluster.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
}

# Security group for EKS cluster control plane
resource "aws_security_group" "cluster" {
  name        = "${var.name_prefix}-eks-cluster-sg"
  description = "Security group for Day32 EKS cluster control plane"
  vpc_id      = var.vpc_id

  # EKS control plane manages its own rules; leave broad outbound.
  egress {
    description = "Allow all outbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(
    local.tags,
    {
      Name = "${var.name_prefix}-eks-cluster-sg"
    }
  )
}

# EKS cluster
resource "aws_eks_cluster" "this" {
  name     = local.cluster_name
  role_arn = aws_iam_role.cluster.arn
  version  = var.cluster_version

  vpc_config {
    subnet_ids = concat(var.private_subnet_ids, var.public_subnet_ids)
    security_group_ids = [
      aws_security_group.cluster.id
    ]
  }

  tags = local.tags

  depends_on = [
    aws_iam_role_policy_attachment.cluster_policy
  ]
}

# IAM role for worker node groups
resource "aws_iam_role" "node" {
  name = "${var.name_prefix}-eks-node-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Service = "ec2.amazonaws.com"
      }
      Action = "sts:AssumeRole"
    }]
  })

  tags = local.tags
}

# Attach necessary policies for nodes (EKS Worker, CNI, ECR, CloudWatch)
resource "aws_iam_role_policy_attachment" "node_worker" {
  role       = aws_iam_role.node.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy"
}

resource "aws_iam_role_policy_attachment" "node_cni" {
  role       = aws_iam_role.node.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy"
}

resource "aws_iam_role_policy_attachment" "node_ecr" {
  role       = aws_iam_role.node.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
}

resource "aws_iam_role_policy_attachment" "node_cloudwatch" {
  role       = aws_iam_role.node.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy"
}

# Security group for worker nodes
resource "aws_security_group" "node" {
  name        = "${var.name_prefix}-eks-node-sg"
  description = "Security group for Day32 EKS worker nodes"
  vpc_id      = var.vpc_id

  # Nodes talk to each other and to cluster
  ingress {
    description = "Allow all node-to-node traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    self        = true
  }

  egress {
    description = "Allow all outbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(
    local.tags,
    {
      Name = "${var.name_prefix}-eks-node-sg"
    }
  )
}

# ------------------------
# Node Group: App
# ------------------------

resource "aws_eks_node_group" "app" {
  cluster_name    = aws_eks_cluster.this.name
  node_group_name = "${var.name_prefix}-app-nodes"
  node_role_arn   = aws_iam_role.node.arn
  subnet_ids      = var.private_subnet_ids

  scaling_config {
    desired_size = var.desired_size_app
    max_size     = var.max_size_app
    min_size     = var.min_size_app
  }

  instance_types = [var.node_instance_type_app]

  # Labels let us target this node group from Deployments
  labels = {
    "role"        = "app"
    "poc"         = "d32-release"
    "environment" = "dev"
  }

  tags = merge(
    local.tags,
    {
      Name     = "${var.name_prefix}-app-nodes"
      NodeRole = "app"
    }
  )

  depends_on = [
    aws_eks_cluster.this,
    aws_iam_role_policy_attachment.node_worker,
    aws_iam_role_policy_attachment.node_cni,
    aws_iam_role_policy_attachment.node_ecr,
    aws_iam_role_policy_attachment.node_cloudwatch,
  ]
}

# ------------------------
# Node Group: Model
# ------------------------

resource "aws_eks_node_group" "model" {
  cluster_name    = aws_eks_cluster.this.name
  node_group_name = "${var.name_prefix}-model-nodes"
  node_role_arn   = aws_iam_role.node.arn
  subnet_ids      = var.private_subnet_ids

  scaling_config {
    desired_size = var.desired_size_model
    max_size     = var.max_size_model
    min_size     = var.min_size_model
  }

  instance_types = [var.node_instance_type_model]

  labels = {
    "role"        = "model"
    "poc"         = "d32-release"
    "environment" = "dev"
  }

  tags = merge(
    local.tags,
    {
      Name     = "${var.name_prefix}-model-nodes"
      NodeRole = "model"
    }
  )

  depends_on = [
    aws_eks_cluster.this,
    aws_iam_role_policy_attachment.node_worker,
    aws_iam_role_policy_attachment.node_cni,
    aws_iam_role_policy_attachment.node_ecr,
    aws_iam_role_policy_attachment.node_cloudwatch,
  ]
}
