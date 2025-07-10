---
allowed-tools: Bash, Read, Write, Edit, Grep, Glob, LS, TodoWrite, TodoRead, mcp__github__list_issues, mcp__github__list_pull_requests, mcp__github__get_issue, mcp__supabase-v3__execute_sql, mcp__vercel-v0__list_generated_components, mcp__docker__list_containers
description: Ultra-comprehensive context restoration with extended thinking and full MCP integration
---

# 🚀 Ultra Context Restoration

**Arguments**: $ARGUMENTS

## Parse Focus Area
!`echo "$ARGUMENTS" > /tmp/focus.txt`
!`FOCUS=$(cat /tmp/focus.txt); echo "🎯 Analyzing: $FOCUS"`

## 1. System Health Check

### Environment Status
!`[ -f .env ] && echo "✅ Environment configured" || echo "❌ Missing .env"`
!`[ -d .venv ] && echo "✅ Virtual environment present" || echo "❌ Missing venv"`
!`[ -d mcp-servers ] && echo "✅ MCP servers directory found" || echo "❌ Missing MCP servers"`

### Git Status
!`echo "📍 Current branch: $(git branch --show-current)"`
!`git status --short | head -10 || echo "Clean working directory"`

### MCP Servers Running
!`ps aux | grep -E "python.*mcp.*server" | grep -v grep | wc -l | xargs -I {} echo "🖥️ {} MCP servers running"`

## 2. Previous Session Recovery

### Find Recent Todos
!`ls -t /home/gotime2022/.claude/todos/*.json 2>/dev/null | head -3 > /tmp/recent-todos.txt`
!`[ -s /tmp/recent-todos.txt ] && echo "📋 Found previous todos:" || echo "📋 No previous todos found"`

### Read Each Todo File
!`cat /tmp/recent-todos.txt | while read f; do echo "=== $f ==="; cat "$f" | jq -r '.[] | "[\(.status)] \(.content)"' 2>/dev/null || cat "$f"; done`

## 3. Project Documentation Context

Core documentation files:
- Project setup: @CLAUDE.md
- Workflow guide: @docs/workflows/COMPREHENSIVE_DEVLOOP_WORKFLOW.md
- Database guide: @backend/scripts/database/docs/DATABASE_MASTER_GUIDE.md
- MCP analysis: @docs/analysis/MCP_SERVER_ANALYSIS_COMPREHENSIVE.md

## 4. GitHub Status

### Active Issues
Use **mcp__github__list_issues** with:
- owner: "vanman2024"
- repo: "DevLoopAI"
- state: "open"
- sort: "updated"
- direction: "desc"
- per_page: 10

### Active Pull Requests
Use **mcp__github__list_pull_requests** with:
- owner: "vanman2024"
- repo: "DevLoopAI"
- state: "open"
- sort: "updated"
- direction: "desc"
- per_page: 10

### Recent Activity
!`gh issue list --repo vanman2024/DevLoopAI --state open --limit 5 --json number,title,assignees,labels | jq -r '.[] | "#\(.number): \(.title) [\(.labels[].name // "no-label")]"' || echo "Unable to fetch issues"`

## 5. Database Analysis

Use **mcp__supabase-v3__execute_sql** with project_id "dkpwdljgnysqzjufjtnk":

```sql
-- Project overview
SELECT 
  p.name, p.status,
  COUNT(DISTINCT m.id) as milestones,
  COUNT(DISTINCT t.id) as tasks,
  COUNT(DISTINCT CASE WHEN t.status = 'in_progress' THEN t.id END) as active_tasks,
  ROUND(COUNT(DISTINCT CASE WHEN t.status = 'completed' THEN t.id END)::numeric / 
        NULLIF(COUNT(DISTINCT t.id), 0) * 100, 2) as completion_pct
FROM projects p
LEFT JOIN milestones m ON p.id = m.project_id
LEFT JOIN phases ph ON m.id = ph.milestone_id
LEFT JOIN modules mo ON ph.id = mo.phase_id
LEFT JOIN tasks t ON mo.id = t.module_id
WHERE p.name IN ('DevLoopAI', 'SynapseAI')
GROUP BY p.id, p.name, p.status;
```

