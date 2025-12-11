locals {
  tags = merge(
    var.tags,
    {
      component = "ecr"
    }
  )
}

resource "aws_ecr_repository" "api" {
  name                 = "${var.name_prefix}-api"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = merge(
    local.tags,
    {
      Name = "${var.name_prefix}-api"
      Role = "api"
    }
  )
}

resource "aws_ecr_repository" "model_service" {
  name                 = "${var.name_prefix}-model-service"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = merge(
    local.tags,
    {
      Name = "${var.name_prefix}-model-service"
      Role = "model-service"
    }
  )
}

resource "aws_ecr_repository" "ui" {
  name                 = "${var.name_prefix}-ui"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = merge(
    local.tags,
    {
      Name = "${var.name_prefix}-ui"
      Role = "ui"
    }
  )
}
