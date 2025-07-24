# **Prima SRE Tech Challenge**  
## **End-to-End Infrastructure and Deployment Solution**

### **Overview**

I designed and implemented a complete CI/CD pipeline and infrastructure automation system for a FastAPI service. This solution covers code to cloud — from development to production — with security, observability, and automation at every stage.

### **Technology Stack**

- **FastAPI** – Python-based REST API  
- **Docker** – Containerization  
- **Terraform** – Infrastructure as Code (AWS)  
- **Kubernetes + Helm** – Deployment orchestration  
- **GitHub Actions** – CI/CD automation  
- **Slack** – Real-time notifications  

### **Architecture Summary**

```
[ FastAPI App ] → [ Docker ] → [ Kubernetes (Helm) ]
       ↓               ↓               ↓
   [ AWS S3 / DynamoDB ] ← [ Terraform ] ← [ GitHub Actions + Slack ]
```

Fully automated, modular, and production-ready.

---

### **API Service (FastAPI)**

#### **Endpoints**
- `GET /users` – Fetch all users from DynamoDB  
- `POST /user` – Register a new user and generate S3 presigned URL for avatar upload  

#### **Features**
- Input validation with Pydantic  
- Secure S3 presigned URLs for uploads  
- AWS SDK integration (boto3)  
- API key authentication via `X-API-Key`  
- Graceful error handling for AWS failures  

---

### **Containerization (Docker)**

I containerized the app using a minimal, secure Docker setup.

- Base: `python:3.11-slim`  
- Dependencies installed with `--no-cache-dir`  
- `.env` excluded from image (security best practice)  

#### **Commands**
```bash
docker build -t abz7896/prima-api:latest .
docker run -p 8000:8000 --env-file .env abz7896/prima-api:latest
```

---

### **Infrastructure as Code (Terraform)**

I used Terraform to provision all AWS resources:

- **S3 bucket** with server-side encryption (KMS) for avatars  
- **DynamoDB table** with KMS encryption for user data  
- **KMS key** with auto-rotation enabled  
- **Remote state backend** in S3 with DynamoDB locking for team safety  

All infrastructure is version-controlled, modular, and reproducible.

> **Note on IAM Roles**:  
> I did **not use IAM roles** like IRSA because this runs on a generic Kubernetes cluster, not EKS. Without EKS, IRSA isn't available. Instead, I securely pass AWS credentials via Helm.

> **KMS & DynamoDB Encryption**:  
> Yes, I **did use KMS correctly** — the DynamoDB table uses **server-side encryption with a customer-managed KMS key**, and I granted the application `kms:Encrypt` and `kms:Decrypt` permissions via IAM policy. This ensures full control and auditability of encryption.

---

### **Kubernetes Deployment (Helm)**

I packaged the deployment using Helm for consistency and reusability.

#### **Chart Includes**
- Deployment with liveness/readiness probes  
- Resource limits and requests  
- Horizontal Pod Autoscaler (HPA)  
- ConfigMap for non-sensitive config  
- Secrets (external) for API key and AWS credentials  

> **Security Note**:  
> I **did not commit** `values-secret.yaml`. It contains:
> ```yaml
> env:
>   API_KEY: primaGUeeghoMV3wooeJnnmTmSoo6mfMZmjVBPqC3z7T7ydJrmP2Rpelsr4lMXJIZ1dtSWHcqoXli0xjONlrDDZx6CEh0NnP55tZ7SxwoaXAoOPNz8LqnCgzpE4tx5L1uStiwNU7wEeDuhoW2ohXEveg2qjHkPTgMkKvFbbebRWLNGzY1EGaRL2Y1wRnljcZXqbwYeKIib0lJTU7VsIQYnUMms4HgQMx3A8TlSZrDt4CNoEJ0cucoLBZX0s36JHl8dpe0NskukIdq4lUQCgrIHZ77aac4IBccgBOWyVWN61yLJK7TqnmEewHmfon5UEcqiqNHchAm997rkeXWk843r0raMEkU1VmNuXlbwgOVtiwjr1v5WEjuwpOBq9uPQowREmeqRk0NTrTFQFPDuXOY5P3iZfZdcW2h9jH6iW9H7SfZE0A52JBmyY97CybG0vtKEWKetZqTEbFQfWL559rfYIVfrKAIjZXT1yGg8LfeFX3XBhkDIydRoJkXYnQInGx"

>   AWS_ACCESS_KEY_ID: "..."
>   AWS_SECRET_ACCESS_KEY: "..."
> ```
> 
> Deploy using:
> ```bash
> helm install prima-api ./helm \
>   --namespace prima \
>   --create-namespace \
>   -f helm/values.yaml \
>   -f values-secret.yaml
> ```
> 
> This keeps secrets out of version control.

---

### **CI/CD Pipeline (GitHub Actions)**

I automated the entire workflow using GitHub Actions:

#### **Jobs in Order**
1. **Build** – Lint Python, run Bandit security scan, build & push Docker image  
2. **Terraform** – Format, init, validate, plan, and apply infrastructure  
3. **Tests** – Run unit and integration tests  
4. **Helm Lint** – Validate Helm chart  
5. **Deploy to Dev** – Merge to `dev` branch  
6. **Deploy to Release** – Merge to `release`  
7. **Deploy to Main** – Merge to `main`  
8. **Slack Notification** – Send status to Slack on **all events**

