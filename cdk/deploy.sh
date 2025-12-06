#!/bin/bash
# Deployment script for Popcorn Sales Manager CDK stack
# Uses .env file for configuration

set -e

# Change to script directory
cd "$(dirname "$0")"

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "Please copy .env.example to .env and fill in your values:"
    echo "  cp .env.example .env"
    exit 1
fi

# Load environment variables from .env
export $(grep -v '^#' .env | xargs)

# Check required variables
if [ -z "$ENVIRONMENT" ]; then
    echo "❌ Error: ENVIRONMENT not set in .env"
    exit 1
fi

if [ -z "$BASE_DOMAIN" ]; then
    echo "❌ Error: BASE_DOMAIN not set in .env"
    exit 1
fi

echo "🚀 Deploying Popcorn Sales Manager"
echo "   Environment: $ENVIRONMENT"
echo "   Domain: $BASE_DOMAIN"
echo "   Account: ${AWS_ACCOUNT_ID:-<from AWS profile>}"
echo "   Region: ${AWS_REGION:-us-east-1}"
echo ""

# Build context arguments for resource import
CONTEXT_ARGS=""
if [ -n "$STATIC_BUCKET_NAME" ]; then
    CONTEXT_ARGS="$CONTEXT_ARGS -c static_bucket_name=$STATIC_BUCKET_NAME"
fi
if [ -n "$EXPORTS_BUCKET_NAME" ]; then
    CONTEXT_ARGS="$CONTEXT_ARGS -c exports_bucket_name=$EXPORTS_BUCKET_NAME"
fi
if [ -n "$TABLE_NAME" ]; then
    CONTEXT_ARGS="$CONTEXT_ARGS -c table_name=$TABLE_NAME"
fi
if [ -n "$USER_POOL_ID" ]; then
    CONTEXT_ARGS="$CONTEXT_ARGS -c user_pool_id=$USER_POOL_ID"
fi
if [ -n "$APPSYNC_API_ID" ]; then
    CONTEXT_ARGS="$CONTEXT_ARGS -c appsync_api_id=$APPSYNC_API_ID"
fi

# Run deployment
echo "Running: npx cdk deploy -c environment=$ENVIRONMENT $CONTEXT_ARGS --require-approval never"
echo ""

npx cdk deploy -c environment=$ENVIRONMENT $CONTEXT_ARGS --require-approval never

echo ""
echo "✅ Deployment complete!"
