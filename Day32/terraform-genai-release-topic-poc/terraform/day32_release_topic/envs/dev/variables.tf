variable "aws_region" {
  description = "AWS region for Day32 d32-release dev environment."
  type        = string
  default     = "ap-south-1"
}

variable "root_domain" {
  description = "Root DNS domain used for this PoC (Route 53 hosted zone)."
  type        = string
  default     = "rdhcloudlab.com"
}

variable "env_name" {
  description = "Logical environment name (e.g. dev, prod)."
  type        = string
  default     = "dev"
}

variable "poc_owner" {
  description = "Owner tag for Day 32 PoC resources."
  type        = string
  default     = "radheshyam"
}
variable "alb_dns_name_api" {
  description = "ALB DNS name for the API Ingress (leave empty until ALB exists)."
  type        = string
  default     = ""
}

variable "alb_dns_name_model" {
  description = "ALB DNS name for the model-service Ingress (leave empty until ALB exists)."
  type        = string
  default     = ""
}

variable "alb_dns_name_ui" {
  description = "ALB DNS name for the UI Ingress (leave empty until ALB exists)."
  type        = string
  default     = ""
}
