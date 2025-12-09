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
variable "db_username" {
  type        = string
  description = "Master username for the dev Postgres instance."
  default     = "llm_user"
}

variable "db_name" {
  type        = string
  description = "Database name for the dev Postgres instance."
  default     = "llm_poc"
}

variable "db_password" {
  type        = string
  description = "Master password for the dev Postgres instance."
  sensitive   = true
}
