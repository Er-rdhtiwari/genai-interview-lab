output "cluster_name" {
  description = "Name of the EKS cluster."
  value       = aws_eks_cluster.this.name
}

output "cluster_endpoint" {
  description = "Endpoint for the EKS cluster API server."
  value       = aws_eks_cluster.this.endpoint
}

output "cluster_ca_certificate" {
  description = "Base64-encoded certificate data required to communicate with the cluster."
  value       = aws_eks_cluster.this.certificate_authority[0].data
}

output "cluster_security_group_id" {
  description = "Security group ID for the EKS cluster."
  value       = aws_security_group.cluster.id
}

output "node_security_group_id" {
  description = "Security group ID for worker nodes."
  value       = aws_security_group.node.id
}

output "app_node_group_name" {
  description = "Name of the app node group."
  value       = aws_eks_node_group.app.node_group_name
}

output "model_node_group_name" {
  description = "Name of the model node group."
  value       = aws_eks_node_group.model.node_group_name
}
