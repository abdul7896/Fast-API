# terraform/modules/s3/main.tf
resource "aws_s3_bucket" "avatars_bucket" {
  bucket = var.s3_bucket_name
  force_destroy     = true
  
}

resource "aws_s3_bucket_ownership_controls" "avatars_bucket_ownership" {
  bucket = aws_s3_bucket.avatars_bucket.id

  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}


resource "aws_s3_bucket_public_access_block" "avatars_public_access" {
  bucket = aws_s3_bucket.avatars_bucket.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

# resource "aws_s3_bucket_policy" "avatars_policy" {
#   bucket = aws_s3_bucket.avatars_bucket.id
#   policy = jsonencode({
#     Version = "2012-10-17"
#     Statement = [
#       {
#         Sid       = "PublicReadGetObject"
#         Effect    = "Allow"
#         Principal = "*"
#         Action    = "s3:GetObject"
#         Resource  = "arn:aws:s3:::${aws_s3_bucket.avatars_bucket.id}/avatars/*"
#       }
#     ]
#   })
# }

# IAM Policy for S3 (used by app)
# resource "aws_iam_policy" "s3_access" {
#   name        = "PrimaS3Access"
#   description = "Allow PutObject, GetObject, and ListBucket for prima-avatars-bucket"
#   policy = jsonencode({
#     Version = "2012-10-17"
#     Statement = [
#       {
#         Effect = "Allow"
#         Action = [
#           "s3:PutObject",
#           "s3:GetObject",
#           "s3:ListBucket"
#         ]
#         Resource = [
#           "arn:aws:s3:::${var.s3_bucket_name}",
#           "arn:aws:s3:::${var.s3_bucket_name}/*"
#         ]
#       }
#     ]
#   })
# }