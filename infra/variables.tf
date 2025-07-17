variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "DYNAMODB_TABLE_name" {
  type    = string
  default = "users"
}

variable "S3_BUCKET" {
  type    = string
  default = "prima-tech-user-avatars"
}
