output "S3_BUCKET" {
  value = aws_s3_bucket.avatars.bucket
}

output "DYNAMODB_TABLE_name" {
  value = aws_DYNAMODB_TABLE.users.name
}
