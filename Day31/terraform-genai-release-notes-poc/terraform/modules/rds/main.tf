// Minimal Postgres RDS instance in the default VPC.
// - Uses default subnets for DB subnet group
// - Has its own security group
// - Not publicly accessible by default

data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default_vpc_subnets" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

resource "aws_db_subnet_group" "this" {
  name       = "${var.name_prefix}-db-subnet-group"
  subnet_ids = data.aws_subnets.default_vpc_subnets.ids

  tags = merge(
    var.tags,
    {
      "component" = "rds-subnet-group"
    }
  )
}

resource "aws_security_group" "this" {
  name        = "${var.name_prefix}-db-sg"
  description = "Security group for ${var.name_prefix} Postgres RDS instance"
  vpc_id      = data.aws_vpc.default.id

  # For this PoC we only define egress; no ingress rules,
  # so the DB is not reachable from outside by default.
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(
    var.tags,
    {
      "component" = "rds-security-group"
    }
  )
}

resource "aws_db_instance" "this" {
  identifier = "${var.name_prefix}-postgres"

  engine         = "postgres"
  # engine_version = "16.3"
  # Let AWS pick the default supported engine version for postgres.
  # If you want a specific version later, set engine_version explicitly
  # to a value you know is supported in this region.

  instance_class    = var.instance_class
  allocated_storage = var.allocated_storage

  db_name  = var.db_name
  username = var.db_username
  password = var.db_password

  db_subnet_group_name   = aws_db_subnet_group.this.name
  vpc_security_group_ids = [aws_security_group.this.id]

  publicly_accessible = false
  multi_az            = false

  skip_final_snapshot = true
  deletion_protection = false

  apply_immediately = true

  tags = merge(
    var.tags,
    {
      "component" = "rds-postgres"
    }
  )
}
