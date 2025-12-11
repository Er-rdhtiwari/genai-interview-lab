variable "name_prefix" {
  description = "Name prefix for the docs bucket (e.g. d32-release-dev)."
  type        = string
}

variable "root_domain" {
  description = "Root DNS domain; used to build a reasonably unique bucket name."
  type        = string
}

variable "tags" {
  description = "Tags to apply to the bucket."
  type        = map(string)
  default     = {}
}
