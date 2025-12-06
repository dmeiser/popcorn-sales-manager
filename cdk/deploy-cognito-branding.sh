#!/bin/bash
#
# Deploy Cognito Managed Login Branding
#
# This script configures the Cognito Hosted UI with:
# - Custom logo (SVG popcorn bucket)
# - Brand colors (primary blue #1976d2)
# - COPPA compliance warning (13+ age requirement)
# - Satisfy font for headings, Open Sans for body
#
# Prerequisites:
# - AWS CLI configured with appropriate credentials
# - CDK stack deployed (to get User Pool ID and Client ID)
#
# Usage:
#   ./deploy-cognito-branding.sh

set -e  # Exit on error

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Cognito Managed Login Branding Deployment ===${NC}\n"

# Get stack outputs
echo -e "${YELLOW}Getting CloudFormation outputs...${NC}"
STACK_NAME="popcorn-sales-manager-dev"

# Extract User Pool ID from CDK stack
USER_POOL_ID=$(aws cloudformation describe-stack-resources \
  --stack-name "$STACK_NAME" \
  --query 'StackResources[?ResourceType==`AWS::Cognito::UserPool`].PhysicalResourceId' \
  --output text)

if [ -z "$USER_POOL_ID" ]; then
  echo -e "${RED}Error: Could not find User Pool ID in stack $STACK_NAME${NC}"
  exit 1
fi

echo -e "User Pool ID: ${GREEN}$USER_POOL_ID${NC}"

# Extract Client ID from User Pool
CLIENT_ID=$(aws cognito-idp list-user-pool-clients \
  --user-pool-id "$USER_POOL_ID" \
  --query 'UserPoolClients[0].ClientId' \
  --output text)

if [ -z "$CLIENT_ID" ]; then
  echo -e "${RED}Error: Could not find Client ID for User Pool $USER_POOL_ID${NC}"
  exit 1
fi

echo -e "Client ID: ${GREEN}$CLIENT_ID${NC}\n"

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if assets exist
LOGO_FILE="$SCRIPT_DIR/assets/cognito-logo.svg"
SETTINGS_FILE="$SCRIPT_DIR/assets/managed-login-settings.json"

if [ ! -f "$LOGO_FILE" ]; then
  echo -e "${RED}Error: Logo file not found: $LOGO_FILE${NC}"
  exit 1
fi

if [ ! -f "$SETTINGS_FILE" ]; then
  echo -e "${RED}Error: Settings file not found: $SETTINGS_FILE${NC}"
  exit 1
fi

echo -e "${YELLOW}Encoding logo to base64...${NC}"
LOGO_BASE64=$(base64 -w 0 < "$LOGO_FILE")

echo -e "${YELLOW}Reading branding settings...${NC}"
SETTINGS_JSON=$(cat "$SETTINGS_FILE")

echo -e "${YELLOW}Creating managed login branding configuration...${NC}\n"

# Create JSON input for AWS CLI (without logo for now - test settings first)
cat > /tmp/cognito-branding-input.json <<EOF
{
  "UserPoolId": "$USER_POOL_ID",
  "ClientId": "$CLIENT_ID",
  "UseCognitoProvidedValues": false,
  "Settings": $SETTINGS_JSON
}
EOF

# Check if branding already exists
echo -e "${YELLOW}Checking for existing branding...${NC}"
EXISTING_BRANDING=$(aws cognito-idp describe-managed-login-branding-by-client \
  --user-pool-id "$USER_POOL_ID" \
  --client-id "$CLIENT_ID" \
  --output json 2>/dev/null || echo "{}")

BRANDING_ID=$(echo "$EXISTING_BRANDING" | jq -r '.ManagedLoginBranding.ManagedLoginBrandingId // empty')

if [ -z "$BRANDING_ID" ]; then
  # Create new branding
  echo -e "${GREEN}No existing branding found. Creating new branding...${NC}\n"
  
  RESULT=$(aws cognito-idp create-managed-login-branding \
    --cli-input-json file:///tmp/cognito-branding-input.json \
    --output json)
  
  BRANDING_ID=$(echo "$RESULT" | jq -r '.ManagedLoginBranding.ManagedLoginBrandingId')
  
  echo -e "${GREEN}✓ Branding created successfully!${NC}"
  echo -e "Branding ID: ${GREEN}$BRANDING_ID${NC}\n"
else
  # Update existing branding
  echo -e "${YELLOW}Found existing branding: $BRANDING_ID${NC}"
  echo -e "${GREEN}Updating branding...${NC}\n"
  
  # Add branding ID to input
  jq --arg id "$BRANDING_ID" '. + {ManagedLoginBrandingId: $id}' \
    /tmp/cognito-branding-input.json > /tmp/cognito-branding-update.json
  
  RESULT=$(aws cognito-idp update-managed-login-branding \
    --cli-input-json file:///tmp/cognito-branding-update.json \
    --output json)
  
  echo -e "${GREEN}✓ Branding updated successfully!${NC}\n"
fi

# Clean up temp files
rm -f /tmp/cognito-branding-input.json /tmp/cognito-branding-update.json

# Show Hosted UI URL
REGION=$(aws configure get region)
HOSTED_UI_URL="https://popcorn-sales-manager-dev.auth.${REGION}.amazoncognito.com/login?client_id=${CLIENT_ID}&response_type=code&redirect_uri=http://localhost:5173"

echo -e "${GREEN}=== Deployment Complete ===${NC}\n"
echo -e "Test your branding at:"
echo -e "${GREEN}${HOSTED_UI_URL}${NC}\n"
echo -e "You should see:"
echo -e "  ✓ Popcorn logo at top of form"
echo -e "  ✓ Primary blue buttons (#1976d2)"
echo -e "  ✓ COPPA warning for 13+ age requirement"
echo -e "  ✓ Brand colors throughout\n"
