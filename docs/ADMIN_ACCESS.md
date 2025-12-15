# Admin Access Control

## Overview

Admin access in KernelWorx is controlled exclusively through **AWS Cognito User Pool Groups**. Users must be manually added to the `ADMIN` group in AWS Cognito to gain admin privileges.

**Security by Design:**
- ❌ No frontend-based admin creation
- ❌ No "first user becomes admin" logic
- ✅ Manual AWS-based admin assignment only
- ✅ Group membership checked on every login

## How It Works

1. **Cognito Group**: The `ADMIN` group exists in the Cognito User Pool
2. **Post-Authentication Trigger**: After each login, a Lambda function checks if the user is in the `ADMIN` group
3. **DynamoDB Account**: The `isAdmin` flag in the Account record is updated based on group membership
4. **Frontend Authorization**: The frontend reads `isAdmin` from the GraphQL `getMyAccount` query

## Adding an Admin User

### Option 1: Using the Helper Script (Recommended)

```bash
cd /home/dm/code/popcorn-sales-manager
./scripts/add-admin.sh <email-or-username>
```

Example:
```bash
./scripts/add-admin.sh dmeiser@gmail.com
```

### Option 2: Using AWS CLI Directly

```bash
aws cognito-idp admin-add-user-to-group \
  --user-pool-id us-east-1_G1E0XFifR \
  --username <email-or-cognito-username> \
  --group-name "ADMIN"
```

### Option 3: Using AWS Console

1. Go to **AWS Console** → **Cognito** → **User Pools**
2. Select user pool: `kernelworx-users-dev`
3. Go to **Users** tab
4. Click on the user
5. Go to **Groups** tab
6. Click **Add user to group**
7. Select **ADMIN** group
8. Click **Add**

## Important Notes

- **User must log out and log back in** for group membership to take effect
- The `isAdmin` flag is updated on every login via the post-authentication Lambda trigger
- Removing a user from the ADMIN group will revoke admin privileges on their next login
- Group membership is read from the Cognito JWT token's `cognito:groups` claim

## Verifying Admin Status

### Check User's Groups in Cognito

```bash
aws cognito-idp admin-list-groups-for-user \
  --user-pool-id us-east-1_G1E0XFifR \
  --username <email-or-username>
```

### Check Account Record in DynamoDB

```bash
aws dynamodb get-item \
  --table-name kernelworx-app-dev \
  --key '{"PK": {"S": "ACCOUNT#<account-id>"}, "SK": {"S": "METADATA"}}' \
  --query 'Item.isAdmin'
```

## Security Considerations

- **Principle of Least Privilege**: Only grant admin access when absolutely necessary
- **Audit Trail**: All admin actions should be logged (future enhancement)
- **Manual Process**: The requirement to use AWS CLI/Console prevents accidental or unauthorized admin creation
- **Token-Based**: Admin status is verified on every request via JWT token validation

## Removing Admin Access

```bash
aws cognito-idp admin-remove-user-from-group \
  --user-pool-id us-east-1_G1E0XFifR \
  --username <email-or-username> \
  --group-name "ADMIN"
```

User will lose admin privileges on their next login.
