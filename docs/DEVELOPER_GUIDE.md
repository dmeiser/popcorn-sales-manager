## Developer Workflow Guide

Audience: contributors working on Popcorn Sales Manager. Focuses on day-to-day commands, quality bars, and deployment steps. Infra coverage is intentionally excluded from coverage gates per project policy.

### Testing
- **Backend Lambdas (Python)**
  - Unit tests (100% enforced):
    - From repo root: `uv run pytest tests/unit --cov=src --cov-fail-under=100`
- **Infrastructure/CDK (Python)**
  - No unit tests maintained; CDK coverage is intentionally excluded. Optional synth/snapshot checks are allowed locally but are not required.
- **Frontend (TypeScript)**
  - Unit/component tests with coverage: `npm run test -- --coverage`
  - E2E (optional): `npm run test:e2e` if configured.

### Code Quality
- **Python (app)**: `uv run ruff check src tests` • `uv run isort src/ tests/` • `uv run ruff format src/ tests/` • `uv run mypy src`
- **Python (cdk)**: `cd cdk && uv run ruff check cdk tests` • `uv run mypy cdk`
- **Frontend**: `npm run lint` • `npm run format` • `npm run typecheck`
- Coverage bars: app code is 100% (src, frontend); CDK infra is excluded from coverage enforcement.

### Deployment
- **Backend/CDK (dev only)**:
  - From `cdk/`: `./deploy.sh`
  - Preview first when making infra changes: `cdk diff` (respect dev-only deployment rule).
- **Frontend**:
  - From `frontend/`: `./deploy.sh` (ensure build succeeds locally with `npm run build`).

### Notes & Conventions
- Always use feature branches and PRs; never push directly to main.
- When running coverage, exclude CDK by scoping `--cov` to application packages (e.g., `--cov=src`).
- Prefer moto for AWS mocks in backend unit tests; LocalStack or AWS dev account for integration as needed.

---

## Code Patterns & Conventions

This section documents the key patterns and shared utilities used throughout the codebase.

### Backend Python Patterns

#### Centralized Validation (`src/utils/validation.py`)

All input validation for Lambda handlers should use the centralized validation module:

```python
from utils.validation import (
    validate_required_fields,
    validate_unit_number,
    validate_unit_fields,
)

# Validate required fields are present
validate_required_fields(data, ["profileId", "campaignName"])

# Validate unit number format (optional field)
validate_unit_number(unit_number, required=False)

# Validate complete unit information
validate_unit_fields(unit_type, unit_number, city, state)
```

All validation functions raise `AppError` with `ErrorCode.INVALID_INPUT` on failure.

#### DynamoDB Utilities (`src/utils/dynamodb.py`)

Use the centralized DynamoDB utilities for consistent table access:

```python
from utils.dynamodb import get_table, get_table_name

# Get a boto3 Table resource
table = get_table()

# Get just the table name
table_name = get_table_name()
```

#### ID Generation (`src/utils/ids.py`)

Use centralized ID generation for consistent formatting:

```python
from utils.ids import normalize_id, generate_unique_id

# Normalize user-provided IDs
profile_id = normalize_id(user_input)

# Generate new unique IDs
new_id = generate_unique_id()
```

#### Error Handling (`src/utils/errors.py`)

Use `AppError` for all application errors:

```python
from utils.errors import AppError, ErrorCode

raise AppError(ErrorCode.INVALID_INPUT, "Profile name is required")
raise AppError(ErrorCode.NOT_FOUND, "Campaign not found")
raise AppError(ErrorCode.UNAUTHORIZED, "Not authorized to view this profile")
```

### Frontend TypeScript Patterns

#### Form State Hook (`frontend/src/hooks/useFormState.ts`)

For dialog forms with multiple fields, use the `useFormState` hook:

```typescript
import { useFormState } from '../hooks/useFormState';

interface FormValues {
  name: string;
  email: string;
  isActive: boolean;
}

const getInitialValues = (): FormValues => ({
  name: '',
  email: '',
  isActive: true,
});

function MyDialog() {
  const { values, setValue, reset, isDirty } = useFormState(getInitialValues);
  
  return (
    <>
      <TextField
        value={values.name}
        onChange={(e) => setValue('name', e.target.value)}
      />
      <Button onClick={reset}>Reset</Button>
    </>
  );
}
```

The hook provides:
- `values` - Current form state
- `setValue(key, value)` - Update a single field
- `setValues(partial)` - Update multiple fields
- `reset()` - Reset to initial values
- `resetTo(values)` - Reset to specific values
- `isDirty` - Whether form has been modified

**When NOT to use `useFormState`:**
- Complex array state (product lists, line items) - use custom hooks
- Fields with special formatting (phone numbers) - use specialized hooks
- When the existing pattern is already well-organized with custom hooks

#### GraphQL Types (`frontend/src/types/index.ts`)

All GraphQL types are centralized and should be imported from the types module:

```typescript
import type { SellerProfile, Campaign, Order, Catalog } from '../types';
```

### CDK Infrastructure Patterns

#### Helper Utilities (`cdk/cdk/helpers.py`)

Use the centralized helpers for resource naming and configuration:

```python
from .helpers import (
    get_region_abbrev,
    get_context_bool,
    get_domain_names,
    make_resource_namer,
)

# Get region abbreviation for naming
region_abbrev = get_region_abbrev()  # e.g., "ue1"

# Get boolean from CDK context
enabled = get_context_bool(self, "feature_flag", default=True)

# Get environment-specific domain names
domains = get_domain_names("kernelworx.app", "dev")
# Returns: {"site_domain": "dev.kernelworx.app", "api_domain": "api.dev.kernelworx.app", ...}

# Create a resource naming function
rn = make_resource_namer("ue1", "dev")
bucket_name = rn("exports")  # "exports-ue1-dev"
```

#### Resolver Builder (`cdk/cdk/appsync/resolver_builder.py`)

For new AppSync resolvers, use the `ResolverBuilder` class:

```python
from .resolver_builder import ResolverBuilder

builder = ResolverBuilder(api, datasources, lambda_datasources, self)

# VTL resolver
builder.create_vtl_resolver(
    field_name="getMyAccount",
    type_name="Query",
    datasource_name="accounts",
    request_template=TEMPLATES_DIR / "request.vtl",
    response_template=TEMPLATES_DIR / "response.vtl",
)

# JavaScript resolver
builder.create_js_resolver(
    field_name="listItems",
    type_name="Query",
    datasource_name="items",
    code_file=RESOLVERS_DIR / "list_items.js",
)

# Pipeline resolver
builder.create_pipeline_resolver(
    field_name="createItem",
    type_name="Mutation",
    functions=[fn1, fn2, fn3],
    code_file=RESOLVERS_DIR / "create_item.js",
)

# Lambda resolver
builder.create_lambda_resolver(
    field_name="generateReport",
    type_name="Mutation",
    lambda_datasource_name="report_generator",
)
```