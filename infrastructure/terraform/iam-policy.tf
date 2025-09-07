# KMS Key for application data encryption
resource "aws_kms_key" "app_data" {
  description             = "KMS key for application data encryption"
  deletion_window_in_days = 7
  enable_key_rotation     = true

  tags = {
    Name        = "${var.project_name}-app-data-key-${var.environment}"
    Environment = var.environment
  }
}

resource "aws_kms_alias" "app_data" {
  name          = "alias/${var.project_name}-app-data-key-${var.environment}"
  target_key_id = aws_kms_key.app_data.key_id
}

# IAM Policy for Prima API
resource "aws_iam_policy" "prima_api_policy" {
  name        = "${var.project_name}-policy-${var.environment}"
  description = "IAM policy for Prima API service"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.prima_avatars.arn,
          "${aws_s3_bucket.prima_avatars.arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:DeleteItem",
          "dynamodb:Scan",
          "dynamodb:Query",
          "dynamodb:DescribeTable"
        ]
        Resource = [
          aws_dynamodb_table.users.arn,
          "${aws_dynamodb_table.users.arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "kms:Encrypt",
          "kms:Decrypt",
          "kms:ReEncrypt*",
          "kms:GenerateDataKey*",
          "kms:DescribeKey"
        ]
        Resource = [
          aws_kms_key.app_data.arn
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "xray:PutTraceSegments",
          "xray:PutTelemetryRecords",
          "xray:GetSamplingRules",
          "xray:GetSamplingTargets"
        ]
        Resource = "*"
      }
    ]
  })

  tags = {
    Name        = "${var.project_name}-policy-${var.environment}"
    Environment = var.environment
  }
}

resource "aws_iam_role_policy_attachment" "prima_api_policy_attachment" {
  role       = aws_iam_role.prima_api_service_role.name
  policy_arn = aws_iam_policy.prima_api_policy.arn
}