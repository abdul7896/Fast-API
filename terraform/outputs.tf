# Output the name of the DynamoDB table from the dynamodb module
output "dynamodb_table_name" {
  description = "Name of the DynamoDB table"
  value       = module.dynamodb.table_name
}

# Output the name of the S3 bucket from the s3 module
output "s3_bucket_name" {
  value = module.s3.bucket_name # Note: reflects the bucket_name output from the s3 module
}

# Output the ARN of the KMS key from the kms module
output "kms_key_arn" {
  value = module.kms.kms_key_arn
}
