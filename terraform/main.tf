resource "aws_s3_bucket" "avatars" {
  bucket = "prima-avatars-${var.environment}"  # e.g., prima-avatars-dev

  tags = {
    Environment = var.environment
  }
}

resource "aws_dynamodb_table" "users" {
  name         = "users-${var.environment}"  # e.g., users-dev
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "email"  # Partition key

  attribute {
    name = "email"
    type = "S"  # String
  }

  tags = {
    Environment = var.environment
  }
}