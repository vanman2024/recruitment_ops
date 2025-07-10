---
allowed-tools: Bash, TodoWrite, TodoRead, mcp__github__get_issue, mcp__github__create_pull_request, mcp__supabase-v3__execute_sql, mcp__supabase-v3__update_data
description: Run complete autonomous workflow from issue to PR
---

# 🤖 Autonomous Workflow Completion

**Arguments**: $ARGUMENTS

## Parse Input
!`echo "$ARGUMENTS" | grep -oP '\d+' > /tmp/issue.txt || echo "$ARGUMENTS" > /tmp/issue.txt`
!`ISSUE=$(cat /tmp/issue.txt); echo "🚀 Continuing workflow for: $ISSUE"`

## Check What Already Exists
!`echo "🔍 Checking existing work..."`

### Recent Plans
!`ls -la .claude/plans/*$ARGUMENTS*.md 2>/dev/null | tail -3 || echo "No saved plans"`

### Existing Issues  
!`gh issue list --repo vanman2024/DevLoopAI --search "$ARGUMENTS" --json number,title,state | jq -r '.[] | "#\(.number): \(.title) [\(.state)]"'`

### Existing Components
!`find frontend/dashboard/src/components -name "*.tsx" -o -name "*.jsx" 2>/dev/null | grep -E "(Login|Auth|Dashboard|Settings)" | head -10 || echo "Check component directory"`

## 1. Get Issue Context

Use **mcp__github__get_issue**:
- owner: "vanman2024"  
- repo: "DevLoopAI"
- issue_number: From /tmp/issue.txt

## 2. Check Existing Work

Use **mcp__supabase-v3__execute_sql** with project_id "dkpwdljgnysqzjufjtnk":
```sql
SELECT t.id, t.name, t.status, t.assigned_specialist
FROM tasks t
WHERE t.github_issue_number = $1
LIMIT 5;
```

## 3. Development Setup

### Create Branch
!`ISSUE=$(cat /tmp/issue.txt); git checkout -b feature/issue-$ISSUE-$(date +%Y%m%d) || echo "Branch may already exist"`

### Initial Todos
Use **TodoWrite** to create:
- [ ] Analyze requirements
- [ ] Implement solution
- [ ] Add tests
- [ ] Update documentation
- [ ] Create PR

## 4. Implementation

**Think deeply** about the issue and implement:
1. Make necessary code changes
2. Follow coding standards
3. Add comprehensive tests
4. Update relevant documentation

## 5. Testing

!`echo "🧪 Running tests..."`
!`[ -f package.json ] && npm test || [ -f pytest.ini ] && pytest -v || echo "⚠️ No test runner found"`

## 6. Commit Changes

!`git add -A && git commit -m "fix: Implement solution for issue #$(cat /tmp/issue.txt)" || echo "No changes to commit"`

## 7. Create Pull Request

### Push Branch
!`git push -u origin $(git branch --show-current) || echo "Failed to push"`

### Create PR
Use **mcp__github__create_pull_request**:
- owner: "vanman2024"
- repo: "DevLoopAI"
- title: "Fix: Issue #$ISSUE"
- head: Current branch
- base: "main"
- body: "Closes #$ISSUE\n\nImplemented solution as discussed in the issue."

## 8. Update Database

Use **mcp__supabase-v3__update_data** to mark tasks as complete

## Cleanup
!`rm -f /tmp/issue.txt`

## Next Steps
- Monitor PR for review feedback
- `/project:pr:complete` - Handle PR review process
- `/project:deploy:ops` - Deploy after merge