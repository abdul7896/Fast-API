variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
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