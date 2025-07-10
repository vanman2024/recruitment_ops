---
allowed-tools: mcp__github-http__*, Write(*), Read(*), TodoWrite(*), mcp__sequential-thinking-http__sequentialthinking, Bash(*), Grep(*), Task(*)
description: Report a bug with automatic task creation in the DevLoop hierarchy
---

# Create Bug Report Command

## Context Loading
- Current directory: !`pwd`
- Git status: !`git status --porcelain`
- Recent logs: !`tail -50 logs/error.log 2>/dev/null || echo "No error logs"`
- System status: !`ps aux | grep -E "node|python|java" | grep -v grep | wc -l`
- Issue template: @.github/ISSUE_TEMPLATE/bug_report.yaml
- Recent deployments: !`git log --oneline --grep="deploy" -5`

## Extended Thinking Trigger
Thinkhard about this step by step:
1. Analyze the bug report and its severity
2. Identify which module and component is affected
3. Determine if this is a regression
4. Consider the production impact
5. Plan immediate mitigation and long-term fix

## Your Task
Create a bug report that will automatically generate a fix task in the appropriate module.

### GitHub Configuration
- Owner: vanman2024
- Repo: DevLoopAI
- Fallback: gh CLI if MCP tool fails

### Requirements Analysis
Based on $ARGUMENTS:
- Bug Description: $ARGUMENTS[0]
- Affected Module: $ARGUMENTS[1] 
- Severity: $ARGUMENTS[2] (Critical, High, Medium, Low)
- Environment: $ARGUMENTS[3] (Production, Preview, Local)

### Implementation Steps
1. **Impact Assessment**: Determine severity and affected users
2. **Root Cause Analysis**: Use Grep/Read to investigate
3. **Bug Report Creation**: 
   - Primary: Create issue using mcp__github-http__create_issue with owner="vanman2024" and repo="DevLoopAI"
   - Fallback: If MCP server fails, use GitHub CLI:
     ```bash
     gh issue create --repo vanman2024/DevLoopAI \
       --title "[Bug]: {description}" \
       --body "{body}" \
       --label "bug,severity:{severity},module:{module}"
     ```
4. **Fix Task Generation**: Auto-create task for the fix
5. **Workaround Documentation**: If applicable

### Interactive Flow
If arguments not provided, ask user:
1. What's the bug? (describe the issue)
2. What were you trying to do? (steps to reproduce)
3. What happened instead? (actual behavior)
4. Which module/component is affected?
5. How severe is this? (Critical/High/Medium/Low)
6. Which environment? (Production/Preview/Local)
7. Any error messages or logs?
8. Is there a workaround?

### Bug Report Template
```yaml
title: "[Bug]: {description}"
body: |
  ## Bug Description
  {detailed_description}
  
  ## Affected Area
  - **Project**: {project}
  - **Module**: {module}
  - **Severity**: {severity}
  - **Environment**: {environment}
  
  ## Steps to Reproduce
  1. {step_1}
  2. {step_2}
  3. {step_3}
  
  ## Expected Behavior
  {expected}
  
  ## Actual Behavior
  {actual}
  
  ## Error Logs
  ```
  {error_logs}
  ```
  
  ## Workaround
  {workaround_if_any}
  
  ## Root Cause (if known)
  {suspected_cause}
  
  ## Fix Task
  This bug report will create a fix task with priority: {priority}
  
labels:
  - bug
  - severity:{severity}
  - module:{module}
  - milestone:{milestone}
  - phase:{phase}
  - environment:{environment}
  - needs-fix
```

### Severity Guidelines
- **Critical**: System down, data loss, security breach
- **High**: Major feature broken, affecting many users
- **Medium**: Feature partially broken, has workaround
- **Low**: Minor issue, cosmetic, edge case

### Auto Task Creation
After bug report, automatically create fix task:
```yaml
title: "[Task]: Fix - {bug_description}"
priority: {based_on_severity}
specialist: {module_specialist}
estimated_hours: {based_on_complexity}
```

### Success Criteria
- Bug report captures all necessary info
- Severity accurately assessed
- Steps to reproduce are clear
- Fix task automatically created
- Workaround documented if available
- Related to correct module in hierarchy

### Error Handling
If any step fails:
1. Use extended thinking to analyze the failure
2. Check for similar bugs: !`gh issue list --label "bug" --search "{keywords}"`
3. Gather more logs: !`docker logs {container} --tail 100`
4. Validate module exists in hierarchy
5. Update TodoWrite with current status

### Example Usage
```bash
# Report bug with details
/create-bug "Login fails with 500 error" "Authentication" "Critical" "Production"

# Interactive mode
/create-bug
```

Remember: Good bug reports lead to fast fixes. Include all context needed for a Claude instance to autonomously fix the issue.