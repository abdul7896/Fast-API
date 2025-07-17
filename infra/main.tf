resource "aws_DYNAMODB_TABLE" "users" {
  name           = var.DYNAMODB_TABLE_name
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "email"

  attribute {
    name = "email"
    type = "S"
  }

  tags = {
    Environment = "dev"
    Project     = "prima-tech-challenge"
  }
}

resource "aws_s3_bucket" "avatars" {
  bucket = var.S3_BUCKET

  tags = {
    Environment = "dev"
    Project     = "prima-tech-challenge"
  }
}

resource "aws_s3_bucket_public_access_block" "avatars_block" {
  bucket = aws_s3_bucket.avatars.id

  block_public_acls   = true
  block_public_policy = true
  ignore_public_acls  = true
  restrict_public_buckets = true
}
