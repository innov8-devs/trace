# GitHub Actions Deployment Setup

## Required Secrets

Add these secrets in your GitHub repository settings:

### AWS Credentials
- `AWS_ACCESS_KEY_ID` - Your AWS access key
- `AWS_SECRET_ACCESS_KEY` - Your AWS secret key

### Database
- `DB_PASSWORD` - PostgreSQL database password

### Application
- `SECRET_KEY` - JWT secret key for your app

## Setup Steps

1. **Create AWS IAM User** with these permissions:
   - `AWSLambdaFullAccess`
   - `AmazonRDSFullAccess`
   - `AmazonAPIGatewayAdministrator`
   - `IAMFullAccess`
   - `AmazonVPCFullAccess`

2. **Add Secrets to GitHub**:
   - Go to Settings → Secrets and variables → Actions
   - Add the required secrets listed above

3. **Push to main branch** to trigger deployment

## Workflows

- **`test.yml`** - Runs on PRs and develop branch
- **`deploy.yml`** - Deploys to AWS on main branch pushes

## Manual Deployment

Trigger manual deployment:
- Go to Actions tab
- Select "Deploy to AWS Lambda"
- Click "Run workflow"