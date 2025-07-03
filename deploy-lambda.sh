#!/bin/bash

# Lambda deployment script for Farmily TRACE API

set -e

echo "🚀 Starting Lambda deployment..."

# Check if Serverless Framework is installed
if ! command -v serverless &> /dev/null; then
    echo "📦 Installing Serverless Framework..."
    npm install -g serverless
    npm install -g serverless-python-requirements
fi

# Step 1: Deploy infrastructure with Terraform
echo "🏗️  Deploying infrastructure..."

cd terraform

# Initialize Terraform if needed
if [ ! -d ".terraform" ]; then
    terraform init
fi

# Apply infrastructure
terraform plan -var-file="terraform.tfvars" -out=tfplan
echo "Please review the plan above. Continue? (y/n)"
read -r response
if [[ "$response" =~ ^[Yy]$ ]]; then
    terraform apply tfplan
else
    echo "❌ Deployment cancelled"
    exit 1
fi

# Get database URL from Terraform output
DATABASE_URL=$(terraform output -raw database_url)
cd ..

# Step 2: Deploy Lambda function
echo "🔧 Deploying Lambda function..."

# Set environment variables
export DATABASE_URL="$DATABASE_URL"
export SECRET_KEY="${SECRET_KEY:-your-secret-key-here}"

# Deploy with Serverless
serverless deploy --stage prod

echo "🎉 Lambda deployment completed!"
echo "🌐 Your API is available at the API Gateway URL shown above"
echo "📊 Monitor your Lambda function in the AWS Console"