# LocalStack Development

This project supports deploying to LocalStack for local development and testing.

## Prerequisites

1. **Docker** must be running
2. **LocalStack Community** (free) or **LocalStack Pro** (if OSS license approved)

## Quick Start

### 1. Start LocalStack

```bash
docker-compose up -d
```

This starts LocalStack with the following services:
- DynamoDB
- S3
- IAM
- Lambda
- Cognito (Pro only)
- AppSync (Pro only)
- CloudFront (Pro only)
- SNS/SES
- Kinesis Firehose
- CloudWatch
- EventBridge

### 2. Deploy Infrastructure

```bash
./deploy-localstack.sh
```

This script:
- Checks LocalStack is running
- Sets environment variables
- Bootstraps CDK
- Synthesizes the stack
- Deploys to LocalStack

### 3. Verify Deployment

```bash
# List DynamoDB tables
awslocal dynamodb list-tables

# List S3 buckets
awslocal s3 ls

# Scan DynamoDB table
awslocal dynamodb scan --table-name PsmApp
```

## Manual Deployment

If you prefer manual control:

```bash
# Set environment variables
export USE_LOCALSTACK=true
export AWS_DEFAULT_REGION=us-east-1
export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test

# Bootstrap CDK
uv run cdk bootstrap

# Synth stack
uv run cdk synth

# Deploy
uv run cdk deploy --require-approval never
```

## LocalStack Pro Features

If you have a LocalStack Pro license (free for OSS projects), you can use:

- **Cognito**: User Pools and social login
- **AppSync**: GraphQL API
- **CloudFront**: CDN distribution

Set your license key:

```bash
export LOCALSTACK_API_KEY=your-key-here
docker-compose up -d
```

## Troubleshooting

### LocalStack not running
```bash
docker-compose ps
docker-compose logs localstack
```

### Reset LocalStack state
```bash
docker-compose down -v
rm -rf localstack-data/
docker-compose up -d
```

### Check LocalStack health
```bash
curl http://localhost:4566/_localstack/health
```

## Differences from AWS

### Account ID
LocalStack uses account ID `000000000000`

### Endpoint
All services use `http://localhost:4566`

### Credentials
Use any credentials (e.g., `test` / `test`)

## Integration with uv

All commands use `uv run` to ensure proper Python environment:

```bash
uv run cdk synth
uv run cdk deploy
uv run cdk diff
```

## Data Persistence

LocalStack data persists in `localstack-data/` directory. This directory is gitignored.

To start fresh:
```bash
rm -rf localstack-data/
```

## LocalStack Pro OSS License

If you receive a LocalStack Pro OSS license:

1. Set your license key in `docker-compose.yml` or `.env`
2. Restart LocalStack
3. Cognito, AppSync, and CloudFront will be available

See [Step 4 in TODO.md](TODO.md#step-4-apply-for-localstack-pro-oss-license) for application details.
