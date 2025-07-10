---
allowed-tools: Bash, TodoWrite, mcp__github__list_issues, mcp__supabase-v3__execute_sql
description: Guided workflow that tells you exactly which commands to run next
---

# 🎯 Guided Feature Development

**Arguments**: $ARGUMENTS

## Workflow Status Check

### Check Current State
!`echo "$ARGUMENTS" > /tmp/feature.txt`
!`git branch --show-current | grep -q "feature" && echo "✅ On feature branch" || echo "❌ Not on feature branch"`

### Check for Issue
!`FEATURE=$(cat /tmp/feature.txt); gh issue list --search "$FEATURE" --json number,state | jq -r '.[] | "Issue #\(.number): \(.state)"' || echo "No issue found"`

### Check Database Tasks
Use **mcp__supabase-v3__execute_sql** with project_id "dkpwdljgnysqzjufjtnk":
```sql
SELECT COUNT(*) as total, 
       COUNT(CASE WHEN status = 'completed' THEN 1 END) as done
FROM tasks 
WHERE name ILIKE '%$ARGUMENTS%';
```

## 🚦 Workflow Decision Tree

Based on the checks above, here's your next command:

### If NO Issue Exists:
```bash
👉 NEXT: /project:issue:create "$ARGUMENTS"
```

### If Issue Exists but NO Branch:
```bash
👉 NEXT: /project:dev:start [issue_number]
```

### If Development Started (0-30% complete):
```bash
👉 NEXT: Continue coding, then run:
         /project:dev:progress
```

### If Development Progress (30-80% complete):
```bash
👉 NEXT: /project:test:run unit
         Then: /project:dev:progress
```

### If Near Complete (80-95% complete):
```bash
👉 NEXT: /project:test:complete
         Then: /project:pr:create
```

### If PR Exists:
```bash
👉 NEXT: /project:pr:update [pr_number]
         Or: /project:pr:complete
```

### If All Complete:
```bash
✅ Feature complete! Consider:
   /project:deploy:ops
   /project:issue:update [issue_number]
```

## 📋 Complete Command Sequence

Use **TodoWrite** to create this checklist:
- [ ] `/project:issue:create "$ARGUMENTS"`
- [ ] `/project:issue:analyze [number]`
- [ ] `/project:dev:start [number]`
- [ ] `/project:test:run unit` (iterative)
- [ ] `/project:test:complete`
- [ ] `/project:pr:create`
- [ ] `/project:pr:complete`
- [ ] `/project:issue:update [number]`

## 🎯 Smart Tips

1. **Copy the next command** from above
2. **Run it immediately** after this completes
3. **Return here** with `/project:workflow:guided-feature "$ARGUMENTS"` to get next step

!`rm -f /tmp/feature.txt`