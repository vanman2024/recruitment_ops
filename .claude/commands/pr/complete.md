---
allowed-tools: Bash(git:*), Bash(gh:*), TodoWrite, mcp__github-http__create_pull_request, mcp__github-http__add_issue_comment, mcp__supabase-v3__update_data
description: Complete PR flow - test, commit, push, create PR with all validations
---

## Context
- Current branch: !`git branch --show-current`
- Changes: !`git diff --stat`
- Issue from branch: !`echo $(git branch --show-current) | grep -oE '[0-9]+' | head -1`
- Test results: @test-results.log (if exists)

## Your task

Complete the entire PR creation flow with proper order of operations:

### 1. Pre-flight Checks
```bash
# Ensure we're not on master
if [ "$(git branch --show-current)" = "master" ]; then
    echo "ERROR: Cannot create PR from master branch!"
    exit 1
fi

# Check for uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
    echo "Uncommitted changes found. Committing..."
    git add .
    git commit -m "Final changes before PR"
fi
```

### 2. Run Complete Test Suite
First, let's ensure all tests pass:
```bash
# This would normally call /test-complete
python -m pytest test_suite/ -v --tb=short > test-results.log
```

### 3. Push to Remote
```bash
# Push local branch to remote with tracking
git push -u origin $(git branch --show-current)
```

### 4. Create PR with Validations
Extract issue number and create PR:
```bash
ISSUE=$(git branch --show-current | grep -oE '[0-9]+' | head -1)
BRANCH=$(git branch --show-current)
```

Use `mcp__github-http__create_pull_request` with:
- title: "Fix #${ISSUE}: [Description]"
- body: Include test results and checklist
- base: "master"
- head: current branch

### 5. Update Database
Use `mcp__supabase-v3__update_data` to update task:
- pr_number: from PR creation response
- pr_status: "open"
- pr_created_at: current timestamp

### 6. Add Test Results to Issue
Use `mcp__github-http__add_issue_comment` to add:
```markdown
## 🚀 PR Created: #[PR_NUMBER]

### Test Results:
- ✅ All tests passing
- 📊 Coverage: XX%
- 🔍 No security issues found

### Next Steps:
- Waiting for code review
- GitHub Actions running
```

### 7. Monitor GitHub Actions
```bash
echo "PR created! Monitor status with:"
echo "  gh pr checks"
echo "  gh pr view --web"
```

### Success Criteria:
- [ ] All tests pass locally
- [ ] Branch pushed to remote
- [ ] PR created with proper title/body
- [ ] PR links to issue
- [ ] Database updated
- [ ] Issue commented
- [ ] GitHub Actions triggered

This command chains the complete PR workflow!