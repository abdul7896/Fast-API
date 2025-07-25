# Name to assign to the S3 bucket
variable "s3_bucket_name" {
  description = "Name for the S3 bucket"
  type        = string
}

# AWS region where resources will be created
variable "region" {
  description = "AWS region"
  type        = string
}
