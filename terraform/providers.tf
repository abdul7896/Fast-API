# Specify required provider versions for Terraform
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws" # Use the official AWS provider from HashiCorp
      version = "~> 4.0"        # Require AWS provider version 4.x
    }
  }
}

# Configure the AWS provider with the region from variables
provider "aws" {
  region = var.region # AWS region for resource deployment
}
