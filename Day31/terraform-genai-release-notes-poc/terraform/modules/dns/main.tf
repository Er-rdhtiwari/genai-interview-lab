// DNS module that *uses* an existing Route 53 hosted zone
// for var.root_domain and can optionally create api.<root_domain>.

data "aws_route53_zone" "this" {
  name         = var.root_domain
  private_zone = false
}

resource "aws_route53_record" "api" {
  count   = var.create_api_record ? 1 : 0
  zone_id = data.aws_route53_zone.this.zone_id
  name    = "api.${var.root_domain}"
  type    = "CNAME"
  ttl     = 60

  # Example future target: "my-alb-123456.ap-south-1.elb.amazonaws.com"
  records = [var.api_record_target]

  depends_on = [data.aws_route53_zone.this]
}
