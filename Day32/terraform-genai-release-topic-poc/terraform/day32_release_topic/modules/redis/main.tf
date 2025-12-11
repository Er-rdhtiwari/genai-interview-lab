locals {
  tags = merge(
    var.tags,
    {
      component = "redis-cache"
    }
  )
}

# Security group: allow Redis (6379) only from within VPC.
resource "aws_security_group" "this" {
  name        = "${var.name_prefix}-redis-sg"
  description = "Security group for Day32 Redis"
  vpc_id      = var.vpc_id

  ingress {
    description = "Redis from VPC"
    from_port   = 6379
    to_port     = 6379
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr_block]
  }

  egress {
    description = "All outbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(
    local.tags,
    {
      Name = "${var.name_prefix}-redis-sg"
    }
  )
}

resource "aws_elasticache_subnet_group" "this" {
  name       = "${var.name_prefix}-redis-subnets"
  subnet_ids = var.private_subnet_ids

  tags = merge(
    local.tags,
    {
      Name = "${var.name_prefix}-redis-subnets"
    }
  )
}

resource "aws_elasticache_cluster" "this" {
  cluster_id           = "${var.name_prefix}-redis"
  engine               = "redis"
  engine_version       = var.engine_version
  node_type            = var.node_type
  num_cache_nodes      = 1
  port                 = 6379
  subnet_group_name    = aws_elasticache_subnet_group.this.name
  security_group_ids   = [aws_security_group.this.id]
  parameter_group_name = "default.redis7"

  tags = merge(
    local.tags,
    {
      Name = "${var.name_prefix}-redis"
    }
  )
}
