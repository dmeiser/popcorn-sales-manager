#!/bin/bash
# Test share-related queries to diagnose DynamoDB errors

set -e

ENV=${1:-dev}
SHARES_TABLE="kernelworx-shares-ue1-${ENV}"
PROFILES_TABLE="kernelworx-profiles-ue1-${ENV}"

echo "Testing share queries for environment: $ENV"
echo "Shares table: $SHARES_TABLE"
echo "Profiles table: $PROFILES_TABLE"
echo ""

# Get all shares
echo "=== All Shares ==="
aws dynamodb scan --table-name "$SHARES_TABLE" --output json | \
  jq -r '.Items[] | "ProfileID: \(.profileId.S // "MISSING"), OwnerID: \(.ownerAccountId.S // "MISSING"), TargetID: \(.targetAccountId.S // "MISSING")"'
echo ""

# Try to get profiles for each share
echo "=== Testing BatchGetItem for each share ==="
aws dynamodb scan --table-name "$SHARES_TABLE" --output json | \
  jq -c '.Items[] | {profileId: .profileId.S, ownerAccountId: .ownerAccountId.S}' | \
  while IFS= read -r line; do
    PROFILE_ID=$(echo "$line" | jq -r '.profileId')
    OWNER_ID=$(echo "$line" | jq -r '.ownerAccountId')
    
    if [ "$PROFILE_ID" != "null" ] && [ "$OWNER_ID" != "null" ]; then
      echo "Testing: ownerAccountId=$OWNER_ID, profileId=$PROFILE_ID"
      aws dynamodb get-item \
        --table-name "$PROFILES_TABLE" \
        --key "{\"ownerAccountId\": {\"S\": \"$OWNER_ID\"}, \"profileId\": {\"S\": \"$PROFILE_ID\"}}" \
        --output json | jq '.Item // "NOT FOUND"'
      echo ""
    fi
  done

echo "✅ Done"