#### **Slack Integration**
- I set up **Slack notifications for every pipeline outcome** (success/failure)  
- Notifications include: workflow name, status, branch, and trigger  
- Uses `slackapi/slack-github-action`  
- Sends updates for **all branches**, not just main  
- Ensures visibility across the team  

---

### **Authentication & Security**

- **API access** protected by `X-API-Key` header  
- **AWS credentials** passed via environment (never hardcoded)  
- **Least-privilege IAM policies** for S3, DynamoDB, and KMS  
- **KMS encryption** enabled for all data at rest  
- **Secrets** injected via external Helm values  
- **Bandit scan** in CI to catch security issues early  

---

### **How to Run It Locally**

1. **Clone the repo**
   ```bash
   git clone https://github.com/abdul7896/prima-tech-challenge.git
   cd prima-tech-challenge
   ```

2. **Create `.env` file**
   ```env
   AWS_ACCESS_KEY_ID=your_access_key
   AWS_SECRET_ACCESS_KEY=your_secret_key
   AWS_REGION=us-east-1
   API_KEY=primaGUeeghoMV3wooeJnnmTmSoo6mfMZmjVBPqC3z7T7ydJrmP2Rpelsr4lMXJIZ1dtSWHcqoXli0xjONlrDDZx6CEh0NnP55tZ7SxwoaXAoOPNz8LqnCgzpE4tx5L1uStiwNU7wEeDuhoW2ohXEveg2qjHkPTgMkKvFbbebRWLNGzY1EGaRL2Y1wRnljcZXqbwYeKIib0lJTU7VsIQYnUMms4HgQMx3A8TlSZrDt4CNoEJ0cucoLBZX0s36JHl8dpe0NskukIdq4lUQCgrIHZ77aac4IBccgBOWyVWN61yLJK7TqnmEewHmfon5UEcqiqNHchAm997rkeXWk843r0raMEkU1VmNuXlbwgOVtiwjr1v5WEjuwpOBq9uPQowREmeqRk0NTrTFQFPDuXOY5P3iZfZdcW2h9jH6iW9H7SfZE0A52JBmyY97CybG0vtKEWKetZqTEbFQfWL559rfYIVfrKAIjZXT1yGg8LfeFX3XBhkDIydRoJkXYnQInGx

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
   cd terraform
   terraform init
   terraform apply
   ```

5. **Deploy to Kubernetes**
   ```bash
   # After creating values-secret.yaml
   2. **Create `.env`**
   ```env
   AWS_ACCESS_KEY_ID=your_key
   AWS_SECRET_ACCESS_KEY=your_secret
   AWS_REGION=us-east-1
   API_KEY=primaGUeeghoMV3wooeJnnmTmSoo6mfMZmjVBPqC3z7T7ydJrmP2Rpelsr4lMXJIZ1dtSWHcqoXli0xjONlrDDZx6CEh0NnP55tZ7SxwoaXAoOPNz8LqnCgzpE4tx5L1uStiwNU7wEeDuhoW2ohXEveg2qjHkPTgMkKvFbbebRWLNGzY1EGaRL2Y1wRnljcZXqbwYeKIib0lJTU7VsIQYnUMms4HgQMx3A8TlSZrDt4CNoEJ0cucoLBZX0s36JHl8dpe0NskukIdq4lUQCgrIHZ77aac4IBccgBOWyVWN61yLJK7TqnmEewHmfon5UEcqiqNHchAm997rkeXWk843r0raMEkU1VmNuXlbwgOVtiwjr1v5WEjuwpOBq9uPQowREmeqRk0NTrTFQFPDuXOY5P3iZfZdcW2h9jH6iW9H7SfZE0A52JBmyY97CybG0vtKEWKetZqTEbFQfWL559rfYIVfrKAIjZXT1yGg8LfeFX3XBhkDIydRoJkXYnQInGx
   S3_BUCKET=prima-avatars-bucket
   DYNAMODB_TABLE=users
   ```
   helm install prima-api helm/ -f helm/values.yaml -f values-secret.yaml
   kubectl port-forward service/prima-api-prima-api 8000:8000
   ```

---

### **Future Improvements**

- **Prometheus + Grafana** – Monitor API metrics and K8s performance  
- **JWT Authentication** – Replace API key with proper auth  
- **GitOps with ArgoCD** – Enable automated sync and rollback  
- **SonarQube + Trivy** – Add code quality and vulnerability scanning  
- **Ingress with TLS** – Expose API securely  
- **Enable IRSA** – When moving to EKS, use IAM roles for service accounts  

---

### **Conclusion**

I delivered a full-stack DevOps solution that automates everything from code commit to production deployment. With Terraform for infrastructure, Helm for deployment, GitHub Actions for CI/CD, and Slack for notifications, this system is secure, observable, and scalable.

Every decision was made with production standards in mind — from KMS encryption to secret management to automated testing. This isn’t just a demo; it’s a foundation for real-world applications.

---

 **Final Note**: This project demonstrates end-to-end ownership — from writing code to managing infrastructure to enabling team collaboration through automation and alerts.

---
