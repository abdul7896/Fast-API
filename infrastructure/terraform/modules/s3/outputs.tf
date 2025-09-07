# Output the name of the avatars S3 bucket
output "bucket_name" {
  value = aws_s3_bucket.avatars_bucket.bucket
}

# Output the ARN (Amazon Resource Name) of the avatars S3 bucket
output "bucket_arn" {
  value = aws_s3_bucket.avatars_bucket.arn
}

# Output the internal ID of the avatars S3 bucket resource
output "bucket_id" {
  value = aws_s3_bucket.avatars_bucket.id
}
