---
allowed-tools: Bash, TodoWrite, mcp__github__get_pull_request, mcp__github__update_pull_request, mcp__github__add_pr_comment, mcp__supabase-v3__update_data
description: Update existing PR with new changes and sync database
---

# 🔄 Update Pull Request

**Arguments**: $ARGUMENTS

## Parse PR Number
!`echo "$ARGUMENTS" | grep -oP '\d+' > /tmp/pr-num.txt`
!`PR=$(cat /tmp/pr-num.txt); echo "📝 Updating PR #$PR"`

## 1. Get Current PR Status

Use **mcp__github__get_pull_request**:
- owner: "vanman2024"
- repo: "DevLoopAI"
- pull_number: From /tmp/pr-num.txt

## 2. Check Local Changes

### New Commits
!`git log origin/$(git branch --show-current)..HEAD --oneline 2>/dev/null | head -10 || echo "No new commits"`

### Uncommitted Changes
!`git status --short`

## 3. Update Process

### Commit Any Changes
!`git add -A && git commit -m "feat: Updates based on PR feedback" || echo "No changes to commit"`

### Push Updates
!`git push origin $(git branch --show-current) || echo "Failed to push"`

## 4. Update PR Description

Use **mcp__github__update_pull_request** to update:
- title: (if needed)
- body: Add update notes
- state: Keep as "open"

## 5. Add Update Comment

Use **mcp__github__add_pr_comment** to add:
```
## 📝 PR Updated

### Changes in this update:
- [List what changed]
- [Why it changed]

### Testing:
- [ ] All tests still passing
- [ ] New tests added for changes
- [ ] Manual testing completed

Ready for re-review! 🚀
```

## 6. Update Database

Use **mcp__supabase-v3__update_data** to:
- Update task status if needed
- Record PR update activity
- Update last_modified timestamps

## 7. Update Todos

Use **TodoWrite** to track:
- [ ] Address remaining feedback
- [ ] Ensure tests pass
- [ ] Update documentation
- [ ] Request re-review

## Cleanup
!`rm -f /tmp/pr-num.txt`

## Next Steps
- `/project:test:run unit` - Quick test validation
- `/project:pr:complete` - When ready to merge
- `/project:pr:update` - If more changes needed