module "s3" {
  source         = "./modules/s3"
  s3_bucket_name = var.s3_bucket_name
  kms_key_arn    = module.kms.key_arn
  region         = var.region
}

module "dynamodb" {
  source     = "./modules/dynamodb"
  table_name = var.dynamodb_table_name
  aws_region = var.region
  kms_key_arn = module.kms.key_arn
}

module "kms" {
  source      = "./modules/kms"
  description = "KMS key for S3 and DynamoDB"
  alias       =var.kms_key_alias
}


