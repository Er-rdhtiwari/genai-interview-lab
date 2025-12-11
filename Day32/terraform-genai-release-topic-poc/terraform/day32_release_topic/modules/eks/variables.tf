variable "name_prefix" {
  description = "Name prefix for EKS resources (e.g. d32-release-dev)."
  type        = string
}

variable "cluster_version" {
  description = "Kubernetes version for the EKS cluster."
  type        = string
  default     = "1.29"
}

variable "vpc_id" {
  description = "VPC ID where the EKS cluster will live."
  type        = string
}

variable "private_subnet_ids" {
  description = "Private subnet IDs for EKS worker nodes."
  type        = list(string)
}

variable "public_subnet_ids" {
  description = "Public subnet IDs (used later for ALB if needed)."
  type        = list(string)
}

variable "tags" {
  description = "Base tags to apply to all EKS-related resources."
  type        = map(string)
  default     = {}
}

variable "node_instance_type_app" {
  description = "Instance type for the app node group."
  type        = string
  default     = "t3.medium"
}

variable "node_instance_type_model" {
  description = "Instance type for the model node group."
  type        = string
  default     = "t3.medium"
}

variable "min_size_app" {
  description = "Minimum size of the app node group."
  type        = number
  default     = 1
}

variable "desired_size_app" {
  description = "Desired size of the app node group."
  type        = number
  default     = 1
}

variable "max_size_app" {
  description = "Maximum size of the app node group."
  type        = number
  default     = 2
}

variable "min_size_model" {
  description = "Minimum size of the model node group."
  type        = number
  default     = 1
}

variable "desired_size_model" {
  description = "Desired size of the model node group."
  type        = number
  default     = 1
}

variable "max_size_model" {
  description = "Maximum size of the model node group."
  type        = number
  default     = 2
}
