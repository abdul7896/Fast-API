#!/bin/bash

# Wait for LocalStack to be ready
echo "Waiting for LocalStack to be ready..."
until curl -s http://localstack:4566/_localstack/health | grep -q '"services":'; do
  sleep 2
done

echo "LocalStack is ready. Creating AWS resources..."

# Create S3 bucket for avatars
awslocal s3 mb s3://prima-avatars

# Create DynamoDB table for users
awslocal dynamodb create-table \
    --table-name users \
    --attribute-definitions \
        AttributeName=email,AttributeType=S \
    --key-schema \
        AttributeName=email,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST

echo "AWS resources created successfully."