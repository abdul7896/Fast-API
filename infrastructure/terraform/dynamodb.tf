# DynamoDB Table
resource "aws_dynamodb_table" "users" {
  name         = "${var.project_name}-users-${var.environment}"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "email"

  attribute {
    name = "email"
    type = "S"
  }

  point_in_time_recovery {
    enabled = var.environment == "production"
  }

  tags = {
    Name = "${var.project_name}-users-${var.environment}"
  }
}