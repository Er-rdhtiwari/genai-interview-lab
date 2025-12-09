// Input variables for the S3 docs bucket module.

variable "bucket_name" {
  type        = string
  description = "Name of the S3 bucket to create (must be globally unique)."
}

variable "tags" {
  type        = map(string)
  description = "Common tags to apply to the bucket and related resources."
  default     = {}
}
