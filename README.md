 Prima SRE Tech Challenge

**End-to-End Infrastructure and Deployment Solution**



 Overview

This project delivers a complete solution for deploying a FastAPI service using a modern DevOps toolchain. The goal is to demonstrate infrastructure automation, secure cloud integration, scalable deployment, and continuous delivery—all aligned with production standards.



 Technology Stack

* FastAPI – RESTful API server in Python
* Docker – Containerization of the application
* Terraform – Infrastructure as Code for AWS resources
* Kubernetes – Container orchestration
* Helm – Kubernetes package management
* GitHub Actions – CI/CD automation



 Architecture Summary

The system is composed of modular components, designed to be loosely coupled, reproducible, and scalable.

```
[ FastAPI App ] --> [ Docker Image ] --> [ Kubernetes Cluster ]
        |                    |                        |
        v                    v                        v
 [ AWS S3 / DynamoDB ] <-- [ Terraform IaC ] <-- [ GitHub Actions CI/CD ]
```

Each stage is independently testable and deployable.



 API Service (FastAPI)

 Endpoints

* `GET /users`: Fetch all registered users from DynamoDB
* `POST /user`: Register a new user and upload an avatar to S3

 Features

* Input validation using Pydantic models
* Presigned URL generation for secure S3 uploads
* AWS SDK integration for DynamoDB and S3
* API key authentication via `X-API-Key` header
* Graceful error handling for all AWS interactions



 Containerization (Docker)

The app is containerized using a multistage Dockerfile to ensure clean, minimal images.

* Base: `python:3.11-slim`
* Uses `pip install --no-cache-dir` for efficient dependency layering
* `.env` file is excluded from the image to prevent secret leakage

 Common Commands

```bash
docker build -t abz7896/prima-api:latest .
docker run -p 8000:8000 --env-file .env abz7896/prima-api:latest
```



 Infrastructure as Code (Terraform)

Terraform scripts are used to provision and manage all required AWS infrastructure:

* S3 bucket with server-side encryption for storing user avatars
* DynamoDB table for storing user records
* IAM policies and roles granting scoped access
* KMS-managed encryption
* Remote backend with S3 state storage and DynamoDB locking

Infrastructure is modular, idempotent, and auditable.



 Kubernetes Deployment (Helm)

Helm is used to package the Kubernetes deployment configuration.

 Helm Chart Includes:

* Deployment with liveness/readiness probes and resource limits
* Service configuration (ClusterIP)
* ConfigMaps for environment variables
* Horizontal Pod Autoscaler (HPA)
* Secrets for API keys or AWS credentials 



 CI/CD (GitHub Actions)

A GitHub Actions workflow automates build, linting, and deployment.

 Key Jobs

* Python linting with `flake8`
* Docker image build and push to Docker Hub
* Helm upgrade for Kubernetes deployment
* Future extension: Include SonarQube scans, security checks, and Prometheus alerts

CI/CD is triggered on pushes to the `feature/python-api-server-final` branch.



 Authentication & Security

* All AWS credentials are handled via environment variables
* API access is protected by a hardcoded API key for now
* S3 buckets and DynamoDB tables use least-privilege IAM policies
* KMS encryption is enabled by default



 Future Improvements

* Prometheus configuration to scrape FastAPI metrics
* Future work includes Grafana dashboards
* Add user authentication (JWT)
* Integrate GitLab CI/CD and SonarQube
* Expand Helm chart to support Ingress with TLS
* Enable AWS IRSA for production-grade security
* Add automated security scanning to the CI pipeline


