variable "dynamodb_table_name" {
  type    = string
  default = "users"
}

variable "s3_bucket" {
  type    = string
  default = "prima-tech-user-avatars"
}

variable "aws_region" {
  type    = string
  default = "us-east-1"
}