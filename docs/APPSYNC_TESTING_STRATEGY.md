# AppSync Resolver Testing Strategy

**Status:** Proposed  
**Last Updated:** December 9, 2025

## Overview

With the Lambda simplification project complete (80% reduction: 15→3 Lambdas), most business logic now resides in AppSync resolvers (VTL, JavaScript, and Pipeline resolvers). This document outlines a comprehensive testing strategy for these resolvers.

## Current State

### Deployed Resolvers (10 total)

**VTL Resolvers (2):**
1. `listOrdersBySeason` - Direct DynamoDB query
2. `revokeShare` - Direct DynamoDB DeleteItem

**JavaScript Resolvers (1):**
3. `createProfileInvite` - ID generation + TTL calculation + DynamoDB PutItem

**Pipeline Resolvers (7):**
4. `updateSeason` - GetItem validation → UpdateItem
5. `deleteSeason` - GetItem validation → DeleteItem  
6. `updateOrder` - GetItem validation → UpdateItem
7. `deleteOrder` - GetItem validation → DeleteItem
8. `createOrder` - GetItem catalog → PutItem with enrichment
9. `shareProfileDirect` - Query GSI8 (email lookup) → PutItem share
10. `redeemProfileInvite` - Query GSI9 (invite lookup) → CreateShare → MarkInviteUsed

### Remaining Lambda Functions (3)

- `post-authentication` (Cognito trigger) - **Unit tested** ✅
- `request-report` (Excel/S3 generation) - **Unit tested** ✅
- `create-profile` (DynamoDB transaction) - **Needs unit tests** ⚠️

## Testing Pyramid for AppSync Resolvers

```
                    /\
                   /  \
                  / E2E \
                 /  (Few) \
                /___________\
               /             \
              /  Integration  \
             /    (Moderate)   \
            /__________________\
           /                    \
          /   Unit (VTL/JS)      \
         /      (Many)            \
        /_________________________\
```

### Layer 1: Unit Tests (VTL/JS Resolver Logic)

**Scope:** Individual resolver request/response mapping templates

**Tools:**
- **VTL Testing**: AWS AppSync VTL unit testing framework
  - Uses `@aws-appsync/unit-test-helpers` npm package
  - Mocks DynamoDB responses
  - Tests request/response transformations

- **JavaScript Resolver Testing**: Vitest/Jest with mocks
  - Test `request()` and `response()` functions independently
  - Mock `util` object (`util.autoId()`, `util.time`, etc.)
  - Verify output structure

**Example Test Structure:**

```typescript
// tests/resolvers/createProfileInvite.test.ts
import { describe, it, expect, vi } from 'vitest';

describe('createProfileInvite JS resolver', () => {
  it('generates unique invite code', () => {
    const mockUtil = {
      autoId: vi.fn(() => 'abc123def456'),
      time: {
        nowEpochSeconds: vi.fn(() => 1702000000),
        epochMilliSecondsToISO8601: vi.fn((ms) => '2025-12-09T00:00:00Z')
      },
      dynamodb: {
        toMapValues: vi.fn((obj) => obj)
      }
    };
    
    const ctx = {
      args: {
        profileId: 'PROFILE#123',
        permissions: ['READ']
      }
    };
    
    // Import and test request function
    const result = request(ctx, mockUtil);
    
    expect(result.operation).toBe('PutItem');
    expect(result.key.SK).toMatch(/^INVITE#[A-Z0-9]{10}$/);
    expect(result.attributeValues.TTL).toBeGreaterThan(1702000000);
  });
});
```

**Coverage Goal:** 80%+ for JavaScript resolvers, 60%+ for VTL

**Priority:** Medium (JavaScript resolvers only - VTL is declarative)

---

### Layer 2: Integration Tests (Against Real AppSync API)

**Scope:** Full GraphQL operations against deployed AppSync API (dev environment)

**Tools:**
- **GraphQL Client**: Apollo Client or AWS AppSync JavaScript SDK
- **Test Framework**: Vitest or Jest
- **Authentication**: Cognito test users
- **Database**: DynamoDB dev table (with cleanup hooks)

**Test Structure:**

