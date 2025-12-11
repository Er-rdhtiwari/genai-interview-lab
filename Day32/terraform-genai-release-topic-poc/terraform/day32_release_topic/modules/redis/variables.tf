variable "name_prefix" {
  description = "Name prefix for Redis resources (e.g. d32-release-dev)."
  type        = string
}

variable "vpc_id" {
  description = "VPC ID where Redis should live."
  type        = string
}

variable "vpc_cidr_block" {
  description = "CIDR block of the VPC (for SG inbound rules)."
  type        = string
}

variable "private_subnet_ids" {
  description = "List of private subnet IDs for the Redis subnet group."
  type        = list(string)
}

variable "node_type" {
  description = "ElastiCache node type."
  type        = string
  default     = "cache.t3.micro"
}

variable "engine_version" {
  description = "Redis engine version."
  type        = string
  default     = "7.0"
}

variable "tags" {
  description = "Tags to apply to Redis resources."
  type        = map(string)
  default     = {}
}
