// Input variables for the dev environment root module.

variable "env" {
  type        = string
  description = "Deployment environment (e.g. dev, stage, prod)."
  default     = "dev"
}

variable "aws_region" {
  type        = string
  description = "AWS region to deploy into."
  default     = "ap-south-1"
}

variable "root_domain" {
  type        = string
  description = "Root domain for the hosted zone (e.g. example.com)."
  default     = "example.com"
}
