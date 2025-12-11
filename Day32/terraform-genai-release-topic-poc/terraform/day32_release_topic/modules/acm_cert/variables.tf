variable "root_domain" {
  description = "Root DNS domain that has a public Route 53 hosted zone (e.g. rdhcloudlab.com)."
  type        = string
}

variable "api_fqdn" {
  description = "FQDN for the API endpoint."
  type        = string
}

variable "model_fqdn" {
  description = "FQDN for the model service endpoint."
  type        = string
}

variable "ui_fqdn" {
  description = "FQDN for the Streamlit UI endpoint."
  type        = string
}

variable "tags" {
  description = "Tags to apply to ACM-related resources."
  type        = map(string)
  default     = {}
}
