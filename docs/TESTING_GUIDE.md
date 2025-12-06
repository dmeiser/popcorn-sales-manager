# Testing Guide - Popcorn Sales Manager

## Testing the GraphQL API

### Prerequisites

1. **Cognito User Account**: You need a confirmed user in the Cognito User Pool
2. **AWS CLI**: Configured with appropriate credentials
3. **jq**: For JSON parsing (optional but helpful)

### User Pool Details

- **User Pool ID**: `us-east-1_m861e2MtM`
- **User Pool Name**: `popcorn-sales-manager-dev`
- **API Endpoint**: `https://twafinvov5dujcdoyhhlql56ea.appsync-api.us-east-1.amazonaws.com/graphql`
- **Auth Type**: `AMAZON_COGNITO_USER_POOLS`

### Creating a Test User

```bash
# Create a test user
aws cognito-idp admin-create-user \
  --user-pool-id us-east-1_m861e2MtM \
  --username testuser@example.com \
  --user-attributes Name=email,Value=testuser@example.com Name=email_verified,Value=true \
  --temporary-password TempPass123! \
  --message-action SUPPRESS

# Set permanent password
aws cognito-idp admin-set-user-password \
  --user-pool-id us-east-1_m861e2MtM \
  --username testuser@example.com \
  --password TestPassword123! \
  --permanent
```

### Getting an ID Token

```bash
# Get the User Pool Client ID
CLIENT_ID=$(aws cognito-idp list-user-pool-clients \
  --user-pool-id us-east-1_m861e2MtM \
  --query 'UserPoolClients[0].ClientId' \
  --output text)

# Authenticate and get tokens
aws cognito-idp initiate-auth \
  --auth-flow USER_PASSWORD_AUTH \
  --client-id $CLIENT_ID \
  --auth-parameters USERNAME=testuser@example.com,PASSWORD=TestPassword123! \
  --query 'AuthenticationResult.IdToken' \
  --output text
```

Save the ID token to an environment variable:
```bash
export ID_TOKEN="<token_from_above>"
```

### Testing Queries

#### 1. Test getMyAccount

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: $ID_TOKEN" \
  https://twafinvov5dujcdoyhhlql56ea.appsync-api.us-east-1.amazonaws.com/graphql \
  -d '{
    "query": "query { getMyAccount { accountId email isAdmin createdAt } }"
  }' | jq
```

**Expected Result**: Should return account details or "Account not found" (if account record doesn't exist in DynamoDB yet)

#### 2. Test listMyProfiles

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: $ID_TOKEN" \
  https://twafinvov5dujcdoyhhlql56ea.appsync-api.us-east-1.amazonaws.com/graphql \
  -d '{
    "query": "query { listMyProfiles { profileId scoutName ownerAccountId createdAt } }"
  }' | jq
```

**Expected Result**: Empty array `[]` (no profiles created yet)

#### 3. Test listSharedProfiles

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: $ID_TOKEN" \
  https://twafinvov5dujcdoyhhlql56ea.appsync-api.us-east-1.amazonaws.com/graphql \
  -d '{
    "query": "query { listSharedProfiles { profileId permissions sharedWithAccountId } }"
  }' | jq
```

**Expected Result**: Empty array `[]` (no shared profiles yet)

### Testing Mutations

#### 1. Create a Profile (using Lambda resolver)

First, you'll need to use the `createSellerProfile` mutation (if implemented) or manually insert data into DynamoDB.

#### 2. Create Profile Invite

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: $ID_TOKEN" \
  https://twafinvov5dujcdoyhhlql56ea.appsync-api.us-east-1.amazonaws.com/graphql \
  -d '{
    "query": "mutation { createProfileInvite(profileId: \"PROFILE#123\", permissions: [READ]) { inviteCode expiresAt } }"
  }' | jq
```

### Manual Data Insertion for Testing

To test the query resolvers, you can manually insert test data into DynamoDB:

```bash
# Insert a test account
aws dynamodb put-item \
  --table-name psm-app-dev \
  --item '{
    "PK": {"S": "ACCOUNT#<cognito_sub>"},
    "SK": {"S": "METADATA"},
    "accountId": {"S": "<cognito_sub>"},
    "email": {"S": "testuser@example.com"},
    "isAdmin": {"BOOL": false},
    "createdAt": {"S": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"}
  }'

# Insert a test profile
aws dynamodb put-item \
  --table-name psm-app-dev \
  --item '{
    "PK": {"S": "ACCOUNT#<cognito_sub>"},
    "SK": {"S": "PROFILE#profile-001"},
    "profileId": {"S": "PROFILE#profile-001"},
    "scoutName": {"S": "Test Scout"},
    "ownerAccountId": {"S": "<cognito_sub>"},
    "createdAt": {"S": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"}
  }'

# Insert a test season
aws dynamodb put-item \
  --table-name psm-app-dev \
  --item '{
    "PK": {"S": "PROFILE#profile-001"},
    "SK": {"S": "SEASON#season-001"},
    "seasonId": {"S": "SEASON#season-001"},
    "profileId": {"S": "PROFILE#profile-001"},
    "year": {"N": "2025"},
    "catalogId": {"S": "CATALOG#default"},
    "createdAt": {"S": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"}
  }'
```

Replace `<cognito_sub>` with the actual Cognito user's `sub` claim (from the ID token).

## Automated Testing

### Unit Tests

All backend code has 100% test coverage. Run tests with:

```bash
cd /home/dm/code/popcorn-sales-manager
uv run pytest tests/unit --cov=src --cov-fail-under=100
```

### Integration Tests (TODO)

Integration tests against LocalStack or AWS dev environment will be added in future phases.

## AppSync Console Testing

You can also test queries directly in the AWS AppSync console:

1. Navigate to: https://console.aws.amazon.com/appsync/home?region=us-east-1
2. Select: `popcorn-sales-manager-api-dev`
3. Click "Queries" in the left sidebar
4. Click "Login with User Pools"
5. Enter credentials and run queries interactively

## Deployed Resolvers

### Query Resolvers (DynamoDB VTL)

✅ **getMyAccount**: Returns account details for authenticated user  
✅ **getProfile**: Returns profile by ID (TODO: add authorization)  
✅ **listMyProfiles**: Lists all profiles owned by authenticated user  
✅ **listSharedProfiles**: Lists profiles shared with authenticated user (via GSI1)  
✅ **getSeason**: Returns season by ID  
✅ **listSeasonsByProfile**: Lists all seasons for a profile  
✅ **getOrder**: Returns order by ID  
✅ **listOrdersBySeason**: Lists all orders for a season  

### Mutation Resolvers (Lambda)

✅ **createProfileInvite**: Creates shareable invite code  
✅ **redeemProfileInvite**: Redeems invite code to gain access  
✅ **shareProfileDirect**: Directly shares profile with another user  
✅ **revokeShare**: Revokes profile access  

## Authorization Notes

- Most resolvers currently use `$ctx.identity.sub` for authentication
- Authorization checks (owner vs shared access) are **TODO** in most resolvers
- The `getProfile` resolver has a TODO comment for authorization
- Profile sharing mutations already implement proper authorization

## Next Steps

1. Implement remaining CRUD mutations (createProfile, updateProfile, createSeason, etc.)
2. Add proper authorization checks to all query resolvers
3. Create integration tests
4. Test end-to-end flows with real Cognito users
5. Document all GraphQL operations with examples
