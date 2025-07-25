# Backend module manages Terraform state storage and locking resources
module "backend" {
  source              = "./modules/backend"
  region              = var.region                      # AWS region for backend resources
  bucket_name         = var.backend_bucket_name         # S3 bucket for Terraform state
  dynamodb_table_name = var.backend_dynamodb_table_name # DynamoDB table for state locking
  kms_key_arn         = module.kms.kms_key_arn          # KMS key ARN for encryption
}

# S3 module manages additional S3 bucket resources
module "s3" {
  source         = "./modules/s3"
  s3_bucket_name = var.s3_bucket_name # Name for the avatars or other S3 bucket
  region         = var.region         # AWS region for the bucket
}

# DynamoDB module manages DynamoDB tables used by the application
module "dynamodb" {
  source      = "./modules/dynamodb"
  table_name  = var.dynamodb_table_name # DynamoDB table name for users or app data
  aws_region  = var.region              # Region for DynamoDB
  kms_key_arn = module.kms.kms_key_arn  # KMS key ARN for table encryption
}

# KMS module manages creation of the KMS key and alias used for encryption
module "kms" {
  source      = "./modules/kms"
  description = "KMS key for S3 and DynamoDB" # Description of the KMS key's purpose
  alias       = var.kms_key_alias             # Alias name for the KMS key
}
