# DynamoDB Table
resource "aws_dynamodb_table" "users" {
  name         = "${var.project_name}-users-${var.environment}"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "email"

  attribute {
    name = "email"
    type = "S"
  }

  server_side_encryption {
    enabled     = true
    kms_key_arn = aws_kms_key.app_data.arn
  }

  point_in_time_recovery {
    enabled = var.environment == "prod" || var.environment == "staging"
  }

  tags = {
    Name        = "${var.project_name}-users-${var.environment}"
    Environment = var.environment
  }
}