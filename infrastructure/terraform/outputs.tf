output "vpc_id" {
  description = "VPC ID"
  value       = module.vpc.vpc_id
}

output "private_subnet_ids" {
  description = "Private subnet IDs"
  value       = module.vpc.private_subnets
}

output "public_subnet_ids" {
  description = "Public subnet IDs"
  value       = module.vpc.public_subnets
}

output "cluster_endpoint" {
  description = "EKS cluster endpoint"
  value       = module.eks.cluster_endpoint
}

output "cluster_certificate_authority_data" {
  description = "EKS cluster certificate authority data"
  value       = module.eks.cluster_certificate_authority_data
}

output "cluster_name" {
  description = "EKS cluster name"
  value       = module.eks.cluster_name
}

output "s3_bucket_name" {
  description = "S3 bucket name for avatars"
  value       = aws_s3_bucket.prima_avatars.bucket
}

output "s3_bucket_arn" {
  description = "S3 bucket ARN for avatars"
  value       = aws_s3_bucket.prima_avatars.arn
}

output "dynamodb_table_name" {
  description = "DynamoDB table name for users"
  value       = aws_dynamodb_table.users.name
}

output "dynamodb_table_arn" {
  description = "DynamoDB table ARN for users"
  value       = aws_dynamodb_table.users.arn
}

output "alb_dns_name" {
  description = "ALB DNS name"
  value       = aws_lb.prima_api.dns_name
}

output "alb_arn" {
  description = "ALB ARN"
  value       = aws_lb.prima_api.arn
}

output "kms_key_arn" {
  description = "KMS key ARN for application data"
  value       = aws_kms_key.app_data.arn
}

output "iam_role_arn" {
  description = "IAM role ARN for Prima API service"
  value       = aws_iam_role.prima_api_service_role.arn
}