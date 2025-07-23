variable "s3_bucket_name" {
  description = "Name for the S3 bucket"
  type        = string
}

variable "kms_key_arn" {
  description = "ARN of the KMS key for encryption"
  type        = string
}

variable "region" {
  description = "AWS region"
  type        = string
}