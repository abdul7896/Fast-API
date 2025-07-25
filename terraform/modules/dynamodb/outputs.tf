# Output the DynamoDB table name after Terraform apply
output "table_name" {
  description = "Name of the DynamoDB table"
  value       = aws_dynamodb_table.users_table.name
}
