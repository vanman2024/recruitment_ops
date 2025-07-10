---
allowed-tools: Bash, TodoWrite, mcp__supabase-v3__update_data, mcp__github__add_issue_comment
description: Run complete test suite in order - unit, integration, e2e, then update status
---

## Context
- Changed files: !`git diff --name-only HEAD`
- Current branch: !`git branch --show-current`
- Test configuration: @test_suite/docs/STANDARD_TESTING_CHECKLIST.md
- CI configuration: @.github/workflows/backend-tests.yml

## Your task

Execute the complete testing workflow in proper order:

### 1. Environment Setup
```bash
cd /home/gotime2022/devloop3
source venv/bin/activate
python backend/utils/environment_validator.py
```

### 2. Unit Tests
```bash
echo "=== Running Unit Tests ==="
python -m pytest test_suite/tests/unit/ -xvs
```

### 3. Integration Tests
```bash
echo "=== Running Integration Tests ==="
# Start server
cd backend && python unified_backend.py &
SERVER_PID=$!
sleep 5

# Run integration tests
python -m pytest test_suite/tests/integration/ -xvs

# Test API endpoints
curl http://localhost:8891/health
curl http://localhost:8891/api/github/webhook-status

# Stop server
kill $SERVER_PID
```

### 4. E2E Tests (if UI changes)
```bash
echo "=== Running E2E Tests ==="
python -m pytest test_suite/tests/e2e/ -xvs
```

### 5. Security Checks
```bash
echo "=== Security Scan ==="
grep -r "sk-" . --exclude-dir=venv --exclude-dir=.git || echo "✓ No API keys found"
grep -r "password.*=.*['\"]" . --exclude-dir=venv || echo "✓ No hardcoded passwords"
```

### 6. Update Database Status
After all tests pass:
- Use `mcp__supabase-v3__update_data` to update task with test results
- Fields: test_status, test_output, tested_at

### 7. Update GitHub Issue
- Use `mcp__github-http__add_issue_comment` to add test summary
- Include coverage percentage and key results

### Output Format
```
TEST SUMMARY
============
Unit Tests: PASS/FAIL (X/Y tests)
Integration Tests: PASS/FAIL (X/Y tests)
E2E Tests: PASS/FAIL (X/Y tests)
Security: PASS/FAIL
Coverage: XX%

Ready for PR: YES/NO
```

This chains all testing types in the correct order!