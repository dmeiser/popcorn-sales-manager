#!/usr/bin/env python3
import os

import aws_cdk as cdk

from cdk.cdk_stack import CdkStack


app = cdk.App()

# Determine if we're deploying to LocalStack
use_localstack = os.getenv("USE_LOCALSTACK", "false").lower() == "true"

# Configure environment
if use_localstack:
    # LocalStack configuration
    env = cdk.Environment(
        account="000000000000",  # LocalStack default account
        region=os.getenv("AWS_DEFAULT_REGION", "us-east-1"),
    )
    stack_name = "PopcornSalesManager-LocalStack"
else:
    # AWS configuration
    env = cdk.Environment(
        account=os.getenv("CDK_DEFAULT_ACCOUNT"),
        region=os.getenv("CDK_DEFAULT_REGION", "us-east-1"),
    )
    stack_name = "PopcornSalesManager"

CdkStack(
    app,
    "CdkStack",
    stack_name=stack_name,
    env=env,
    description="Popcorn Sales Manager - Core Infrastructure (DynamoDB, S3, IAM)",
)

app.synth()
