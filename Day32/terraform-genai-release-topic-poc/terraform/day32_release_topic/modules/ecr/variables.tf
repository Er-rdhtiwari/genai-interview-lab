variable "name_prefix" {
  description = "Name prefix for ECR repositories (e.g. d32-release-dev)."
  type        = string
}

variable "tags" {
  description = "Tags to apply to ECR repositories."
  type        = map(string)
  default     = {}
}
