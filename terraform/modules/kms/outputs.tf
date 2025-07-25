# Output the unique identifier of the created KMS key
output "kms_key_id" {
  value = aws_kms_key.kms_key.key_id
}

# Output the Amazon Resource Name (ARN) of the created KMS key
output "kms_key_arn" {
  value = aws_kms_key.kms_key.arn
}

# Output the alias name assigned to the KMS key
output "kms_alias_name" {
  value = aws_kms_alias.kms_alias.name
}
