#!/bin/bash

# Script to provision AWS infrastructure with Terraform

echo "Initializing Terraform..."
cd /home/linux/branches/Fast-API/tmp-enterprise/infrastructure/terraform
terraform init

echo "Planning infrastructure changes..."
terraform plan -out=tfplan

echo "Applying infrastructure changes..."
terraform apply tfplan

echo "Infrastructure provisioning complete."