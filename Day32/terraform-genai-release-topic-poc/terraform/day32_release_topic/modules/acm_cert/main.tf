locals {
  tags = merge(
    var.tags,
    {
      component = "acm-cert"
    }
  )
}

# Look up the public hosted zone for the root domain.
data "aws_route53_zone" "root" {
  name         = var.root_domain
  private_zone = false
}

# Request ACM certificate with DNS validation.
resource "aws_acm_certificate" "this" {
  domain_name               = var.root_domain
  subject_alternative_names = [
    var.api_fqdn,
    var.model_fqdn,
    var.ui_fqdn,
  ]
  validation_method = "DNS"

  tags = merge(
    local.tags,
    {
      Name = "${var.root_domain}-d32-release-cert"
    }
  )
}

# Create DNS validation records in Route 53.
resource "aws_route53_record" "validation" {
  for_each = {
    for dvo in aws_acm_certificate.this.domain_validation_options :
    dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  }

  zone_id = data.aws_route53_zone.root.zone_id
  name    = each.value.name
  type    = each.value.type
  ttl     = 300
  records = [each.value.record]
}

# Wait for validation to complete.
resource "aws_acm_certificate_validation" "this" {
  certificate_arn = aws_acm_certificate.this.arn
  validation_record_fqdns = [
    for record in aws_route53_record.validation : record.fqdn
  ]
}

