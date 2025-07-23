output "kms_key_id" {
  value = aws_kms_key.kms_key.key_id
}

output "kms_key_arn" {
  value = aws_kms_key.kms_key.arn
}

output "kms_alias_name" {
  value = aws_kms_alias.kms_alias.name
}







