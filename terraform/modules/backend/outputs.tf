# Output the name of the S3 bucket used for storing Terraform state
output "s3_bucket_name" {
  description = "Name of the S3 bucket for Terraform state"
  value       = aws_s3_bucket.tf_state.bucket
}

# Output the name of the DynamoDB table used for state locking
output "dynamodb_table_name" {
  description = "Name of the DynamoDB table used for state locking"
  value       = aws_dynamodb_table.tf_lock.name
}
