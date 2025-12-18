#!/bin/bash
# Deployment script for Popcorn Sales Manager CDK stack
# Minimal configuration - most values are derived automatically

set -e

# Change to script directory
cd "$(dirname "$0")"

# Load environment variables from .env if it exists
if [ -f .env ]; then
    export $(grep -v '^#' .env | grep -v '^$' | xargs)
fi

# Environment defaults to 'dev' if not set
ENVIRONMENT="${ENVIRONMENT:-dev}"

# Region defaults to AWS_REGION env var or us-east-1
AWS_REGION="${AWS_REGION:-us-east-1}"
export AWS_REGION

echo "🚀 Deploying Popcorn Sales Manager"
echo "   Environment: $ENVIRONMENT"
echo "   Region: $AWS_REGION"
echo "   Account: ${AWS_ACCOUNT_ID:-<from AWS profile>}"
echo ""

# Build context arguments for resource import (optional, for migrations only)
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

# Support two-stage deployment for fresh installs
# Phase 1: Skip Cognito custom domain (set CREATE_COGNITO_DOMAIN=false)
# Phase 2: Add Cognito custom domain after DNS propagates (set CREATE_COGNITO_DOMAIN=true or unset)
if [ -n "$CREATE_COGNITO_DOMAIN" ]; then
    CONTEXT_ARGS="$CONTEXT_ARGS -c create_cognito_domain=$CREATE_COGNITO_DOMAIN"
fi

# Run deployment
echo "Running: npx cdk deploy -c environment=$ENVIRONMENT $CONTEXT_ARGS --require-approval never"
echo ""

npx cdk deploy -c environment=$ENVIRONMENT $CONTEXT_ARGS --require-approval never

echo ""
echo "✅ Deployment complete!"
