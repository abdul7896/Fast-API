#!/bin/bash

# Script to apply security configurations

echo "Applying Network Policies..."
kubectl apply -f /home/linux/branches/Fast-API/tmp-enterprise/kubernetes/networking/user-service-network-policy.yaml
kubectl apply -f /home/linux/branches/Fast-API/tmp-enterprise/kubernetes/networking/avatar-service-network-policy.yaml
kubectl apply -f /home/linux/branches/Fast-API/tmp-enterprise/kubernetes/networking/api-gateway-network-policy.yaml

echo "Applying Pod Security Policies..."
kubectl apply -f /home/linux/branches/Fast-API/tmp-enterprise/kubernetes/security/psp.yaml

echo "Security configurations applied successfully."