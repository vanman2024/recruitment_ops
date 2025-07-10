---
allowed-tools: TodoRead, TodoWrite, Bash(*), Read(*), mcp__github-http__list_issues, mcp__github-http__list_pull_requests, mcp__github-http__get_issue_timeline, mcp__github-http__list_issue_comments, mcp__github-http__list_commits, mcp__supabase-v3__select_data, mcp__supabase-v3__execute_sql, mcp__sequential-thinking-http__sequentialthinking, mcp__routing-http__session_continue, mcp__routing-http__get_agent_workload, mcp__memory-http__search_nodes, mcp__memory-http__read_graph, mcp__vercel-deploy-http__list_deployments, mcp__vercel-deploy-http__get_deployment_status, mcp__vercel-deploy-http__list_domains
description: Advanced development progress analyzer with deployment health monitoring
---

@/home/gotime2022/devloop3/.claude/docs/WORKFLOW_SEQUENCES.md
@/home/gotime2022/devloop3/.claude/docs/WORKFLOW_EXECUTION_GUIDE.md

## Context

### Git & Branch Status
- Current branch: !`git branch --show-current`
- Branch ahead/behind: !`git status -sb | head -1`
- Working tree status: !`git status --porcelain | wc -l` files changed
- Stash count: !`git stash list | wc -l` stashes

### Recent Activity
- Last 10 commits: !`git log --oneline --graph -10`
- Files changed today: !`find . -name "*.py" -o -name "*.ts" -o -name "*.tsx" | xargs ls -lt 2>/dev/null | grep "$(date +%b' '%e)" | wc -l`
- Active processes: !`ps aux | grep -E "(python|node|npm)" | grep -v grep | wc -l`

### GitHub Status
- Repository: !`gh repo view --json nameWithOwner -q .nameWithOwner 2>/dev/null || echo "vanman2024/DevLoopAI"`
- Open PRs: !`gh pr list --state open --limit 3 --json number,title,state,isDraft | jq -r '.[] | "\(.number): \(.title) [\(.state)\(if .isDraft then " DRAFT" else "" end)]"' 2>/dev/null || echo "No PRs"`
- Assigned issues: !`gh issue list --assignee @me --state open --limit 3 --json number,title,labels | jq -r '.[] | "\(.number): \(.title) [\(.labels[].name // "no-labels" | @csv)]"' 2>/dev/null || echo "No assigned issues"`

### Project Health
- Test status: !`[ -f pytest.ini ] && echo "pytest configured" || echo "No pytest config"`
- Lint status: !`[ -f .flake8 ] || [ -f .pylintrc ] && echo "Linting configured" || echo "No lint config"`
- CI/CD status: !`[ -d .github/workflows ] && ls .github/workflows/*.yml | wc -l` workflow files

## Your Task: Comprehensive Progress Analysis

### 1. Session History Analysis
```bash
# Find and analyze previous todo sessions
echo "=== TODO SESSION HISTORY ==="
for f in $(ls -t /home/gotime2022/.claude/todos/*.json 2>/dev/null | head -10); do 
  if [ -f "$f" ]; then
    size=$(wc -c < "$f")
    if [ $size -gt 50 ]; then 
      echo -e "\n📋 Session: $(basename $f)"
      echo "Size: $size bytes | Modified: $(stat -c %y "$f" 2>/dev/null | cut -d' ' -f1,2)"
      # Extract key info
      jq -r 'if .todos then "Todos: " + (.todos | length | tostring) + " items" elif .session_ended then "Session ended: " + .session_ended else . end' "$f" 2>/dev/null | head -3
    fi
  fi
done

# Check for session continuations
if [ -d /home/gotime2022/.claude/continuations ]; then
  echo -e "\n=== SESSION CONTINUATIONS ==="
  ls -lt /home/gotime2022/.claude/continuations/*.json 2>/dev/null | head -5
fi
```

### 2. GitHub Integration Analysis
Use MCP to get comprehensive GitHub status:
- List current milestone issues and progress
- Check PR review status and comments
- Analyze issue dependencies and blockers
- Track commit frequency and patterns

### 3. Database Task Tracking (Supabase)
Query the tasks table for:
- Tasks in current sprint/module
- Task completion rates
- Blocked tasks and dependencies
- Time estimates vs actual

