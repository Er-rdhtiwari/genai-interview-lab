variable "name_prefix" {
  description = "Name prefix for all VPC-related resources (e.g. d32-release-dev)."
  type        = string
}

variable "cidr_block" {
  description = "CIDR block for the VPC."
  type        = string
  default     = "10.32.0.0/16"
}

variable "az_count" {
  description = "Number of availability zones to use (2 recommended for this PoC)."
  type        = number
  default     = 2
}

variable "tags" {
  description = "Base tags to apply to all resources."
  type        = map(string)
  default     = {}
}
