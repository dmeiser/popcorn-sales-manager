# VTL Resolver Implementation Notes

## Overview

This document describes the VTL (Velocity Template Language) resolvers implemented for the Popcorn Sales Manager GraphQL API, including their capabilities and limitations.

## Implemented Resolvers

### Query Resolvers (100% Complete)

All 8 query resolvers are fully functional using VTL with DynamoDB:

1. **getMyAccount** - Direct GetItem on `ACCOUNT#<sub>`
2. **listMyProfiles** - Query on account with `begins_with(SK, "PROFILE#")`
3. **listSharedProfiles** - Query on GSI1 for shared profiles
4. **getProfile** - Query on GSI4 by profileId
5. **getSeason** - Query on GSI5 by seasonId
6. **listSeasonsByProfile** - Query on profile with `begins_with(SK, "SEASON#")`
7. **getOrder** - Query on GSI6 by orderId
8. **listOrdersBySeason** - Query on season with `begins_with(SK, "ORDER#")`

### Mutation Resolvers

#### Fully Functional ✅

1. **createSellerProfile** - PutItem with auto-generated profileId
   - Creates profile under `ACCOUNT#<sub>` partition
   - Sets ownership and initial permissions
   - Returns created profile

2. **updateSellerProfile** - UpdateItem with conditional check
   - Updates profile name
   - Enforces ownership (condition: `ownerAccountId = :ownerId`)
   - Returns updated profile

3. **createSeason** - PutItem with auto-generated seasonId
   - Creates season under profile partition
   - Handles optional `endDate`
   - Returns created season

4. **createOrder** - PutItem with auto-generated orderId
   - Creates order under season partition
   - Calculates `totalAmount` from lineItems in VTL
   - Sets GSI2PK/GSI2SK for orders-by-profile queries
   - Handles optional fields (customerPhone, customerAddress, notes)
   - Returns created order

5. **revokeShare** - VTL DeleteItem with condition ✅ **DEPLOYED**
   - Deletes share by profileId + targetAccountId
   - Simple conditional delete operation

6. **Profile Sharing Mutations** (Lambda-based - fully functional)
   - createProfileInvite (Lambda)
   - redeemProfileInvite (Lambda)
   - shareProfileDirect (Lambda)

#### Migrated to Pipeline Resolvers ✅

7. **updateSeason** - Pipeline resolver (GSI7 lookup → UpdateItem) ✅ **DEPLOYED**
   - **Implementation**: 2-step pipeline with LookupSeasonFn + UpdateSeasonFn
   - **JavaScript**: Uses AppSync JS runtime for dynamic update expressions
   - **Authorization**: Simplified to Cognito-only (not full share-based checks)

8. **deleteSeason** - Pipeline resolver (GSI7 lookup → DeleteItem) ✅ **DEPLOYED**
   - **Implementation**: 2-step pipeline with LookupSeasonFn + DeleteSeasonFn
   - **JavaScript**: Uses AppSync JS runtime
   
9. **updateOrder** - Pipeline resolver (GSI6 lookup → UpdateItem) ✅ **DEPLOYED**
   - **Implementation**: 2-step pipeline with LookupOrderFn + UpdateOrderFn
   - **JavaScript**: Handles all order fields including lineItems and totalAmount recalculation

10. **deleteOrder** - Pipeline resolver (GSI6 lookup → DeleteItem) ✅ **DEPLOYED**
   - **Implementation**: 2-step pipeline with LookupOrderFn + DeleteOrderFn
   - **JavaScript**: Uses AppSync JS runtime

#### Legacy (Previously Partially Implemented - Now Removed)

~~**updateSeason** - Query-based approach with limitations~~
~~**updateOrder** - Query-based stub~~
~~**deleteOrder** - Query-based stub~~

These have been replaced with pipeline resolvers (see above).

## VTL Limitations

### Single Operation Per Resolver

VTL resolvers can only execute ONE DynamoDB operation per request/response cycle. This creates challenges for:

