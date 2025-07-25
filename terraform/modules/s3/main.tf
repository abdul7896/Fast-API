# Create an S3 bucket for storing avatars with forced destroy enabled
resource "aws_s3_bucket" "avatars_bucket" {
  bucket        = var.s3_bucket_name      # Bucket name from variables
  force_destroy = true                    # Allow bucket and all objects to be deleted on destroy
}

# Enable server-side encryption using AES256 for the avatars bucket
resource "aws_s3_bucket_server_side_encryption_configuration" "avatars_bucket_sse" {
  bucket = aws_s3_bucket.avatars_bucket.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"           # Use AES256 encryption (SSE-S3)
    }
  }
}

# Configure ownership controls to prefer bucket owner over object owner
resource "aws_s3_bucket_ownership_controls" "avatars_bucket_ownership" {
  bucket = aws_s3_bucket.avatars_bucket.id

  rule {
    object_ownership = "BucketOwnerPreferred"  # Bucket owner takes ownership of all objects
  }
}

# Manage public access block settings for the bucket (allowing public read access)
resource "aws_s3_bucket_public_access_block" "avatars_public_access" {
  bucket = aws_s3_bucket.avatars_bucket.id

  block_public_acls       = false   # Do not block public ACLs
  block_public_policy     = false   # Do not block public bucket policies
  ignore_public_acls      = false   # Consider public ACLs
  restrict_public_buckets = false   # Do not restrict public buckets
}

# Enable versioning on the avatars bucket to preserve object history
resource "aws_s3_bucket_versioning" "avatars_bucket_versioning" {
  bucket = aws_s3_bucket.avatars_bucket.id

  versioning_configuration {
    status = "Enabled"              # Enable versioning
  }
}

# Define bucket policy to allow public read access on all objects in the bucket
resource "aws_s3_bucket_policy" "avatars_bucket_policy" {
  bucket = aws_s3_bucket.avatars_bucket.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Sid       = "AllowPublicRead",
        Effect    = "Allow",
        Principal = "*",             # Allow anyone (public)
        Action    = "s3:GetObject", # Allow read/get object
        Resource  = "${aws_s3_bucket.avatars_bucket.arn}/*"  # Applies to all objects in bucket
      }
    ]
  })
}
