output "s3_bucket_name" {
  description = "Name of the S3 bucket"
  value       = aws_s3_bucket.avatars_bucket.id
}