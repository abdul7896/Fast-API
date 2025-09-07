#!/bin/bash
set -e

echo "🚀 Setting up LocalStack AWS services..."

# Wait for LocalStack to be ready
echo "⏳ Waiting for LocalStack to be ready..."
while ! curl -s http://localstack:4566/health | grep -q "running"; do
  echo "   Still waiting for LocalStack..."
  sleep 2
done

echo "✅ LocalStack is ready!"

# Create S3 bucket
echo "📦 Creating S3 bucket: prima-avatars-local"
aws --endpoint-url=http://localstack:4566 s3api create-bucket \
  --bucket prima-avatars-local \
  --region us-east-1

# Enable S3 bucket versioning
aws --endpoint-url=http://localstack:4566 s3api put-bucket-versioning \
  --bucket prima-avatars-local \
  --versioning-configuration Status=Enabled

# Create DynamoDB table
echo "🗃️  Creating DynamoDB table: users-local"
aws --endpoint-url=http://localstack:4566 dynamodb create-table \
  --table-name users-local \
  --attribute-definitions \
    AttributeName=email,AttributeType=S \
  --key-schema \
    AttributeName=email,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1

# Wait for table to be active
echo "⏳ Waiting for DynamoDB table to be active..."
aws --endpoint-url=http://localstack:4566 dynamodb wait table-exists \
  --table-name users-local \
  --region us-east-1

# Create test data (optional)
echo "📝 Creating test user..."
aws --endpoint-url=http://localstack:4566 dynamodb put-item \
  --table-name users-local \
  --item '{
    "email": {"S": "test@example.com"},
    "name": {"S": "Test User"},
    "avatar_url": {"S": "https://prima-avatars-local.s3.amazonaws.com/avatars/test@example.com/test.jpg"}
  }' \
  --region us-east-1

echo "✅ LocalStack setup completed successfully!"
echo "🔗 S3 bucket: prima-avatars-local"
echo "🔗 DynamoDB table: users-local"
echo "🔗 LocalStack endpoint: http://localhost:4566"

# Keep container running briefly to show completion
sleep 2
