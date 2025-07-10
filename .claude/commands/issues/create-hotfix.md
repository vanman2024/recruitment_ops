---
allowed-tools: mcp__github-http__*, Write(*), Read(*), TodoWrite(*), Bash(*), Task(*), mcp__sequential-thinking-http__sequentialthinking
description: Create an urgent hotfix for critical production issues
---

# Create Hotfix Command

## Context Loading
- Current directory: !`pwd`
- Git status: !`git status --porcelain`
- Production status: !`curl -s https://api.devloop.ai/health || echo "API Down"`
- Recent deployments: !`git log --oneline --grep="deploy" -3`
- Active incidents: !`gh issue list --repo vanman2024/DevLoopAI --label "hotfix" --state open`
- Last stable version: !`git tag -l "v*" | sort -V | tail -1`

## Extended Thinking Trigger
Think through this URGENTLY:
1. Assess the production impact and affected users
2. Identify root cause if possible
3. Determine if rollback is viable
4. Plan immediate mitigation
5. Design minimal fix with lowest risk

## Your Task
Create an urgent hotfix issue and immediately begin resolution process.

### GitHub Configuration
- Owner: vanman2024
- Repo: DevLoopAI
- Fallback: gh CLI if MCP tool fails

### Requirements Analysis
Based on $ARGUMENTS:
- Issue Description: $ARGUMENTS[0]
- Impact Level: $ARGUMENTS[1] (System Down, Major Feature Broken, Data Risk, Security, Performance)
- Affected Module: $ARGUMENTS[2]

### EMERGENCY RESPONSE STEPS
1. **Impact Assessment**: Quantify affected users/systems
2. **Immediate Mitigation**: Apply workaround if possible
3. **Hotfix Issue Creation**: 
   - Primary: Create with mcp__github-http__create_issue (owner="vanman2024", repo="DevLoopAI")
   - Fallback: If MCP server fails, use GitHub CLI:
     ```bash
     gh issue create --repo vanman2024/DevLoopAI \
       --title "[HOTFIX]: {description}" \
       --body "{body}" \
       --label "hotfix,critical,production,incident,module:{module}"
     ```
4. **Fix Implementation**: Launch Task for immediate fix
5. **Emergency Deployment**: Fast-track to production

### Interactive Flow (QUICK MODE)
If not provided, rapidly ask:
1. What's broken in production? (describe urgently)
2. How many users affected?
3. Can we rollback safely?
4. What's the suspected cause?
5. Emergency contact?

### Hotfix Issue Template
```yaml
title: "[HOTFIX]: {description}"
body: |
  ⚠️ **PRODUCTION EMERGENCY** ⚠️
  
  ## Impact
  - **Severity**: {impact_level}
  - **Affected Users**: {user_count}
  - **Started**: {timestamp}
  - **Module**: {module}
  
  ## Issue Description
  {urgent_description}
  
  ## Error Evidence
  ```
  {error_logs}
  ```
  
  ## Immediate Actions Taken
  - [ ] Incident declared
  - [ ] Team notified
  - [ ] Workaround applied: {workaround}
  - [ ] Monitoring increased
  
  ## Root Cause
  {suspected_cause}
  
  ## Proposed Fix
  {fix_approach}
  
  ## Rollback Viable?
  {can_rollback}
  
  ## Emergency Contact
  {contact}
  
labels:
  - hotfix
  - critical
  - production
  - incident
  - module:{module}
```

### Automatic Emergency Response
Immediately after issue creation:

```bash
# 1. Create hotfix branch
git checkout -b hotfix/{issue_number}-{description}

# 2. Launch emergency fix task
Task(*) with prompt: "EMERGENCY FIX REQUIRED: {description}"

# 3. Notify team
gh issue comment --repo vanman2024/DevLoopAI {issue_number} --body "@team Production emergency declared. All hands on deck."

# 4. Start incident timeline
echo "[$(date)] - Incident started: {description}" > incident_{issue_number}.log
```

### Severity Actions
- **System Down**: Page on-call, status page update
- **Major Feature Broken**: Disable feature flag if possible
- **Data Risk**: Stop writes, backup immediately
- **Security**: Disable affected endpoints
- **Performance**: Scale resources, cache clear

### Success Criteria
- Issue created within 2 minutes
- Team notified immediately
- Fix task launched autonomously
- Workaround applied if possible
- Timeline tracking started
- No additional damage caused

### Error Handling
In emergency, if anything fails:
1. Don't waste time debugging tools
2. Create issue manually if needed
3. Focus on production stability
4. Document everything for post-mortem
5. Escalate to senior staff

### Example Usage
```bash
# Emergency hotfix
/create-hotfix "Authentication service returning 500" "System Down" "Backend API"

# Ultra-quick mode
/create-hotfix URGENT
```

### Post-Hotfix Checklist
After stabilization:
- [ ] Write post-mortem
- [ ] Update monitoring
- [ ] Add regression tests
- [ ] Document lessons learned
- [ ] Schedule proper fix

Remember: In production emergencies, speed and stability matter most. Fix it first, make it pretty later.