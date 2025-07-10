---
allowed-tools: Bash(gh:*), mcp__github-http__list_pull_requests
description: Monitor GitHub Actions workflow status and debug failures
---

## Claude Prompt:
```
I need to check GitHub Actions workflow status.
I'll monitor running workflows, check failures, and help debug issues.
```

## Your task

Monitor and debug GitHub Actions workflows:

1. **Check Workflow Status for Current Branch**:
   ```bash
   # List recent workflow runs
   gh run list --branch $(git branch --show-current) --limit 5
   
   # Show all workflows
   gh workflow list
   ```

2. **Monitor Active Workflows**:
   ```bash
   # Watch latest workflow run
   gh run watch
   
   # Watch specific workflow
   gh run watch [run-id]
   ```

3. **Check PR Status** (includes workflow checks):
   ```bash
   # View all checks for current PR
   gh pr checks
   
   # View detailed PR status
   gh pr view --web
   ```

4. **Debug Failed Workflows**:
   ```bash
   # View failed workflow logs
   gh run view --log-failed
   
   # View specific job logs
   gh run view [run-id] --log
   
   # Download artifacts from failed run
   gh run download [run-id]
   ```

5. **Common Workflow Failures and Fixes**:

   **Milestone Check Failed**:
   ```bash
   # PR validation requires milestone
   gh pr edit --milestone "MVP"
   ```

   **Test Failures**:
   ```bash
   # Run same tests locally
   cd /home/gotime2022/devloop3
   source venv/bin/activate
   python -m pytest test_suite/ -v
   ```

   **Format Check Failed**:
   ```bash
   # Check what format-check.yml runs
   cat .github/workflows/format-check.yml
   # Run formatter locally
   ```

6. **Re-run Failed Workflows**:
   ```bash
   # Re-run all jobs
   gh run rerun [run-id]
   
   # Re-run only failed jobs
   gh run rerun [run-id] --failed
   ```

## Understanding Workflow Files:
- **automated-pr-validation.yml**: Ensures PRs have milestones, runs tests
- **backend-tests.yml**: Runs pytest suite on push
- **devloopai-ci.yml**: Main CI/CD pipeline
- **format-check.yml**: Code style validation
- **pr-issue-link-checker.yml**: Ensures PRs link to issues
- **pr-labeler.yml**: Auto-labels PRs based on files changed

## Integration with MCP:
- Use `mcp__github-http__list_pull_requests` to get PR details
- Cross-reference with workflow status

## Quick Diagnosis:
```bash
# One command to see everything
gh pr checks && echo "---" && gh run list --limit 3
```

Remember: Fix issues LOCALLY first, then push to re-trigger workflows!