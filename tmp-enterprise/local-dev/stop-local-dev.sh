#!/bin/bash

# Script to stop the local development environment

echo "Stopping local development environment..."

# Stop LocalStack and services with docker-compose
cd /home/linux/branches/Fast-API/tmp-enterprise/local-dev/docker-compose
docker-compose down

echo "Local development environment stopped."