# AWS region where backend resources (S3, DynamoDB, KMS) will be created
variable "region" {
  description = "AWS region for backend resources"
  type        = string
  default     = "us-east-1"
}

# Name of the S3 bucket to store the Terraform remote state
variable "bucket_name" {
  description = "S3 bucket name for Terraform state"
  type        = string
  default     = "my-prima-tf-state9278"
}

# Name of the DynamoDB table used for Terraform state locking
variable "dynamodb_table_name" {
  description = "DynamoDB table name for Terraform state locking"
  type        = string
  default     = "terraform-lock-table"
}

# ARN of the KMS key used to encrypt the Terraform state in S3
variable "kms_key_arn" {
  description = "ARN of the KMS key for encryption"
  type        = string
}
