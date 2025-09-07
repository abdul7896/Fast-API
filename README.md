# Prima API - Production-Ready FastAPI Service

[![Security Scanning](https://github.com/your-org/Fast-API/actions/workflows/security.yaml/badge.svg)](https://github.com/your-org/Fast-API/actions/workflows/security.yaml)
[![CI/CD](https://github.com/your-org/Fast-API/actions/workflows/ci-cd.yaml/badge.svg)](https://github.com/your-org/Fast-API/actions/workflows/ci-cd.yaml)

## Overview

A production-ready FastAPI microservice with complete CI/CD pipeline, infrastructure automation, and Kubernetes deployment. This solution demonstrates enterprise-grade DevOps practices with security, observability, and automation at every stage.

## 🚀 Features

- **REST API**: FastAPI with Pydantic v2, automatic OpenAPI docs
- **Security**: API key authentication, input validation, security scanning
- **Containerization**: Multi-stage Docker builds with security best practices
- **Kubernetes**: Production-ready Helm charts with HPA, NetworkPolicy, PDB
- **Infrastructure**: Terraform for AWS resources (S3, DynamoDB, KMS, EKS)
- **CI/CD**: GitHub Actions with security scanning and automated deployments
- **Monitoring**: Prometheus metrics, health checks, structured logging
- **Documentation**: Comprehensive guides for deployment and development

## 📊 Technology Stack

| Component | Technology | Purpose |
|-----------|------------|----------|
| **API Framework** | FastAPI + Uvicorn | High-performance async Python API |
| **Containerization** | Docker | Multi-stage builds with security |
| **Orchestration** | Kubernetes + Helm | Container orchestration and packaging |
| **Infrastructure** | Terraform | AWS infrastructure as code |
| **CI/CD** | GitHub Actions | Automated testing and deployment |
| **Security** | Bandit, Trivy, Checkov | Comprehensive security scanning |
| **Monitoring** | Prometheus, AWS X-Ray | Metrics and observability |
| **Storage** | AWS S3 + DynamoDB | Object storage and NoSQL database |

## 🏗️ Project Structure

See [Project Structure Documentation](docs/project-structure.md) for detailed information about the directory layout.

### Key Directories

- `src/` - Application source code
- `infrastructure/` - Terraform configurations for AWS
- `kubernetes/` - Kubernetes manifests and Helm charts
- `.github/workflows/` - CI/CD pipeline definitions
- `scripts/` - Utility scripts for deployment and operations

## 📡 API Endpoints

- `GET /health` - Kubernetes liveness probe
- `GET /ready` - Kubernetes readiness probe
- `GET /metrics` - Prometheus metrics endpoint
- `GET /users` - Fetch all users from DynamoDB
- `POST /user` - Register a new user and upload avatar to S3

## 🐳 Containerization (Docker)

Multi-stage Docker build with security best practices:

```bash
docker build -t prima-api:latest .
docker run -p 8000:8000 --env-file .env prima-api:latest
```

## ☁️ Infrastructure as Code (Terraform)

Provision complete AWS infrastructure including:

- **EKS Cluster** with VPC, subnets, and security groups
- **S3 bucket** with server-side encryption (KMS) for avatars
- **DynamoDB table** with KMS encryption for user data
- **KMS keys** with auto-rotation enabled
- **IAM roles** for service accounts (IRSA)
- **ALB Ingress** with TLS termination

```bash
cd infrastructure/terraform
terraform init
terraform apply
```

## ⎈ Kubernetes Deployment (Helm)

Production-ready Helm charts with:

- Horizontal Pod Autoscaler (HPA)
- Network Policies
- Pod Disruption Budgets
- Resource limits and requests
- Liveness/readiness probes

```bash
# After creating kubernetes/helm/charts/prima-api/values-secret.yaml
helm install prima-api kubernetes/helm/charts/prima-api \
  --namespace prima \
  --create-namespace \
  -f kubernetes/helm/charts/prima-api/values.yaml \
  -f kubernetes/helm/charts/prima-api/values-secret.yaml
```

## 🔄 CI/CD Pipeline (GitHub Actions)

Automated workflow with multiple jobs:

1. **Security Scanning** - Bandit, Trivy, Checkov
2. **Build & Test** - Docker build, unit/integration tests
3. **Terraform** - Format, init, validate, plan, apply
4. **Helm Lint** - Validate Helm chart
5. **Deploy** - Auto-promote to dev, release, and main
6. **Slack Notifications** - Status updates for all events

## 🔐 Authentication & Security

- **API access** protected by `X-API-Key` header
- **AWS credentials** managed via IRSA (IAM Roles for Service Accounts)
- **Least-privilege IAM policies** for all services
- **KMS encryption** enabled for all data at rest
- **Secrets** injected via external Helm values
- **Security scanning** in CI pipeline

## 🧪 How to Run It Locally

1. **Clone the repo**

2. **Create `.env` file**
   ```env
   AWS_ACCESS_KEY_ID=your_access_key
   AWS_SECRET_ACCESS_KEY=your_secret_key
   AWS_REGION=us-east-1
   API_KEY=your_api_key
   S3_BUCKET=prima-avatars-bucket
   DYNAMODB_TABLE=users
   ```

3. **Run the app**
   ```bash
   docker build -t prima-api .
   docker run -p 8000:8000 --env-file .env prima-api
   ```

4. **Apply infrastructure**
   ```bash
   cd infrastructure/terraform
   terraform init
   terraform apply
   ```

5. **Deploy to Kubernetes**
   ```bash
   # After creating kubernetes/helm/charts/prima-api/values-secret.yaml
   helm install prima-api kubernetes/helm/charts/prima-api \
     -f kubernetes/helm/charts/prima-api/values.yaml \
     -f kubernetes/helm/charts/prima-api/values-secret.yaml
   kubectl port-forward service/prima-api 8000:8000
   ```

## 📈 Monitoring & Observability

- **Prometheus metrics** exposed at `/metrics` endpoint
- **AWS X-Ray** for distributed tracing
- **Health checks** at `/health` and `/ready` endpoints
- **Structured logging** for debugging and audit

## 🚀 Deployment Strategy

1. **Development** - Auto-deploy on push to `dev` branch
2. **Staging** - Manual promotion from `dev` to `release` branch
3. **Production** - Manual promotion from `release` to `main` branch
4. **Rollback** - GitOps-enabled with ArgoCD for instant rollback

## 🛡️ Security Features

- **Bandit** - Python security scanner in CI pipeline
- **Trivy** - Container vulnerability scanning
- **Checkov** - Infrastructure as Code security scanning
- **KMS encryption** - For all data at rest
- **IRSA** - IAM Roles for Service Accounts in EKS
- **Network Policies** - Pod-to-pod communication restrictions

## 📚 Documentation

- [Project Structure](docs/project-structure.md)
- [API Documentation](docs/api.md)
- [Deployment Guide](docs/deployment.md)
- [Security Guide](docs/security.md)
- [Monitoring Guide](docs/monitoring.md)

## 🤝 Future Improvements

- **JWT Authentication** - Replace API key with proper auth
- **GitOps with ArgoCD** - Enable automated sync and rollback
- **SonarQube** - Add code quality scanning
- **Ingress with TLS** - Expose API securely with Let's Encrypt
- **Chaos Engineering** - Add resilience testing
- **Service Mesh** - Implement Istio for advanced traffic management

## 🏁 Conclusion

This project demonstrates a complete, production-ready DevOps solution that automates everything from code commit to production deployment. With Terraform for infrastructure, Helm for deployment, GitHub Actions for CI/CD, and Slack for notifications, this system is secure, observable, and scalable.

Every decision was made with production standards in mind — from KMS encryption to secret management to automated testing. This isn't just a demo; it's a foundation for real-world applications.