// Input variables for DNS (Route 53) module that uses an existing hosted zone.

variable "root_domain" {
  type        = string
  description = "Root domain for the hosted zone (e.g. rdhcloudlab.com)."
}

variable "tags" {
  type        = map(string)
  description = "Common tags to apply to DNS-related resources."
  default     = {}
}

variable "create_api_record" {
  type        = bool
  description = "Whether to create an api.<root_domain> record."
  default     = false
}

variable "api_record_target" {
  type        = string
  description = "Target for api.<root_domain> (e.g. ALB/App Runner DNS name)."
  default     = ""
}