Example query:
```sql
SELECT 
  t.id, t.title, t.status, t.priority,
  m.name as module, 
  COUNT(st.id) as subtask_count,
  SUM(CASE WHEN st.status = 'completed' THEN 1 ELSE 0 END) as completed_subtasks
FROM tasks t
LEFT JOIN modules m ON t.module_id = m.id
LEFT JOIN subtasks st ON t.id = st.task_id
WHERE t.status != 'completed'
GROUP BY t.id, t.title, t.status, t.priority, m.name
ORDER BY t.priority DESC, t.created_at ASC
LIMIT 10;
```

### 4. Intelligent Progress Metrics
Calculate and display:
- **Velocity**: Commits per day, tasks completed per sprint
- **Quality**: Test coverage trends, lint issues over time
- **Blockers**: Identify patterns in blocked work
- **Focus**: Time spent on different types of tasks

### 5. Memory Graph Analysis
Use memory MCP to track:
- Key decisions made during development
- Technical debt observations
- Recurring issues or patterns
- Team knowledge gaps

### 6. Multi-Agent Workload Status
Check routing MCP for:
- Active agent sessions
- Pending handoffs
- Resource utilization
- Queue depths

### 7. Advanced Todo Management
Beyond simple todo tracking:
- Categorize todos by type (bug, feature, refactor, docs)
- Estimate completion time based on similar past tasks
- Identify todo dependencies and optimal order
- Flag todos that may be outdated or irrelevant

### 8. Deployment Health Check
Use Vercel MCP to monitor production status:
- **Latest Deployment**: Check if production is running latest master commit
- **Health Status**: Verify deployment is READY and accessible
- **Domain Status**: Ensure custom domains are properly configured
- **Error Rate**: Check deployment logs for recent errors
- **Performance**: Monitor response times from deployment

Example checks:
```python
# Get latest production deployment
deployments = mcp__vercel-deploy-http__list_deployments(
    limit=5,
    target="production"
)

# Check if healthy
if deployments and deployments[0]["state"] == "READY":
    # Get detailed status
    status = mcp__vercel-deploy-http__get_deployment_status(
        deployment_id=deployments[0]["id"]
    )
    # Check for errors in logs if needed
```

### 9. Predictive Analysis
Use sequential thinking to:
- Predict potential blockers based on current state
- Suggest optimal next actions
- Identify risks in current approach
- Recommend resource allocation
- Flag deployment issues before they impact users

### 10. Generate Executive Summary
Create a structured report with:
```markdown
# Development Progress Report - [Date]

## 🎯 Current Sprint/Milestone
- Name: [milestone]
- Progress: [X/Y tasks] ([percentage]%)
- Est. Completion: [date]

## 📊 Key Metrics
- Velocity: [commits/day, tasks/week]
- Code Quality: [test coverage]%, [lint score]
- Team Load: [active PRs], [open issues]

## ✅ Completed (Last 24-48h)
- [List key completions with impact]

## 🚧 In Progress
- [Current focus with % complete]
- [Blockers and mitigation]

## 📋 Upcoming Priority
1. [Next critical task]
2. [Dependencies to resolve]
3. [Technical debt items]

## 🚨 Risks & Blockers
- [Issue with severity and impact]
- [Proposed solutions]

## 💡 Recommendations
- [Data-driven suggestions]
- [Process improvements]
- [Resource needs]

## 📈 Trend Analysis
- [Velocity trend: improving/declining]
- [Quality trend: test coverage changes]
- [Cycle time: PR merge times]
```

### 10. Actionable Next Steps
Based on analysis, automatically:
- Update todo priorities
- Create new todos for discovered work
- Suggest PR reviews needed
- Recommend focus areas
- Flag items needing escalation

### Implementation Instructions
1. Use sequential thinking for complex analysis
2. Batch MCP calls for efficiency
3. Cache results for quick re-runs
4. Provide visual indicators (emoji) for quick scanning
5. Keep summary under 50 lines for readability
6. Always end with 3-5 concrete next actions

Remember: This is not just status checking - it's intelligent project analysis that drives decisions and improves velocity.