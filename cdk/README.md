Two-stage CDK deploy
=====================

When the authoritative nameservers for your base domain are managed outside of Route53 (for example, Cloudflare), Cognito custom domains can fail during stack creation because Cognito requires the parent domain to actually resolve.

This repository supports a two-stage deploy to work around that:

1) Phase 1 — create site, CloudFront, DNS records (skip Cognito custom domain)

```bash
# deploy everything except the Cognito custom domain
npx cdk deploy -c environment=dev -c create_cognito_domain=false --require-approval never
```

2) Wait for CloudFront + Route53 to be visible (DNS propagation). Once the site domain (e.g. `dev.kernelworx.app`) resolves consistently to CloudFront, run Phase 2.

3) Phase 2 — create Cognito custom domain

```bash
# deploy again enabling the Cognito custom domain creation
npx cdk deploy -c environment=dev -c create_cognito_domain=true --require-approval never
```

Notes
- You can omit `-c create_cognito_domain=true` in phase 2 since the default is `true`.
- If you manage nameservers at your registrar, prefer pointing the domain to Route53 nameservers — that removes the need for two-stage deploys.
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
