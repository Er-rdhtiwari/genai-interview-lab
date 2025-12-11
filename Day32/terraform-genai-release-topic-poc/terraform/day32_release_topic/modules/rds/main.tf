locals {
  tags = merge(
    var.tags,
    {
      component = "rds-postgres"
    }
  )
}

# Security group: allow Postgres (5432) from within the VPC CIDR only.
resource "aws_security_group" "this" {
  name        = "${var.name_prefix}-rds-sg"
  description = "Security group for Day32 RDS Postgres"
  vpc_id      = var.vpc_id

  ingress {
    description = "Postgres from VPC"
    from_port   = 5432
    to_port     = 5432
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
      Name = "${var.name_prefix}-rds-sg"
    }
  )
}

resource "aws_db_subnet_group" "this" {
  name       = "${var.name_prefix}-rds-subnets"
  subnet_ids = var.private_subnet_ids

  tags = merge(
    local.tags,
    {
      Name = "${var.name_prefix}-rds-subnets"
    }
  )
}

resource "aws_db_instance" "this" {
  identifier        = "${var.name_prefix}-postgres"
  engine            = "postgres"
  instance_class    = var.instance_class
  allocated_storage = var.allocated_storage

  db_name  = var.db_name
  username = var.db_username
  password = var.db_password

  storage_encrypted      = true
  skip_final_snapshot    = true
  deletion_protection    = false
  multi_az               = false
  publicly_accessible    = false
  backup_retention_period = 1

  db_subnet_group_name   = aws_db_subnet_group.this.name
  vpc_security_group_ids = [aws_security_group.this.id]

  tags = merge(
    local.tags,
    {
      Name = "${var.name_prefix}-postgres"
    }
  )
}
