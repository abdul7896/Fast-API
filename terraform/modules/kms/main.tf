resource "aws_kms_key" "kms_key" {
  description             = var.description
  enable_key_rotation     = true
  deletion_window_in_days = 30
}

resource "aws_kms_alias" "kms_alias" {
  name          = "alias/${var.alias}"
  target_key_id = aws_kms_key.kms_key.key_id
}

