#!/bin/bash

# Script to deploy Helm charts to Kubernetes

echo "Creating Kubernetes namespace..."
kubectl create namespace prima-api --dry-run=client -o yaml | kubectl apply -f -

echo "Deploying User Service..."
helm upgrade --install user-service \
  /home/linux/branches/Fast-API/tmp-enterprise/platform/helm-charts/user-service \
  --namespace prima-api \
  --values /home/linux/branches/Fast-API/tmp-enterprise/platform/helm-charts/user-service/values.yaml

echo "Deploying Avatar Service..."
helm upgrade --install avatar-service \
  /home/linux/branches/Fast-API/tmp-enterprise/platform/helm-charts/avatar-service \
  --namespace prima-api \
  --values /home/linux/branches/Fast-API/tmp-enterprise/platform/helm-charts/avatar-service/values.yaml

echo "Deploying API Gateway..."
helm upgrade --install api-gateway \
  /home/linux/branches/Fast-API/tmp-enterprise/platform/helm-charts/api-gateway \
  --namespace prima-api \
  --values /home/linux/branches/Fast-API/tmp-enterprise/platform/helm-charts/api-gateway/values.yaml

echo "Helm charts deployed successfully."