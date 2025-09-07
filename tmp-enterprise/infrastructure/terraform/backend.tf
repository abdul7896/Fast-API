# Terraform backend configuration
terraform {
  backend "s3" {
    bucket         = "prima-api-terraform-state"
    key            = "terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "prima-api-terraform-state-lock"
    encrypt        = true
  }
}