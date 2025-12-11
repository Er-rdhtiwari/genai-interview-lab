output "vpc_id" {
  description = "ID of the VPC."
  value       = aws_vpc.this.id
}

output "public_subnet_ids" {
  description = "IDs of the public subnets."
  value       = [for s in aws_subnet.public : s.id]
}

output "private_subnet_ids" {
  description = "IDs of the private subnets."
  value       = [for s in aws_subnet.private : s.id]
}

output "public_subnet_cidrs" {
  description = "CIDRs of the public subnets."
  value       = [for s in aws_subnet.public : s.cidr_block]
}

output "private_subnet_cidrs" {
  description = "CIDRs of the private subnets."
  value       = [for s in aws_subnet.private : s.cidr_block]
}

output "vpc_cidr_block" {
  description = "CIDR block of the VPC."
  value       = aws_vpc.this.cidr_block
}
