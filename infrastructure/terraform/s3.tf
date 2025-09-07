# S3 Bucket for avatars
resource "aws_s3_bucket" "prima_avatars" {
  bucket = "${var.project_name}-avatars-${var.environment}-${random_string.bucket_suffix.result}"
}

resource "random_string" "bucket_suffix" {
  length  = 8
  special = false
  upper   = false
}

resource "aws_s3_bucket_versioning" "prima_avatars" {
  bucket = aws_s3_bucket.prima_avatars.id
  versioning_configuration {
    status = var.environment == "prod" ? "Enabled" : "Suspended"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "prima_avatars" {
  bucket = aws_s3_bucket.prima_avatars.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.app_data.arn
    }
  }
}

resource "aws_s3_bucket_public_access_block" "prima_avatars" {
  bucket = aws_s3_bucket.prima_avatars.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_lifecycle_configuration" "prima_avatars" {
  bucket = aws_s3_bucket.prima_avatars.id

  rule {
    id     = "delete_old_versions"
    status = var.environment == "prod" ? "Enabled" : "Disabled"

    noncurrent_version_expiration {
      noncurrent_days = 90
    }
  }
}