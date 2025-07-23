output "dynamodb_table_name" {
  description = "Name of the DynamoDB table"
  value       = module.dynamodb.table_name
}

output "s3_bucket_name" {
  value = module.s3.bucket_name # Changed from s3_bucket_name to bucket_name
}

output "kms_key_arn" {
  value = module.kms.kms_key_arn
}