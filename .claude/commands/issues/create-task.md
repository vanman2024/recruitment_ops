---
allowed-tools: mcp__github-http__*, Write(*), Read(*), TodoWrite(*), mcp__sequential-thinking-http__sequentialthinking, Bash(*), Task(*)
description: Create a development task (atomic work unit) in the DevLoop hierarchy
---

# Create Task Command

## Context Loading
- Current directory: !`pwd`
- Git status: !`git status --porcelain`
- Current branch: !`git branch --show-current`
- Issue template: @.github/ISSUE_TEMPLATE/task.yaml
- Database hierarchy: @/home/gotime2022/devloop3/backend/HIERARCHY_UPDATE_SUMMARY.md
- Active milestones: !`gh issue list --repo vanman2024/DevLoopAI --label "milestone" --limit 5`

## Extended Thinking Trigger
Thinkhard about this step by step:
1. Understand the task requirements and scope
2. Identify the correct position in Project → Milestone → Phase → Module → Task hierarchy
3. Determine task type and specialist needed
4. Estimate hours realistically
5. Identify dependencies and related files

## Your Task
Create an atomic development task that can be assigned to a Claude instance for autonomous execution.

### GitHub Configuration
- Owner: vanman2024
- Repo: DevLoopAI
- Fallback: gh CLI if MCP tool fails

### Requirements Analysis
Based on $ARGUMENTS:
- Task Description: $ARGUMENTS[0]
- Module: $ARGUMENTS[1] (Backend API, Frontend UI, Database, etc.)
- Priority: $ARGUMENTS[2] (Critical, High, Medium, Low)
- Hours: $ARGUMENTS[3] (estimated hours)

### Implementation Steps
1. **Hierarchy Validation**: Ensure task fits in proper hierarchy
2. **Task Planning**: Use TodoWrite to define acceptance criteria
3. **Issue Creation**: 
   - Primary: Create task using mcp__github-http__create_issue with owner="vanman2024" and repo="DevLoopAI"
   - Fallback: If MCP server fails, use GitHub CLI:
     ```bash
     gh issue create --repo vanman2024/DevLoopAI \
       --title "[Task]: {description}" \
       --body "{body}" \
       --label "task,module:{module},priority:{priority},milestone:{milestone},phase:{phase},hours:{hours},ready-for-claude"
     ```
4. **Assignment Ready**: Ensure task has all info for Claude execution
5. **Link Dependencies**: Connect to related issues/PRs

### Interactive Flow
If arguments not provided, ask user:
1. What specific task needs to be done?
2. Which module owns this task?
3. What project/milestone/phase does this belong to?
4. What's the priority?
5. How many hours estimated?
6. Any dependencies or blockers?
7. Which specialist type should handle this?

### Task Creation Template
```yaml
title: "[Task]: {description}"
body: |
  ## Task Description
  {detailed_description}
  
  ## Hierarchy
  - **Project**: {project}
  - **Milestone**: {milestone}
  - **Phase**: {phase}
  - **Module**: {module}
  
  ## Acceptance Criteria
  - [ ] {criterion_1}
  - [ ] {criterion_2}
  - [ ] {criterion_3}
  - [ ] Tests written with 90%+ coverage
  
  ## Technical Details
  {technical_requirements}
  
  ## Estimated Hours: {hours}
  
  ## Dependencies
  {dependencies}
  
  ## Related Files
  {files_to_modify}
  
  ## Specialist Required: {specialist_type}
  
labels:
  - task
  - module:{module}
  - priority:{priority}
  - milestone:{milestone}
  - phase:{phase}
  - hours:{hours}
  - ready-for-claude
```

### Task Types
- Feature Implementation
- Bug Fix
- Refactoring
- Testing
- Documentation
- Performance Optimization
- Security Fix
- Infrastructure
- MCP Server Development
- API Development
- UI Component
- Database Migration

### Success Criteria
- Task is atomic and completable in estimated hours
- Clear acceptance criteria defined
- All hierarchy fields populated
- Ready for Claude assignment
- Includes test coverage requirements
- Dependencies clearly stated

### Error Handling
If any step fails:
1. Use extended thinking to analyze the failure
2. Validate hierarchy: Ensure project/milestone/phase exist
3. Check for duplicate tasks: !`gh issue list --repo vanman2024/DevLoopAI --search "{description}"`
4. If MCP server fails, fallback to GitHub CLI:
   ```bash
   # Create task with GitHub CLI
   gh issue create --repo vanman2024/DevLoopAI \
     --title "[Task]: ${TASK_TITLE}" \
     --body "${TASK_BODY}" \
     --label "task,module:${MODULE},priority:${PRIORITY}"
   ```
5. Retry with corrected approach
6. Update TodoWrite with current status

### Example Usage
```bash
# Create task with details
/create-task "Implement JWT refresh tokens" "Backend API" "High" "8"

# Interactive mode
/create-task
```

Remember: Tasks are the atomic units of work that Claude instances execute autonomously. They must be self-contained with clear acceptance criteria.