## 6. Focus-Specific Analysis

### Check Focus Area
!`FOCUS=$(cat /tmp/focus.txt); if echo "$FOCUS" | grep -qi "frontend"; then echo "🎨 Frontend focus detected"; fi`
!`FOCUS=$(cat /tmp/focus.txt); if echo "$FOCUS" | grep -qi "backend"; then echo "⚙️ Backend focus detected"; fi`
!`FOCUS=$(cat /tmp/focus.txt); if echo "$FOCUS" | grep -qi "mcp"; then echo "🔧 MCP focus detected"; fi`
!`FOCUS=$(cat /tmp/focus.txt); if echo "$FOCUS" | grep -qi "issue"; then echo "🐛 Issue focus detected"; fi`

### Frontend Specific (if applicable)
!`FOCUS=$(cat /tmp/focus.txt); if echo "$FOCUS" | grep -qi "frontend"; then git log --oneline -10 -- frontend/ 2>/dev/null | head -5 || echo "No recent frontend changes"; fi`

### Backend Specific (if applicable)
!`FOCUS=$(cat /tmp/focus.txt); if echo "$FOCUS" | grep -qi "backend"; then git log --oneline -10 -- backend/ 2>/dev/null | head -5 || echo "No recent backend changes"; fi`

### Issue Specific (if applicable)
!`FOCUS=$(cat /tmp/focus.txt); ISSUE_NUM=$(echo "$FOCUS" | grep -oP '\d+' || echo ""); if [ ! -z "$ISSUE_NUM" ]; then echo "🔍 Searching for issue #$ISSUE_NUM references"; fi`

## 7. Extended Thinking Phase

**Think deeply** about the system state based on all gathered information:

### Architecture Analysis
- Backend core: @backend/unified_backend.py
- Frontend dashboard: @frontend/dashboard/pages/index.tsx
- Testing patterns: @test_suite/docs/STANDARD_TESTING_CHECKLIST.md

**Think harder** about:
1. What was the last work in progress?
2. Are there any blocking issues?
3. What's the critical path for current development?
4. How can MCP tools accelerate the work?

### Priority Assessment
**Think more deeply** about what needs immediate attention based on:
- Active GitHub issues and PRs
- In-progress database tasks
- Recent commit patterns
- System health indicators

## 8. Action Planning

**Think deeply** about all gathered information and create comprehensive todos.

Use **TodoWrite** to create a prioritized task list that includes:

### From GitHub Data
- High-priority open issues that need attention
- PRs that need review or updates
- Issues without assignees that match current work

### From Database Analysis
- In-progress tasks that need completion
- Blocked tasks that can be unblocked
- Tasks assigned to current specialist

### From Previous Todos
- Incomplete items from previous sessions
- Follow-up tasks identified
- Deferred work that's now relevant

### System Health Items
- Any failing tests or builds
- Configuration issues found
- Performance problems detected

Organize todos by:
1. **🚨 Critical** - Blockers and broken functionality
2. **📌 Current Sprint** - Active development work
3. **🎯 Quick Wins** - < 1 hour tasks for momentum
4. **📋 Backlog** - Important but not urgent

## 9. Output Summary

Provide a structured report with:
- 🏥 **System Health**: Overall status and any issues
- 🎯 **Current Focus**: Active work and priorities
- 🚧 **Blockers**: What's preventing progress
- ✅ **Next Actions**: Immediate steps to take
- 💾 **Session Continuity**: How to resume work

## Cleanup
!`rm -f /tmp/focus.txt /tmp/recent-todos.txt 2>/dev/null`

## Next Commands

Based on findings, chain to appropriate commands:
- `/project:context:big-picture` - Understand the larger vision
- `/project:issue:analyze [number]` - Deep dive into specific issue
- `/project:dev:start [issue]` - Begin development work
- `/project:test:run all` - Run test suite
- `/project:pr:create` - Create pull request

Remember: This command connects you to **current work in progress**. For the bigger picture of what we're building, use `/project:context:big-picture`.