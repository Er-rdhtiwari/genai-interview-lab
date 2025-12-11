variable "name_prefix" {
  description = "Name prefix for RDS resources (e.g. d32-release-dev)."
  type        = string
}

variable "vpc_id" {
  description = "VPC ID where RDS should live."
  type        = string
}

variable "vpc_cidr_block" {
  description = "CIDR block of the VPC (for SG inbound rules)."
  type        = string
}

variable "private_subnet_ids" {
  description = "List of private subnet IDs for the DB subnet group."
  type        = list(string)
}

variable "db_name" {
  description = "Initial database name."
  type        = string
  default     = "genai"
}

variable "db_username" {
  description = "Master username for the database."
  type        = string
  default     = "genai"
}

variable "db_password" {
  description = "Master password for the database (dev-only!)."
  type        = string
  sensitive   = true
  default     = "dev-test-only-password-123"
}

variable "instance_class" {
  description = "RDS instance class."
  type        = string
  default     = "db.t3.micro"
}

variable "allocated_storage" {
  description = "Allocated storage in GB."
  type        = number
  default     = 20
}

variable "tags" {
  description = "Tags to apply to RDS resources."
  type        = map(string)
  default     = {}
}
