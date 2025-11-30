#!/usr/bin/env python3
import os

import aws_cdk as cdk

from cdk.cdk_stack import CdkStack


app = cdk.App()

# Get environment from context or environment variable (dev/prod)
env_name = app.node.try_get_context("environment") or os.getenv("ENVIRONMENT", "dev")

# Configure environment
env = cdk.Environment(
    account=os.getenv("CDK_DEFAULT_ACCOUNT"),
    region=os.getenv("CDK_DEFAULT_REGION", "us-east-1"),
)

# Environment-specific stack name
stack_name = f"popcorn-sales-manager-{env_name}"

CdkStack(
    app,
    f"CdkStack-{env_name}",
    stack_name=stack_name,
    env_name=env_name,
    env=env,
    description=f"Popcorn Sales Manager - Core Infrastructure ({env_name})",
)

app.synth()
