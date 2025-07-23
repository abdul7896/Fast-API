variable "region" {
  description = "AWS region"
  type        = string
}

variable "s3_bucket_name" {
  description = "Name for the S3 bucket"
  type        = string
  default     = "prima-avatars-bucket"
}

variable "dynamodb_table_name" {
  description = "Name for the DynamoDB table"
  type        = string
  default     = "users"
}

variable "kms_key_alias" {
  description = "Alias for the KMS key"
  type        = string
  default     = "prima-api-key-alias"
}