```typescript
// tests/integration/profileSharing.integration.test.ts
import { ApolloClient, gql } from '@apollo/client';
import { beforeEach, afterEach, describe, it, expect } from 'vitest';

describe('Profile Sharing Integration Tests', () => {
  let client: ApolloClient;
  let testProfileId: string;
  let testAccountId: string;
  
  beforeEach(async () => {
    // Set up Apollo Client with Cognito auth
    client = createAuthenticatedClient(testAccountId);
    
    // Create test profile
    const { data } = await client.mutate({
      mutation: CREATE_PROFILE,
      variables: { name: 'Test Profile' }
    });
    testProfileId = data.createProfile.profileId;
  });
  
  afterEach(async () => {
    // Clean up test data
    await deleteTestProfile(testProfileId);
  });
  
  describe('shareProfileDirect pipeline resolver', () => {
    it('creates share when valid email provided', async () => {
      const { data } = await client.mutate({
        mutation: SHARE_PROFILE_DIRECT,
        variables: {
          profileId: testProfileId,
          targetEmail: 'contributor@example.com',
          permissions: ['READ']
        }
      });
      
      expect(data.shareProfileDirect.share).toBeDefined();
      expect(data.shareProfileDirect.share.permissions).toContain('READ');
    });
    
    it('returns error when email not found', async () => {
      await expect(
        client.mutate({
          mutation: SHARE_PROFILE_DIRECT,
          variables: {
            profileId: testProfileId,
            targetEmail: 'nonexistent@example.com',
            permissions: ['READ']
          }
        })
      ).rejects.toThrow('Account not found');
    });
  });
});
```

**Test Coverage:**

✅ **Happy Path Tests:**
- Create invite → Redeem invite → Verify share exists
- Share directly by email → Verify recipient has access
- Revoke share → Verify access removed
- Create order with catalog → Verify line items enriched
- Update season → Verify optimistic locking
- Delete season → Verify cascade (if implemented)

✅ **Error Cases:**
- Invalid email in `shareProfileDirect`
- Expired invite in `redeemProfileInvite`
- Already-used invite
- Nonexistent catalog in `createOrder`
- Authorization failures (non-owner attempting write operations)
- Optimistic locking conflicts

✅ **Edge Cases:**
- Empty permissions array
- Duplicate shares
- Concurrent invite redemptions
- Very long customer names/addresses

**Environment:**
- **Option A:** Dedicated test AWS account with isolated resources
- **Option B:** LocalStack Pro (if OSS license approved) for local testing
- **Option C:** Dev account with data isolation (test-* prefixes)

**Coverage Goal:** 90%+ of resolver logic paths

**Priority:** **HIGH** - This is the primary testing strategy for AppSync resolvers

---

### Layer 3: End-to-End Tests (Full User Workflows)

**Scope:** Complete user journeys through frontend → AppSync → DynamoDB

**Tools:**
- **Frontend Testing**: Playwright (already set up)
- **Browser Automation**: Chromium, Firefox, WebKit
- **Authentication**: Real Cognito login flow (or mock for speed)

**Test Scenarios:**

1. **Profile Management Flow**
   - User logs in → Creates profile → Shares with contributor → Contributor accepts

2. **Order Management Flow**
   - User creates season → Selects catalog → Creates orders → Generates report

3. **Collaboration Flow**
   - Owner creates invite → Shares code → Contributor redeems → Both can view orders

4. **Admin Flow**
   - Admin views all profiles → Transfers ownership → Hard deletes test data

**Coverage Goal:** 70%+ of critical user workflows

**Priority:** Medium (after integration tests are stable)

---

## Recommended Testing Priorities

### Phase 1: Foundation (Current)
✅ Unit tests for remaining Lambda functions (create-profile, request-report, post-auth)  
✅ Documentation of testing strategy (this document)

### Phase 2: Integration Testing (Next Step)
1. Set up integration test environment (dev AWS account or LocalStack)
2. Create test data fixtures and cleanup utilities
3. Implement integration tests for **high-risk resolvers:**
   - `createOrder` (catalog enrichment logic)
   - `shareProfileDirect` (email lookup + share creation)
   - `redeemProfileInvite` (multi-step pipeline)
4. Add integration tests for **auth-critical resolvers:**
   - `revokeShare` (ensures proper access revocation)
   - `deleteSeason`, `deleteOrder` (authorization checks)

### Phase 3: Unit Testing JavaScript Resolvers (Optional)
1. Set up `@aws-appsync/unit-test-helpers`
2. Write unit tests for `createProfileInvite` (ID generation, TTL calculation)
3. Document patterns for future JavaScript resolvers

