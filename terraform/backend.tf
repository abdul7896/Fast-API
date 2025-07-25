terraform {
  backend "s3" {
    bucket         = "my-prima-tf-state9278"      # S3 bucket to store Terraform state files
    key            = "env/prod/terraform.tfstate" # Path within the bucket for the state file
    region         = "us-east-1"                  # AWS region of the S3 bucket and DynamoDB table
    dynamodb_table = "terraform-lock-table"       # DynamoDB table for state locking to prevent concurrent changes
    encrypt        = true                         # Enable encryption for the state file in S3
  }
}

# Local backend configuration 
# terraform {
#   backend "local" {
#     path = "bootstrap.tfstate"              # Local path to store Terraform state file
#   }
# }
