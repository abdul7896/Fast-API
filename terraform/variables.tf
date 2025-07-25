# AWS region where resources will be created
variable "region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

# Name of the S3 bucket for storing avatars or other assets
variable "s3_bucket_name" {
  description = "Name for the S3 bucket"
  type        = string
  default     = "prima-avatars-bucket"
}

# Name of the DynamoDB table for application data (e.g., users)
variable "dynamodb_table_name" {
  description = "Name for the DynamoDB table"
  type        = string
  default     = "users"
}

# Alias name for the KMS key used for encryption
variable "kms_key_alias" {
  description = "Alias for the KMS key"
  type        = string
  default     = "prima-api-key-alias"
}

# DynamoDB table name used specifically for Terraform state locking
variable "backend_dynamodb_table_name" {
  description = "DynamoDB table name for Terraform state locking"
  type        = string
  default     = "terraform-lock-table"
}

# S3 bucket name used specifically for storing Terraform state files
variable "backend_bucket_name" {
  description = "S3 bucket name for Terraform state"
  type        = string
  default     = "my-prima-tf-state9278"
}
