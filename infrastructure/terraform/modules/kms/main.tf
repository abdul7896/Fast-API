# Create a customer-managed KMS key with rotation and deletion window
resource "aws_kms_key" "kms_key" {
  description             = var.description         # Description of the key's purpose
  enable_key_rotation     = true                    # Enable automatic annual key rotation
  deletion_window_in_days = 30                      # Waiting period before key deletion (30 days)
}

# Create an alias for the KMS key to simplify referencing it
resource "aws_kms_alias" "kms_alias" {
  name          = "alias/${var.alias}"             # Alias name prefixed with "alias/"
  target_key_id = aws_kms_key.kms_key.key_id      # Link alias to the created KMS key
}
