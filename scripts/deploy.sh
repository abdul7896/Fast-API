#!/bin/bash
set -e

# Prima API Deployment Script
# Usage: ./scripts/deploy.sh [local|staging|production]

ENVIRONMENT=${1:-local}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "🚀 Deploying Prima API to environment: $ENVIRONMENT"

case $ENVIRONMENT in
  "local")
    echo "📦 Building and starting local development environment..."
    cd "$PROJECT_DIR"
    
    # Build and start with docker-compose
    docker-compose down
    docker-compose build prima-api-dev
    docker-compose up -d localstack aws-cli
    
    echo "⏳ Waiting for LocalStack setup to complete..."
    docker-compose logs -f aws-cli
    
    echo "🎯 Starting Prima API in development mode..."
    docker-compose up -d prima-api-dev
    
    echo "✅ Local deployment complete!"
    echo "🔗 API available at: http://localhost:8000"
    echo "📖 API docs at: http://localhost:8000/docs"
    echo "📊 LocalStack dashboard: http://localhost:4566"
    ;;
    
  "staging"|"production")
    echo "☸️  Deploying to Kubernetes environment: $ENVIRONMENT"
    
    # Check if kubectl is available
    if ! command -v kubectl &> /dev/null; then
      echo "❌ kubectl is required but not installed."
      exit 1
    fi
    
    # Check if helm is available
    if ! command -v helm &> /dev/null; then
      echo "❌ helm is required but not installed."
      exit 1
    fi
    
    # Set namespace
    NAMESPACE="$ENVIRONMENT"
    
    # Create namespace if it doesn't exist
    kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -
    
    # Apply RBAC
    echo "🔐 Applying RBAC configuration..."
    kubectl apply -f "$PROJECT_DIR/k8s/rbac.yaml" -n "$NAMESPACE"
    
    # Apply ConfigMap and Secrets
    echo "⚙️ Applying configuration..."
    kubectl apply -f "$PROJECT_DIR/k8s/config.yaml" -n "$NAMESPACE"
    
    # Deploy with Helm
    echo "🎯 Deploying with Helm..."
    helm upgrade --install "prima-api-$ENVIRONMENT" "$PROJECT_DIR/helm" \
      --namespace "$NAMESPACE" \
      --set environment="$ENVIRONMENT" \
      --set image.tag="${2:-latest}" \
      --wait
    
    echo "✅ Kubernetes deployment complete!"
    echo "🔍 Checking deployment status..."
    kubectl get pods -n "$NAMESPACE" -l app=prima-api
    echo "🔗 Service details:"
    kubectl get svc -n "$NAMESPACE" -l app=prima-api
    ;;
    
  *)
    echo "❌ Unknown environment: $ENVIRONMENT"
    echo "Usage: $0 [local|staging|production]"
    exit 1
    ;;
esac

echo "🎉 Deployment completed successfully!"
