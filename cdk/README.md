# CDK Infrastructure

AWS CDK infrastructure for Popcorn Sales Manager.

## Quick Start

1. **Configure your environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

2. **Deploy**:
   ```bash
   ./deploy.sh
   ```

## Configuration

All configuration is managed through the `.env` file (gitignored):

- `ENVIRONMENT` - Deployment environment (dev, staging, prod)
- `BASE_DOMAIN` - Your Route53 hosted zone domain
- `AWS_ACCOUNT_ID` - AWS account ID
- `AWS_REGION` - AWS region (default: us-east-1)

### Resource Import

To import existing resources, add them to `.env`:

- `STATIC_BUCKET_NAME` - S3 bucket for static assets
- `EXPORTS_BUCKET_NAME` - S3 bucket for exports
- `TABLE_NAME` - DynamoDB table name
- `USER_POOL_ID` - Cognito User Pool ID
- `APPSYNC_API_ID` - AppSync API ID

## Files

- `.env` - **Your configuration (never commit!)** - gitignored
- `.env.example` - Template for .env configuration
- `deploy.sh` - Deployment script (reads from .env)
- `app.py` - CDK app entry point (loads .env)
- `cdk/cdk_stack.py` - Main infrastructure stack

## Manual Deployment

```bash
# Synthesis only
npx cdk synth

# Deploy
npx cdk deploy --require-approval never

# Destroy
npx cdk destroy
```

## Security Note

⚠️ **Never commit `.env` to version control!** It contains environment-specific configuration and potentially sensitive information like:
- Domain names
- AWS account IDs
- Resource identifiers

The `.env` file is automatically excluded by `.gitignore`.
