#!/bin/bash
#
# Deploy CDK stack to LocalStack
#
# Usage:
#   ./deploy-localstack.sh
#

set -e

echo "============================================================"
echo "Deploying Popcorn Sales Manager to LocalStack"
echo "============================================================"
echo ""

# Check if LocalStack is running
if ! docker ps | grep -q popcorn-sales-localstack; then
    echo "❌ LocalStack is not running. Start it with: docker-compose up -d"
    exit 1
fi

echo "✅ LocalStack is running"
echo ""

# Set environment variables for LocalStack
export AWS_DEFAULT_REGION=us-east-1
export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
export USE_LOCALSTACK=true
export LOCALSTACK_ENDPOINT=http://localhost:4566

# Use cdklocal wrapper if available, otherwise use cdk with endpoint override
if command -v cdklocal &> /dev/null; then
    echo "Using cdklocal wrapper..."
    CDK_CMD="cdklocal"
else
    echo "Using cdk with LocalStack endpoint..."
    CDK_CMD="uv run cdk"
    export CDK_DEFAULT_ACCOUNT=000000000000
    export CDK_DEFAULT_REGION=us-east-1
fi

echo ""
echo "Bootstrapping CDK (if needed)..."
$CDK_CMD bootstrap

echo ""
echo "Synthesizing stack..."
$CDK_CMD synth

echo ""
echo "Deploying stack..."
$CDK_CMD deploy --require-approval never

echo ""
echo "============================================================"
echo "✅ Deployment complete!"
echo "============================================================"
echo ""
echo "LocalStack endpoint: http://localhost:4566"
echo ""
echo "To interact with resources:"
echo "  awslocal dynamodb list-tables"
echo "  awslocal s3 ls"
echo ""
