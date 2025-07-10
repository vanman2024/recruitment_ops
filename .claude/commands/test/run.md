---
allowed-tools: Bash, TodoWrite
description: Run tests with smart detection and type selection
---

# 🧪 Smart Test Runner

**Arguments**: $ARGUMENTS

## Parse Test Type
!`echo "$ARGUMENTS" > /tmp/test-args.txt`
!`TYPE=$(cat /tmp/test-args.txt | awk '{print $1}'); [ -z "$TYPE" ] && TYPE="all"; echo "🎯 Test type: $TYPE"`

## Environment Check
!`[ -f package.json ] && echo "📦 Node.js project detected" || echo "🐍 Python project detected"`
!`[ -f pytest.ini ] || [ -f setup.cfg ] && echo "✅ Pytest configured" || echo "⚠️ No pytest config"`
!`[ -f jest.config.js ] || [ -f package.json ] && grep -q "jest" package.json && echo "✅ Jest configured" || echo "⚠️ No Jest config"`

## Run Tests Based on Type

### All Tests
!`TYPE=$(cat /tmp/test-args.txt | awk '{print $1}'); if [ "$TYPE" = "all" ]; then echo "🏃 Running all tests..."; fi`
!`TYPE=$(cat /tmp/test-args.txt | awk '{print $1}'); if [ "$TYPE" = "all" ] && [ -f package.json ]; then npm test || yarn test; fi`
!`TYPE=$(cat /tmp/test-args.txt | awk '{print $1}'); if [ "$TYPE" = "all" ] && [ -f pytest.ini ]; then pytest -v; fi`

### Unit Tests
!`TYPE=$(cat /tmp/test-args.txt | awk '{print $1}'); if [ "$TYPE" = "unit" ]; then echo "🔬 Running unit tests..."; fi`
!`TYPE=$(cat /tmp/test-args.txt | awk '{print $1}'); if [ "$TYPE" = "unit" ] && [ -f package.json ]; then npm run test:unit || jest --testPathPattern=unit; fi`
!`TYPE=$(cat /tmp/test-args.txt | awk '{print $1}'); if [ "$TYPE" = "unit" ] && [ -f pytest.ini ]; then pytest tests/unit -v || pytest -k "unit" -v; fi`

### Integration Tests
!`TYPE=$(cat /tmp/test-args.txt | awk '{print $1}'); if [ "$TYPE" = "integration" ]; then echo "🔗 Running integration tests..."; fi`
!`TYPE=$(cat /tmp/test-args.txt | awk '{print $1}'); if [ "$TYPE" = "integration" ] && [ -f package.json ]; then npm run test:integration || jest --testPathPattern=integration; fi`
!`TYPE=$(cat /tmp/test-args.txt | awk '{print $1}'); if [ "$TYPE" = "integration" ] && [ -f pytest.ini ]; then pytest tests/integration -v || pytest -k "integration" -v; fi`

### E2E Tests
!`TYPE=$(cat /tmp/test-args.txt | awk '{print $1}'); if [ "$TYPE" = "e2e" ]; then echo "🌐 Running e2e tests..."; fi`
!`TYPE=$(cat /tmp/test-args.txt | awk '{print $1}'); if [ "$TYPE" = "e2e" ] && [ -f package.json ]; then npm run test:e2e || npm run cypress || npm run playwright; fi`
!`TYPE=$(cat /tmp/test-args.txt | awk '{print $1}'); if [ "$TYPE" = "e2e" ] && [ -f pytest.ini ]; then pytest tests/e2e -v || pytest -k "e2e" -v; fi`

### Specific File/Module
!`ARGS=$(cat /tmp/test-args.txt); FILE=$(echo "$ARGS" | awk '{print $2}'); if [ ! -z "$FILE" ] && [ "$TYPE" != "all" ]; then echo "📄 Testing specific: $FILE"; fi`
!`ARGS=$(cat /tmp/test-args.txt); FILE=$(echo "$ARGS" | awk '{print $2}'); if [ ! -z "$FILE" ] && [ -f package.json ]; then jest "$FILE" || npm test -- "$FILE"; fi`
!`ARGS=$(cat /tmp/test-args.txt); FILE=$(echo "$ARGS" | awk '{print $2}'); if [ ! -z "$FILE" ] && [ -f pytest.ini ]; then pytest "$FILE" -v; fi`

## Coverage Report
!`[ -f package.json ] && [ -d coverage ] && echo "📊 Coverage report: $(cat coverage/coverage-summary.json 2>/dev/null | jq -r '.total.lines.pct' || echo 'Run with coverage flag')"`
!`[ -f .coverage ] && echo "📊 Coverage: $(coverage report --format=total 2>/dev/null || echo 'Run: coverage report')"`

## Test Results Summary
!`echo -e "\n📋 Test Summary:"`
!`[ -f package.json ] && grep -E "(passed|failed|skipped)" *.log 2>/dev/null | tail -3`
!`[ -f pytest.ini ] && grep -E "(passed|failed|skipped|warnings)" *.log 2>/dev/null | tail -3`

## Cleanup
!`rm -f /tmp/test-args.txt`

## Usage Examples
```
/project:test:run              # Run all tests
/project:test:run unit         # Run unit tests only
/project:test:run integration  # Run integration tests
/project:test:run e2e          # Run end-to-end tests
/project:test:run unit auth    # Run unit tests for auth module
```

## Next Steps
- `/project:pr:validate` - Validate PR readiness after tests
- `/project:test:coverage` - Generate detailed coverage report
- `/project:pr:create` - Create PR if tests pass