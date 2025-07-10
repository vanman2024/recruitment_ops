---
allowed-tools: Bash, mcp__github__list_issues, mcp__github__list_pull_requests, mcp__supabase-v3__execute_sql, TodoWrite
description: Show current workflow status and next commands to run
---

# 📊 Workflow Status & Next Steps

**Arguments**: $ARGUMENTS

## Current Work Analysis

### Active Issues
Use **mcp__github__list_issues**:
- owner: "vanman2024"
- repo: "DevLoopAI"
- state: "open"
- assignee: "@me"

### Active PRs
Use **mcp__github__list_pull_requests**:
- owner: "vanman2024"
- repo: "DevLoopAI"
- state: "open"
- author: "@me"

### Database Task Status
Use **mcp__supabase-v3__execute_sql** with project_id "dkpwdljgnysqzjufjtnk":
```sql
-- Get workflow status
WITH task_status AS (
  SELECT 
    t.github_issue_number,
    t.name,
    t.status,
    COUNT(*) OVER (PARTITION BY t.github_issue_number) as total_tasks,
    COUNT(CASE WHEN t.status = 'completed' THEN 1 END) 
      OVER (PARTITION BY t.github_issue_number) as completed_tasks
  FROM tasks t
  WHERE t.status != 'completed'
    AND t.assigned_specialist IS NOT NULL
  ORDER BY t.updated_at DESC
  LIMIT 10
)
SELECT DISTINCT
  github_issue_number,
  ROUND(completed_tasks::numeric / total_tasks * 100, 0) as completion_pct,
  total_tasks - completed_tasks as remaining_tasks
FROM task_status;
```

## 🎯 Recommended Next Commands

Based on the analysis above:

### For Issues Without PRs (In Development)
```bash
# Check progress:
/project:dev:progress

# Run tests:
/project:test:run unit

# When ready:
/project:pr:create
```

### For Issues With PRs (In Review)
```bash
# Update PR:
/project:pr:update [pr_number]

# Complete PR:
/project:pr:complete
```

### For Stale Issues (No recent activity)
```bash
# Update status:
/project:issue:update [issue_number]

# Or close:
/project:issue:close [issue_number]
```

### For New Work
```bash
# Start fresh:
/project:context:restore

# Create new feature:
/project:issue:create "Feature name"
```

## 📋 Workflow Checklist

Use **TodoWrite** to track where you are in each workflow:
- Issues in development
- PRs awaiting review  
- Blocked tasks
- Next features to start

## 🔄 Command Sequences

### Quick Progress Check:
```bash
/project:workflow:status
/project:dev:progress  
/project:test:run unit
```

### PR Flow:
```bash
/project:workflow:status
/project:pr:update [number]
/project:pr:complete
```

### New Feature:
```bash
/project:workflow:status
/project:context:big-picture
/project:issue:create "Feature"
```

💡 **Pro Tip**: Bookmark this command! Run it between tasks to always know your next step.