# terraform/modules/dynamodb/variables.tf
variable "table_name" {
  description = "Name for the DynamoDB table"
  type        = string
}

variable "aws_region" {
  description = "AWS region for DynamoDB ARN"
  type        = string
}

variable "kms_key_arn" {
  description = "ARN of the KMS key for encryption"
  type        = string
}