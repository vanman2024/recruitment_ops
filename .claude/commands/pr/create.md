---
allowed-tools: Bash, TodoWrite, mcp__github__create_pull_request, mcp__supabase-v3__update_data
description: Create a pull request with proper local/remote handling and Synapse workflow
---

@/home/gotime2022/devloop3/.claude/docs/WORKFLOW_SEQUENCES.md

## Context
- Current LOCAL branch: !`git branch --show-current`
- LOCAL changes: !`git status --short`
- Commits ahead of remote: !`git log origin/$(git branch --show-current)..HEAD --oneline 2>/dev/null || echo "No remote branch yet"`

## Claude Prompt:
```
I'm creating a PR following the Synapse workflow.
I will:
1. Ensure all LOCAL changes are committed
2. Push LOCAL branch to REMOTE
3. Create PR with proper linking
4. Update database task status
```

## Your task

Create PR for current branch:

1. **Commit any remaining LOCAL changes**:
   ```bash
   # Check for uncommitted changes
   git status --short
   
   # If changes exist, commit them
   git add .
   git commit -m "Final changes for PR"
   ```

2. **Push LOCAL branch to REMOTE**:
   ```bash
   # First push (creates REMOTE branch)
   git push -u origin $(git branch --show-current)
   
   # Or if already tracking
   git push
   ```

3. **Verify LOCAL and REMOTE are in sync**:
   ```bash
   # Should show "Your branch is up to date"
   git status
   
   # Verify remote branch exists
   git ls-remote --heads origin $(git branch --show-current)
   ```

4. **Create PR using GitHub CLI**:
   ```bash
   # Extract issue number from branch name
   ISSUE=$(git branch --show-current | grep -oE '[0-9]+' | head -1)
   
   gh pr create \
     --title "Fix #$ISSUE: [descriptive title]" \
     --body "Closes #$ISSUE

## Summary
[What this PR does]

## Testing Completed
- [ ] All automated tests pass
- [ ] Manual testing completed
- [ ] No regression issues found

## Changes Made
- [List key changes]

🤖 Generated with Claude Code" \
     --base master
   ```

5. **Alternative: Use MCP to create PR**:
   ```python
   # Use mcp__github-http__create_pull_request
   # head: current branch name
   # base: "master"
   # title: "Fix #X: Description"
   # body: Include test results
   ```

6. **Update database task**:
   - Use `mcp__supabase-v3__update_data`
   - Set pr_number, pr_status = "open"

## Important Notes:
- LOCAL branch must be pushed to REMOTE before PR
- PR links LOCAL's REMOTE version to base branch
- Always include test results in PR body
- PR should reference the issue it closes

## What Happens After PR Creation:

**GitHub Actions will automatically:**
1. Run `automated-pr-validation.yml` - Checks milestone
2. Run `pr-issue-link-checker.yml` - Verifies issue link
3. Run `pr-labeler.yml` - Adds labels
4. Run `backend-tests.yml` - Executes test suite
5. Run `format-check.yml` - Validates code style

**Monitor with:**
```bash
gh pr checks  # Watch status
gh pr view --web  # View in browser
```

## Post-PR checklist:
- [ ] LOCAL branch pushed to REMOTE
- [ ] PR created and links to issue
- [ ] Milestone assigned (REQUIRED)
- [ ] Waiting for GitHub Actions to complete
- [ ] Ready to monitor workflow status