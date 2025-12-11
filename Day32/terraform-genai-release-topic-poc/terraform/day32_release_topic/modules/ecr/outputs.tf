output "api_repository_url" {
  description = "ECR URL for the API image."
  value       = aws_ecr_repository.api.repository_url
}

output "model_service_repository_url" {
  description = "ECR URL for the model service image."
  value       = aws_ecr_repository.model_service.repository_url
}

output "ui_repository_url" {
  description = "ECR URL for the Streamlit UI image."
  value       = aws_ecr_repository.ui.repository_url
}
