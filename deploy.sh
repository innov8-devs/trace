#!/bin/bash

# Deployment script for Farmily TRACE API to AWS

set -e

# Configuration
AWS_REGION="us-east-1"
ECR_REPO_NAME="farmily-app"
ECS_CLUSTER_NAME="farmily-cluster"
ECS_SERVICE_NAME="farmily-service"

echo "🚀 Starting deployment to AWS..."

# Step 1: Build and push Docker image to ECR
echo "📦 Building and pushing Docker image..."

# Get AWS account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO_NAME}"

# Login to ECR
aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_URI}

# Build image
docker build -f Dockerfile.prod -t ${ECR_REPO_NAME}:latest .

# Tag image
docker tag ${ECR_REPO_NAME}:latest ${ECR_URI}:latest

# Push image
docker push ${ECR_URI}:latest

echo "✅ Docker image pushed to ECR: ${ECR_URI}:latest"

# Step 2: Deploy infrastructure with Terraform (if not already deployed)
echo "🏗️  Checking infrastructure..."

cd terraform

if [ ! -f "terraform.tfstate" ]; then
    echo "🔧 Initializing and applying Terraform..."
    terraform init
    terraform plan
    echo "Please review the plan above. Continue? (y/n)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        terraform apply -auto-approve
    else
        echo "❌ Deployment cancelled"
        exit 1
    fi
else
    echo "✅ Infrastructure already exists"
fi

cd ..

echo "🎉 Deployment completed!"
echo "🌐 Your API will be available at the Load Balancer DNS name shown in Terraform outputs"
echo "📊 Monitor your application in the AWS Console:"
echo "   - ECS: https://console.aws.amazon.com/ecs/home?region=${AWS_REGION}#/clusters/${ECS_CLUSTER_NAME}"
echo "   - ECR: https://console.aws.amazon.com/ecr/repositories/${ECR_REPO_NAME}?region=${AWS_REGION}"