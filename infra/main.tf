provider "aws" {
  region = "us-east-1"
}

resource "random_id" "bucket_id" {
  byte_length = 4
}

resource "aws_s3_bucket" "avatars" {
  bucket = "prima-tech-challenge-${random_id.bucket_id.hex}"
}

resource "aws_dynamodb_table" "users" {
  name         = "users"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "email"

  attribute {
    name = "email"
    type = "S"
  }
}

output "s3_bucket_name" {
  value = aws_s3_bucket.avatars.bucket
}

output "dynamodb_table_name" {
  value = aws_dynamodb_table.users.name
}