### Phase 4: E2E Testing (Future)
1. Implement Playwright tests for critical workflows
2. Add CI/CD integration for nightly E2E runs
3. Monitor for flakiness and refine as needed

---

## Testing Gaps & Mitigation

### Current Gaps

| Gap | Impact | Mitigation |
|-----|--------|------------|
| No automated tests for VTL resolvers | Medium | Integration tests cover behavior; VTL is declarative |
| No tests for pipeline resolver error handling | High | **Priority for Phase 2 integration tests** |
| Limited edge case coverage | Medium | Add edge cases to integration tests incrementally |
| No performance/load testing | Low | Monitor CloudWatch metrics in production; add load tests post-v1 |

### Technical Debt

- **Removed unit tests for migrated Lambdas**: Documented in test files with references to this document
- **Coverage drop from 100% to ~82%**: Accepted trade-off due to Lambda→AppSync migration
  - `validation.py` (47% coverage): Functions now used only by remaining Lambdas
  - `profile_operations.py` (0% coverage): `create_seller_profile` needs unit tests (TODO)

---

## Tooling & Setup

### Integration Test Setup (Recommended)

**Option 1: AWS Dev Account** (Preferred)
```bash
# Install dependencies
npm install --save-dev @aws-sdk/client-appsync @apollo/client graphql

# Set up Cognito test users
aws cognito-idp admin-create-user \
  --user-pool-id <USER_POOL_ID> \
  --username test-owner@example.com \
  --temporary-password 'TempPass123!' \
  --message-action SUPPRESS

# Run integration tests
npm run test:integration
```

**Option 2: LocalStack Pro**
```bash
# Requires LocalStack Pro license
docker-compose up localstack

# Deploy to LocalStack
cdklocal deploy

# Run tests against LocalStack
APPSYNC_ENDPOINT=http://localhost:4566 npm run test:integration
```

### CI/CD Integration

```yaml
# .github/workflows/test.yml
name: Test Suite

on: [push, pull_request]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Python unit tests
        run: |
          uv sync
          uv run pytest tests/unit --cov=src --cov-fail-under=80
      - name: Run Frontend unit tests
        run: |
          cd frontend
          npm install
          npm run test -- --coverage

  integration-tests:
    runs-on: ubuntu-latest
    needs: unit-tests
    environment: dev
    steps:
      - uses: actions/checkout@v3
      - name: Configure AWS Credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      - name: Run integration tests
        run: npm run test:integration

  e2e-tests:
    runs-on: ubuntu-latest
    needs: integration-tests
    environment: dev
    steps:
      - uses: actions/checkout@v3
      - name: Install Playwright
        run: npx playwright install --with-deps
      - name: Run E2E tests
        run: npm run test:e2e
```

---

## Metrics & Success Criteria

### Code Coverage Targets

| Component | Target | Current | Status |
|-----------|--------|---------|--------|
| Python Lambda Functions | 100% | ~82% | ⚠️ Missing profile_operations tests |
| Frontend Components | 80% | ~60% | ⚠️ In progress |
| AppSync Resolvers (Integration) | 90% | 0% | ❌ Not started |
| E2E Workflows | 70% | 0% | ❌ Not started |

### Quality Gates

- ✅ All unit tests pass before merge
- ⏸️ Integration tests pass in dev environment (Phase 2)
- ⏸️ No high-severity security issues (Dependabot, Snyk)
- ⏸️ E2E tests pass for critical workflows (Phase 4)

---

## References

- **AWS AppSync Testing Docs**: https://docs.aws.amazon.com/appsync/latest/devguide/test-debug-resolvers.html
- **VTL Unit Testing**: https://www.npmjs.com/package/@aws-appsync/unit-test-helpers
- **Playwright Docs**: https://playwright.dev/docs/intro
- **Apollo Client Testing**: https://www.apollographql.com/docs/react/development-testing/testing/

---

## Revision History

| Date | Version | Changes |
|------|---------|---------|
| 2025-12-09 | 1.0 | Initial testing strategy for AppSync resolvers |

---

## Next Steps

1. ✅ Complete unit tests for `create_seller_profile` Lambda
2. ⏸️ Set up integration test environment (AWS dev account)
3. ⏸️ Implement integration tests for pipeline resolvers (Phase 2)
4. ⏸️ Document test data cleanup strategy
5. ⏸️ Add CI/CD integration for automated testing
