# AWS Configuration
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "development"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "prima-api"
}

# EKS Configuration
variable "cluster_name" {
  description = "Name of the EKS cluster"
  type        = string
  default     = "prima-api-cluster"
}

variable "kubernetes_version" {
  description = "Kubernetes version"
  type        = string
  default     = "1.28"
}

# VPC Configuration
variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "private_subnets" {
  description = "Private subnet CIDR blocks"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
}

variable "public_subnets" {
  description = "Public subnet CIDR blocks"
  type        = list(string)
  default     = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]
}

# Legacy variables for backward compatibility
variable "region" {
  description = "AWS region (legacy variable name)"
  type        = string
  default     = "us-east-1"
}

variable "backend_bucket_name" {
  description = "S3 bucket name for Terraform backend"
  type        = string
  default     = "prima-api-terraform-state"
}

variable "backend_dynamodb_table_name" {
  description = "DynamoDB table name for Terraform state locking"
  type        = string
  default     = "prima-api-terraform-lock"
}

variable "s3_bucket_name" {
  description = "S3 bucket name for application data"
  type        = string
  default     = "prima-api-avatars"
}

variable "dynamodb_table_name" {
  description = "DynamoDB table name for application data"
  type        = string
  default     = "prima-api-users"
}

variable "kms_key_alias" {
  description = "KMS key alias"
  type        = string
  default     = "alias/prima-api-key"
}
