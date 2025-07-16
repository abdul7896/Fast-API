variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "dynamodb_table_name" {
  type    = string
  default = "users"
}

variable "s3_bucket_name" {
  type    = string
  default = "prima-tech-user-avatars"
}
