#!/bin/bash

# Script to start the local development environment

echo "Starting local development environment..."

# Start LocalStack and services with docker-compose
cd /home/linux/branches/Fast-API/tmp-enterprise/local-dev/docker-compose
docker-compose up -d

echo "Local development environment started."
echo "Access the API at http://localhost:8000"
echo "User Service at http://localhost:8001"
echo "Avatar Service at http://localhost:8002"