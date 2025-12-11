locals {
  tags = merge(
    var.tags,
    {
      component = "dns"
    }
  )
}

data "aws_route53_zone" "root" {
  name         = var.root_domain
  private_zone = false
}

# API CNAME -> ALB DNS (created if alb_dns_name_api is non-empty)
resource "aws_route53_record" "api" {
  count = length(var.alb_dns_name_api) > 0 ? 1 : 0

  zone_id = data.aws_route53_zone.root.zone_id
  name    = var.api_fqdn
  type    = "CNAME"
  ttl     = 60

  records = [var.alb_dns_name_api]
}

# Model service CNAME -> ALB DNS
resource "aws_route53_record" "model" {
  count = length(var.alb_dns_name_model) > 0 ? 1 : 0

  zone_id = data.aws_route53_zone.root.zone_id
  name    = var.model_fqdn
  type    = "CNAME"
  ttl     = 60

  records = [var.alb_dns_name_model]
}

# UI CNAME -> ALB DNS
resource "aws_route53_record" "ui" {
  count = length(var.alb_dns_name_ui) > 0 ? 1 : 0

  zone_id = data.aws_route53_zone.root.zone_id
  name    = var.ui_fqdn
  type    = "CNAME"
  ttl     = 60

  records = [var.alb_dns_name_ui]
}
