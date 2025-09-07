# EKS Cluster
module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 19.0"

  cluster_name    = "${var.cluster_name}-${var.environment}"
  cluster_version = var.kubernetes_version

  vpc_id                          = module.vpc.vpc_id
  subnet_ids                      = module.vpc.private_subnets
  cluster_endpoint_public_access  = true
  cluster_endpoint_private_access = true

  # Encryption
  cluster_encryption_config = [{
    provider_key_arn = aws_kms_key.eks.arn
    resources        = ["secrets"]
  }]

  cluster_addons = {
    coredns = {
      most_recent = true
    }
    kube-proxy = {
      most_recent = true
    }
    vpc-cni = {
      most_recent = true
    }
    aws-ebs-csi-driver = {
      most_recent = true
    }
    aws-efs-csi-driver = {
      most_recent = true
    }
  }

  eks_managed_node_groups = {
    general = {
      desired_size = var.environment == "prod" ? 3 : var.environment == "staging" ? 2 : 1
      min_size     = var.environment == "prod" ? 2 : 1
      max_size     = var.environment == "prod" ? 10 : var.environment == "staging" ? 5 : 3

      instance_types = var.environment == "prod" ? ["t3.large"] : ["t3.medium"]
      capacity_type  = "ON_DEMAND"

      labels = {
        Environment = var.environment
        NodeGroup   = "general"
      }

      tags = {
        Name = "${var.project_name}-node-${var.environment}"
      }

      update_config = {
        max_unavailable_percentage = 33
      }
    }
  }

  # aws-auth configmap
  manage_aws_auth_configmap = true

  aws_auth_roles = [
    {
      rolearn  = aws_iam_role.prima_api_service_role.arn
      username = "prima-api-service"
      groups   = ["system:masters"]
    },
  ]

  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

# KMS Key for EKS secrets encryption
resource "aws_kms_key" "eks" {
  description             = "KMS key for EKS secrets encryption"
  deletion_window_in_days = 7
  enable_key_rotation     = true

  tags = {
    Name        = "${var.project_name}-eks-key-${var.environment}"
    Environment = var.environment
  }
}

resource "aws_kms_alias" "eks" {
  name          = "alias/${var.project_name}-eks-key-${var.environment}"
  target_key_id = aws_kms_key.eks.key_id
}