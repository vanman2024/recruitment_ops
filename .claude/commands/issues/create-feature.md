---
allowed-tools: mcp__github-http__*, Write(*), Read(*), TodoWrite(*), mcp__sequential-thinking-http__sequentialthinking, Task(*)
description: Create a feature request issue following DevLoop hierarchy (Project → Milestone → Phase → Module → Task)
---

# Create Feature Request Command

## Context Loading
- Current directory: !`pwd`
- Git status: !`git status --porcelain`
- Current branch: !`git branch --show-current`
- Recent commits: !`git log --oneline -5`
- Issue template: @.github/ISSUE_TEMPLATE/feature_request.yaml
- Database hierarchy: @/home/gotime2022/devloop3/backend/HIERARCHY_UPDATE_SUMMARY.md

## Extended Thinking Trigger
Thinkhard about this step by step:
1. Analyze the feature request requirements from $ARGUMENTS
2. Understand how it fits in the DevLoop hierarchy
3. Determine which project, milestone, phase, and module it belongs to
4. Consider dependencies and implementation approach
5. Plan how this feature creates user-facing outcomes

## Your Task
Create a feature request issue in the appropriate repository following the DevLoop hierarchy.

### GitHub Configuration
- Owner: vanman2024
- Repo: DevLoopAI
- Fallback: gh CLI if MCP tool fails

### Requirements Analysis
Based on $ARGUMENTS:
- Feature Description: $ARGUMENTS[0]
- Project: $ARGUMENTS[1] (default: DevLoopAI)
- Milestone: $ARGUMENTS[2] (default: MVP Launch)
- Priority: $ARGUMENTS[3] (default: Medium)

### Implementation Steps
1. **Context Validation**: Verify we're in the right repository
2. **Planning Phase**: Use TodoWrite to break down the feature
3. **Issue Creation**: 
   - Primary: Create issue using mcp__github-http__create_issue with owner="vanman2024" and repo="DevLoopAI"
   - Fallback: If MCP server fails, use GitHub CLI:
     ```bash
     gh issue create --repo vanman2024/DevLoopAI \
       --title "[Feature]: {description}" \
       --body "{body}" \
       --label "enhancement,module:{module},priority:{priority}"
     ```
4. **Task Breakdown**: If complex, create subtasks
5. **Documentation**: Update relevant docs if needed

### Interactive Flow
If arguments not provided, ask user:
1. What feature do you want to request? (description)
2. Which project? (DevLoopAI, SynapseAI, FlyerApp, etc.)
3. Which milestone does this support?
4. What priority? (Critical, High, Medium, Low)
5. Which module will implement this?
6. Estimated hours?

### Issue Creation Template
Repository: `vanman2024/DevLoopAI`
```yaml
title: "[Feature]: {description}"
body: |
  ## Feature Description
  {detailed_description}
  
  ## Hierarchy
  - **Project**: {project}
  - **Milestone**: {milestone}  
  - **Phase**: {phase}
  - **Module**: {module}
  
  ## Technical Requirements
  {requirements}
  
  ## User Outcomes
  What user-facing outcomes will this feature create?
  
  ## Estimated Hours
  {hours}
  
labels:
  - enhancement
  - module:{module}
  - priority:{priority}
  - milestone:{milestone}
  - phase:{phase}
```

### Success Criteria
- Issue created with proper hierarchy fields
- Labels applied correctly
- Clear user outcomes defined
- Tasks can be created from this feature
- Follows DevLoop Project → Milestone → Phase → Module → Task structure

### Error Handling
If any step fails:
1. Use extended thinking to analyze the failure
2. Check GitHub permissions: !`gh auth status`
3. Validate repository: !`gh repo view vanman2024/DevLoopAI`
4. If MCP server fails, fallback to GitHub CLI:
   ```bash
   # Create issue with GitHub CLI
   gh issue create --repo vanman2024/DevLoopAI \
     --title "[Feature]: ${FEATURE_TITLE}" \
     --body "${ISSUE_BODY}" \
     --label "enhancement,module:${MODULE},priority:${PRIORITY}"
   ```
5. Retry with corrected approach
6. Update TodoWrite with current status

### Example Usage
```bash
# Create a feature with all details
/create-feature "Add OAuth2 authentication" "DevLoopAI" "MVP Launch" "High"

# Interactive mode (will ask questions)
/create-feature
```

Remember: Features represent user-facing outcomes that emerge from completed work, not just technical tasks.