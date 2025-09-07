# AWS Infrastructure Documentation

This document describes the AWS infrastructure provisioned by Terraform for the Prima API.

## Architecture Overview

The infrastructure consists of the following components:

1. **VPC** - Virtual Private Cloud with public and private subnets
2. **EKS** - Amazon Elastic Kubernetes Service cluster
3. **S3** - Object storage for user avatars
4. **DynamoDB** - NoSQL database for user data
5. **KMS** - Key Management Service for encryption
6. **ALB** - Application Load Balancer for traffic distribution
7. **IAM** - Identity and Access Management for secure access

## Environment-Specific Configurations

### Development
- Single NAT Gateway for cost optimization
- Smaller instance types (t3.medium)
- Minimal node group size (1 node)
- Versioning suspended for S3 buckets
- Point-in-time recovery disabled for DynamoDB

### Staging
- Multiple NAT Gateways for high availability
- Medium instance types (t3.medium)
- Moderate node group size (2 nodes)
- Versioning enabled for S3 buckets
- Point-in-time recovery enabled for DynamoDB

### Production
- Multiple NAT Gateways for high availability
- Larger instance types (t3.large)
- Larger node group size (3+ nodes)
- Versioning enabled for S3 buckets
- Point-in-time recovery enabled for DynamoDB
- Deletion protection enabled for ALB

## Security Features

1. **Encryption**:
   - All data at rest encrypted with KMS keys
   - SSL/TLS encryption for data in transit
   - Secrets encryption in EKS

2. **Access Control**:
   - IAM roles with least-privilege policies
   - IRSA (IAM Roles for Service Accounts) for Kubernetes
   - Security groups for network isolation

3. **Network Security**:
   - Public and private subnet separation
   - NAT Gateways for private subnet internet access
   - Security groups with restricted ingress/egress rules

## Deployment Process

1. **Prerequisites**:
   - AWS CLI configured with appropriate permissions
   - Terraform installed
   - Existing S3 bucket for Terraform state
   - Existing DynamoDB table for state locking

2. **Deployment Steps**:
   ```bash
   # Initialize Terraform
   terraform init -backend-config="bucket=prima-api-terraform-state" -backend-config="key=dev/terraform.tfstate" -backend-config="region=us-east-1" -backend-config="dynamodb_table=prima-api-terraform-state-lock"
   
   # Plan the changes
   terraform plan -var-file="terraform-dev.tfvars"
   
   # Apply the changes
   terraform apply -var-file="terraform-dev.tfvars"
   ```

3. **Environment Variables**:
   - `AWS_ACCESS_KEY_ID` - AWS access key
   - `AWS_SECRET_ACCESS_KEY` - AWS secret key
   - `AWS_REGION` - AWS region (default: us-east-1)

## Cost Optimization

1. **Development Environment**:
   - Single NAT Gateway to reduce costs
   - Smaller instance types
   - Minimal node group size

2. **Auto Scaling**:
   - Node groups automatically scale based on demand
   - Configurable min/max sizes per environment

3. **Resource Cleanup**:
   - Automatic cleanup of old S3 object versions
   - Scheduled scaling policies (can be added)

## Monitoring and Observability

1. **CloudWatch**:
   - Automatic metrics collection for all resources
   - Alarms for critical resource thresholds

2. **X-Ray**:
   - Distributed tracing for application performance
   - Integrated with IAM policies for access

3. **Logging**:
   - VPC flow logs for network monitoring
   - EKS control plane logs
   - Application logs via Fluent Bit (to be implemented)