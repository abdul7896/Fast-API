#!/bin/bash

# Script to deploy monitoring stack (Prometheus, Grafana, X-Ray)

echo "Deploying Prometheus..."
kubectl apply -f /home/linux/branches/Fast-API/tmp-enterprise/monitoring/prometheus/configmap.yaml
kubectl apply -f /home/linux/branches/Fast-API/tmp-enterprise/monitoring/prometheus/deployment.yaml
kubectl apply -f /home/linux/branches/Fast-API/tmp-enterprise/monitoring/prometheus/service.yaml

echo "Deploying Grafana..."
kubectl apply -f /home/linux/branches/Fast-API/tmp-enterprise/monitoring/grafana/deployment.yaml
kubectl apply -f /home/linux/branches/Fast-API/tmp-enterprise/monitoring/grafana/service.yaml
kubectl apply -f /home/linux/branches/Fast-API/tmp-enterprise/monitoring/grafana/dashboards-configmap.yaml

echo "Deploying X-Ray..."
kubectl apply -f /home/linux/branches/Fast-API/tmp-enterprise/monitoring/xray/daemonset.yaml
kubectl apply -f /home/linux/branches/Fast-API/tmp-enterprise/monitoring/xray/service.yaml

echo "Monitoring stack deployed successfully."