---
description: Procedure for executing the master quality gate (make check) to validate formatting, typing, testing, and security.
---

# Workflow: Running the Master Quality Gate

## Objective
Execute the comprehensive verification pipeline (`make check`) before committing code, opening pull requests, or transitioning phases.

## Execution Steps

### 1. Execute Unified Quality Target
From the repository root, run:
```bash
make check
```

### 2. Breakdown of Automated Quality Stages
The target executes the following sub-checks in sequence:

1. **Python Formatting & Linting:**
   ```bash
   uv run ruff format --check backend/
   uv run ruff check backend/
   ```
2. **Python Static Type Checking:**
   ```bash
   uv run mypy backend/
   ```
3. **Frontend Linting & Type Checking:**
   ```bash
   pnpm --dir frontend lint
   pnpm --dir frontend typecheck
   ```
4. **Hermetic Unit & Property Tests:**
   ```bash
   uv run pytest backend/tests/unit
   uv run pytest backend/tests/property
   ```
5. **Collector Contract & Integration Tests:**
   ```bash
   uv run pytest backend/tests/contract
   uv run pytest backend/tests/integration
   ```
6. **Security & Vulnerability Scans:**
   ```bash
   uv run pytest backend/tests/security
   gitleaks detect --source . -v
   uv run pip-audit
   pnpm --dir frontend audit
   ```

### 3. Remediation on Failure
- If format errors occur: run `uv run ruff format backend/` and `pnpm --dir frontend format`.
- If security lint fails on leaks: rotate the exposed token immediately and verify scrubbing.
- If contract tests fail: verify whether upstream schema drift occurred and update fixtures/schemas accordingly.

