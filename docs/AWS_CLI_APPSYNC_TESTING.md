# AWS CLI AppSync Resolver Testing Workflow

**Critical Discovery**: AWS CLI provides detailed TypeScript errors that CDK/CloudFormation deployments hide.

## The Problem

When deploying AppSync JS resolvers via CDK, errors are vague:
```
The code contains one or more errors
```

No line numbers, no specifics, no debugging information.

## The Solution

Use `aws appsync evaluate-code` CLI to test resolvers locally before deployment.

## Workflow

### 1. Get Your AppSync API ID

```bash
aws appsync list-graphql-apis --query 'graphqlApis[?name==`YOUR-API-NAME`].apiId' --output text
```

Example:
```bash
aws appsync list-graphql-apis --query 'graphqlApis[?name==`kernelworx-api-dev`].apiId' --output text
# Output: ymbwcstfmzbl7euhghyblmlkhu
```

### 2. Create Test Resolver File

Create `/tmp/test-resolver.js` with your resolver code:

```javascript
import { util } from '@aws-appsync/utils';

export function request(ctx) {
    const inviteCode = util.autoId().substring(0, 10).toUpperCase();
    const expirySeconds = 14 * 24 * 60 * 60;
    const expiresAtEpoch = util.time.nowEpochSeconds() + expirySeconds;
    const expiresAtISO = util.time.epochMilliSecondsToISO8601(expiresAtEpoch * 1000);
    
    return {
        operation: 'PutItem',
        key: util.dynamodb.toMapValues({
            PK: 'TEST',
            SK: 'INVITE#' + inviteCode
        }),
        attributeValues: util.dynamodb.toMapValues({
            inviteCode,
            expiresAt: expiresAtISO,
            TTL: expiresAtEpoch
        })
    };
}

export function response(ctx) {
    return ctx.result;
}
```

### 3. Test with AWS CLI

```bash
aws appsync evaluate-code \
  --runtime '{"name":"APPSYNC_JS","runtimeVersion":"1.0.0"}' \
  --code file:///tmp/test-resolver.js \
  --context '{"arguments":{},"identity":{"sub":"test-user"}}' \
  --function request
```

### 4. Read the Results

**Success Example**:
```json
{
    "evaluationResult": "{\"operation\":\"PutItem\",\"key\":{\"SK\":{\"S\":\"INVITE#DB19189C-3\"},\"PK\":{\"S\":\"TEST\"}},\"attributeValues\":{\"inviteCode\":{\"S\":\"DB19189C-3\"},\"expiresAt\":{\"S\":\"2025-12-22T21:22:08Z\"},\"TTL\":{\"N\":\"1766438528\"}}}"
}
```

**Error Example** (with line numbers and suggestions!):
```json
{
    "error": {
        "message": "code.js(16,36): error TS2551: Property 'epochSecondsToISO8601' does not exist on type 'TimeUtils'. Did you mean 'epochMilliSecondsToISO8601'?",
        "codeErrors": [
            {
                "errorType": "PARSE_ERROR",
                "location": {
                    "line": 16,
                    "column": 36,
                    "span": 21
                }
            }
        ]
    }
}
```

## Key Insights

1. **Time Utilities Require Milliseconds**:
   - ❌ `util.time.epochSecondsToISO8601()` - DOES NOT EXIST
   - ✅ `util.time.epochMilliSecondsToISO8601(epochSeconds * 1000)` - CORRECT

2. **CLI Shows TypeScript Errors**:
   - Property names, type mismatches, undefined variables
   - Line numbers and column positions
   - Suggestions for correct method names

3. **Faster Iteration**:
   - CLI test: ~1 second
   - CDK deployment: 2+ minutes
   - 100x faster debugging loop

## Common Context Patterns

### Mutation Context
```json
{
  "arguments": {
    "input": {
      "profileId": "PROFILE#123",
      "permissions": ["READ"]
    }
  },
  "identity": {
    "sub": "user-123"
  }
}
```

### Query Context
```json
{
  "arguments": {
    "seasonId": "SEASON#456"
  },
  "identity": {
    "sub": "user-123"
  }
}
```

## Testing Response Functions

Add `--function response` and provide mock DynamoDB results:

```bash
aws appsync evaluate-code \
  --runtime '{"name":"APPSYNC_JS","runtimeVersion":"1.0.0"}' \
  --code file:///tmp/test-resolver.js \
  --context '{"result":{"inviteCode":"ABC123"}}' \
  --function response
```

## Best Practices

1. **Always test locally first** before CDK deployment
2. **Start simple** - test basic operations before adding complexity
3. **Validate utilities** - confirm AppSync supports the method you're using
4. **Read TypeScript errors carefully** - they often suggest the correct method name
5. **Keep test files** in `/tmp/` for rapid iteration

## References

- [AppSync JavaScript Resolver Reference](https://docs.aws.amazon.com/appsync/latest/devguide/resolver-reference-js-version.html)
- [AppSync Time Utilities](https://docs.aws.amazon.com/appsync/latest/devguide/built-in-util-js.html#time-helpers-js)
- [AWS CLI evaluate-code](https://docs.aws.amazon.com/cli/latest/reference/appsync/evaluate-code.html)

---

**Last Updated**: December 2025  
**Related**: TODO_SIMPLIFY_LAMBDA.md Phase 1.3 resolution
