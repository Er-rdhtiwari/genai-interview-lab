// Input variables for the RDS Postgres module.

variable "name_prefix" {
  type        = string
  description = "Prefix used for RDS identifiers (e.g., llm-dev)."
}

variable "db_name" {
  type        = string
  description = "Initial database name."
}

variable "db_username" {
  type        = string
  description = "Master username for the RDS instance."
}

variable "db_password" {
  type        = string
  description = "Master password for the RDS instance."
  sensitive   = true
}

variable "instance_class" {
  type        = string
  description = "Instance class for the RDS instance."
  default     = "db.t3.micro"
}

variable "allocated_storage" {
  type        = number
  description = "Allocated storage (in GB) for the RDS instance."
  default     = 20
}

variable "tags" {
  type        = map(string)
  description = "Common tags to apply to RDS resources."
  default     = {}
}
