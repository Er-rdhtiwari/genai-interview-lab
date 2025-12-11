variable "root_domain" {
  description = "Root DNS domain (e.g. rdhcloudlab.com)."
  type        = string
}

variable "api_fqdn" {
  description = "FQDN for the API endpoint."
  type        = string
}

variable "model_fqdn" {
  description = "FQDN for the model service endpoint."
  type        = string
}

variable "ui_fqdn" {
  description = "FQDN for the UI endpoint."
  type        = string
}

# ALB DNS names for each component.
# These come from the AWS console or `kubectl get ingress` after ALB is created
# by AWS Load Balancer Controller.
variable "alb_dns_name_api" {
  description = "ALB DNS name for the API Ingress (e.g. xyz.ap-south-1.elb.amazonaws.com)."
  type        = string
  default     = ""
}

variable "alb_dns_name_model" {
  description = "ALB DNS name for the model-service Ingress."
  type        = string
  default     = ""
}

variable "alb_dns_name_ui" {
  description = "ALB DNS name for the UI Ingress."
  type        = string
  default     = ""
}

variable "tags" {
  description = "Tags to apply to Route 53 records."
  type        = map(string)
  default     = {}
}
