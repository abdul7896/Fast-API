provider "aws" {
  region = "us-east-1"
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

resource "aws_s3_bucket" "avatars" {
  bucket = "prima-tech-challenge"
}