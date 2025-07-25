# Name to assign to the DynamoDB table
variable "table_name" {
  description = "Name for the DynamoDB table"
  type        = string
}

# AWS region where the DynamoDB table and related resources reside
variable "aws_region" {
  description = "AWS region for DynamoDB ARN"
  type        = string
}

# ARN of the KMS key used to encrypt the DynamoDB table
variable "kms_key_arn" {
  description = "ARN of the KMS key for encryption"
  type        = string
}
