# Configure the AWS provider using the region defined in variables
provider "aws" {
  region = var.region
}

# S3 bucket used to store Terraform remote state securely
resource "aws_s3_bucket" "tf_state" {
  bucket = var.bucket_name  # Bucket name passed via variables

  # Enable versioning to keep a history of all changes to the state file
  versioning {
    enabled = true
  }

  # Enable server-side encryption using a customer-managed AWS KMS key
  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm     = "aws:kms"              # Use AWS KMS for encryption
        kms_master_key_id = var.kms_key_arn        # KMS key ARN provided via variables
      }
    }
  }

  # Lifecycle rules for automatically cleaning up old/incomplete files
  lifecycle_rule {
    enabled = true

    # Automatically delete incomplete multipart uploads after 7 days
    abort_incomplete_multipart_upload_days = 7

    # Expire objects after 365 days
    expiration {
      days = 365
    }
  }
}

# DynamoDB table used for Terraform state locking
resource "aws_dynamodb_table" "tf_lock" {
  name         = var.dynamodb_table_name   # Table name passed via variables
  billing_mode = "PAY_PER_REQUEST"         # No need to manage read/write capacity
  hash_key     = "LockID"                  # Primary key to identify the lock

  # Define the primary key attribute
  attribute {
    name = "LockID"
    type = "S"  # String type
  }
}
