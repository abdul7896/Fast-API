output "s3_bucket" {
  value = aws_s3_bucket.avatars.bucket
}

output "dynamodb_table" {
  value = aws_dynamodb_table.users.name
}
