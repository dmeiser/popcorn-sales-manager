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