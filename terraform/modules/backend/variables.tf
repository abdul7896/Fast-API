variable "bucket_name" {
  description = "Name of the S3 bucket for terraform state"
  type        = string
}

variable "lock_table_name" {
  description = "Name of the DynamoDB table for terraform state locking"
  type        = string
}