1. **Updates requiring GSI lookups**:
   - Problem: Need to query GSI to find PK/SK, then update the item
   - VTL: Can only do Query OR Update, not both
   - Solution: Pipeline resolvers or Lambda

2. **Deletes requiring GSI lookups**:
   - Problem: Need to find item via GSI before deleting
   - VTL: Can only do Query OR Delete, not both
   - Solution: Pipeline resolvers or Lambda

3. **Complex authorization checks**:
   - Problem: Check if user owns profile before updating season
   - VTL: Limited to conditional expressions in single operation
   - Solution: Lambda with proper auth logic

### No Cross-Item Operations

VTL cannot:
- Update multiple items atomically
- Perform batch operations
- Implement transactions
- Aggregate data from multiple queries

### Limited String/Math Operations

VTL has basic string manipulation but:
- No complex parsing
- Limited date arithmetic
- No regex support
- Basic math only (we use it for totalAmount calculation)

## Recommendations

### For Production Use

1. **Keep VTL for Simple Operations**:
   - Direct GetItem/PutItem where PK/SK are known
   - Simple Query operations
   - Basic validations via conditional expressions

2. **Use Lambda for Complex Operations**:
   - Any mutation requiring GSI lookup first
   - Multi-step workflows
   - Complex authorization logic
   - Batch operations
   - External API calls

3. **Consider Pipeline Resolvers**: ✅ **NOW IMPLEMENTED**
   - Chain multiple AppSync functions
   - Query GSI → UpdateItem/DeleteItem as separate functions
   - Better than Lambda for pure DynamoDB operations
   - **Deployed**: updateSeason, deleteSeason, updateOrder, deleteOrder

### Migration Status (Updated December 2025)

**Phase 1 & 2 Complete** ✅

1. **VTL Resolvers Deployed**:
   - ✅ listOrdersBySeason (VTL Query)
   - ✅ revokeShare (VTL DeleteItem)

2. **Pipeline Resolvers Deployed**:
   - ✅ updateSeason (GSI7 lookup → UpdateItem)
   - ✅ deleteSeason (GSI7 lookup → DeleteItem)
   - ✅ updateOrder (GSI6 lookup → UpdateItem)
   - ✅ deleteOrder (GSI6 lookup → DeleteItem)

**Lambda Count**: Reduced from 15 to ~9 (40% reduction)

~~To complete Phase 1 CRUD mutations:~~ **COMPLETED**

Legacy code examples removed - see `TODO_SIMPLIFY_LAMBDA.md` for current migration plan.

## Testing Status

### Tested and Working ✅

- createSellerProfile: ✅ Creates profile with auto-ID
- updateSellerProfile: ✅ Updates name with ownership check
- createSeason: ✅ Creates season with auto-ID
- createOrder: ✅ Creates order with total calculation
- listOrdersBySeason: ✅ VTL Query resolver (DEPLOYED)
- revokeShare: ✅ VTL DeleteItem resolver (DEPLOYED)
- updateSeason: ✅ Pipeline resolver (DEPLOYED)
- deleteSeason: ✅ Pipeline resolver (DEPLOYED)
- updateOrder: ✅ Pipeline resolver (DEPLOYED)
- deleteOrder: ✅ Pipeline resolver (DEPLOYED)
- All query resolvers: ✅ (tested in previous sessions)

### Needs Testing/Fixing ⚠️

None - all Phase 1 & 2 resolvers are deployed and operational.

## Current Implementation Status

**CRUD Functionality: 100% Complete** ✅

- ✅ Create operations: 100% (Profile, Season, Order)
- ✅ Read operations: 100% (All queries working)
- ✅ Update operations: 100% (Profile via VTL, Season/Order via Pipeline)
- ✅ Delete operations: 100% (Order/Season via Pipeline, Share via VTL)

**Resolver Type Distribution**:
- VTL Resolvers: Queries + simple mutations (listOrdersBySeason, revokeShare)
- Pipeline Resolvers: Complex mutations requiring GSI lookup (updateSeason, deleteSeason, updateOrder, deleteOrder)
- Lambda Resolvers: External dependencies, transactions, Cognito triggers (~9 remaining)
