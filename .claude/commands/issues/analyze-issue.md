---
allowed-tools: mcp__github-http__*, mcp__supabase-v4__*, Read(*), Write(*), TodoWrite(*), mcp__sequential-thinking-http__sequentialthinking, Bash(*), Grep(*), Task(*)
description: Deep issue analysis with extended thinking, hierarchy mapping, and implementation planning
---

# Analyze Issue Command

## Context Loading
- Current directory: !`pwd`
- Git status: !`git status --porcelain`
- Current branch: !`git branch --show-current`
- Recent commits: !`git log --oneline -5`
- Project structure: !`find . -maxdepth 2 -type d | head -10`
- Package info: @package.json
- Database hierarchy: @/home/gotime2022/devloop3/backend/HIERARCHY_UPDATE_SUMMARY.md
- Issue templates: @.github/ISSUE_TEMPLATE/
- Testing standards: @.claude/docs/testing-standards.md

## Extended Thinking Trigger
Thinkhard about this step by step:
1. Analyze the issue requirements and understand the root problem
2. Map the issue to the DevLoop hierarchy (Project → Milestone → Phase → Module → Task)
3. Identify all components and files that will be affected
4. Consider architectural implications and design patterns
5. Plan testing strategy with 90%+ coverage requirements
6. Identify dependencies, blockers, and risks
7. Estimate effort realistically based on complexity

## Your Task
Perform deep analysis of issue $ARGUMENTS[0] to create a comprehensive implementation plan.

### GitHub Configuration
- Owner: vanman2024
- Repo: DevLoopAI
- Fallback: gh CLI if MCP tool fails

### Requirements Analysis
Based on $ARGUMENTS:
- Issue Number/URL: $ARGUMENTS[0]
- Repository: $ARGUMENTS[1] (default: DevLoopAI)
- Analysis Depth: $ARGUMENTS[2] (quick/standard/deep, default: deep)

### Implementation Steps

1. **Issue Context Extraction**
   ```javascript
   // Parse issue number from various formats
   const issueNum = $ARGUMENTS[0].match(/#?(\d+)/)[1];
   const [owner, repo] = ($ARGUMENTS[1] || "vanman2024/DevLoopAI").split('/');
   ```

2. **Fetch Issue Details**
   - Primary: Use mcp__github-http__get_issue with owner="vanman2024" and repo="DevLoopAI"
   - Fallback: If MCP server fails, use GitHub CLI:
     ```bash
     gh issue view --repo vanman2024/DevLoopAI ${issueNum} --json title,body,labels,milestone,assignees
     ```
   - Extract title, body, labels, milestone, assignees
   - Analyze issue type (bug/feature/enhancement)
   - Identify priority and severity

3. **Gather Related Context**
   - Search related issues: mcp__github-http__search_issues
   - Find linked PRs: !`gh pr list --repo vanman2024/DevLoopAI --search "#{issueNum}"`
   - Code references: !`rg -i "issue.*{issueNum}|#{issueNum}" --type-add 'code:*.{js,ts,tsx,py,md}' -t code -C 2`
   - Recent commits: !`git log --grep="#{issueNum}" --oneline -10`

4. **Database Hierarchy Analysis**
   Use mcp__supabase-v4__execute_sql with project_id "dkpwdljgnysqzjufjtnk":
   ```sql
   -- Find existing tasks for this issue
   SELECT 
     t.id, t.name, t.status, t.estimated_hours,
     m.name as module_name,
     ph.name as phase_name,
     ml.name as milestone_name,
     p.name as project_name
   FROM tasks t
   JOIN modules m ON t.module_id = m.id
   JOIN phases ph ON m.phase_id = ph.id
   JOIN milestones ml ON ph.milestone_id = ml.id
   JOIN projects p ON ml.project_id = p.id
   WHERE t.github_issue_number = $1 
      OR LOWER(t.name) LIKE LOWER('%issue ' || $1 || '%');
   ```

5. **Technical Deep Dive**
   Use mcp__sequential-thinking-http__sequentialthinking:
   - Architectural implications
   - Component dependencies
   - Performance considerations
   - Security implications
   - Breaking change analysis

6. **Implementation Planning**
   Create detailed task breakdown with TodoWrite:
   - Analysis phase (understanding requirements)
   - Design phase (architecture decisions)
   - Implementation phase (code changes)
   - Testing phase (90%+ coverage)
   - Documentation phase
   - Review phase

7. **Risk Assessment**
   Think deeper about:
   - Breaking changes to existing functionality
   - Performance degradation risks
   - Security vulnerabilities
   - User experience impacts
   - Data migration needs

### Analysis Report Template
```markdown
# 📊 Issue Analysis: #{issue_number}

## Summary
- **Type**: {bug/feature/enhancement}
- **Priority**: {critical/high/medium/low}
- **Complexity**: {simple/moderate/complex}
- **Estimated Effort**: {hours} hours

## Hierarchy Mapping
- **Project**: {project}
- **Milestone**: {milestone}
- **Phase**: {phase}
- **Module**: {module}
- **Tasks Required**: {count}

## Technical Analysis

### Affected Components
- Frontend: {components}
- Backend: {services/apis}
- Database: {tables/migrations}
- Infrastructure: {services}

### Implementation Approach
{detailed_approach}

### Testing Strategy
- Unit Tests: {approach}
- Integration Tests: {approach}
- E2E Tests: {approach}
- Coverage Target: 90%+ (95% for critical paths)

## Dependencies & Blockers
- Depends on: {issues/PRs}
- Blocks: {issues/PRs}
- External dependencies: {libraries/services}

## Risk Analysis
- **High Risks**: {critical_risks}
- **Medium Risks**: {moderate_risks}
- **Mitigation Strategies**: {approaches}

## Implementation Plan
1. {step_1} - {hours}h
2. {step_2} - {hours}h
3. {step_3} - {hours}h

## Recommendation
{clear_next_steps}
```

8. **Update Issue with Analysis**
   - Primary: Use mcp__github-http__add_issue_comment with owner="vanman2024" and repo="DevLoopAI"
   - Fallback: If MCP server fails, use GitHub CLI:
     ```bash
     gh issue comment --repo vanman2024/DevLoopAI ${issueNum} --body "${analysis_summary}"
     ```

### Success Criteria
- Complete understanding of issue requirements
- Clear hierarchy mapping established
- All affected components identified
- Realistic effort estimation provided
- Testing strategy defined (90%+ coverage)
- Dependencies and risks documented
- Implementation plan created
- Issue updated with analysis

### Error Handling
If any step fails:
1. Use extended thinking to analyze the failure
2. Check GitHub permissions: !`gh auth status`
3. Verify repository access: !`gh repo view vanman2024/DevLoopAI`
4. If MCP server fails, use GitHub CLI as fallback for all operations
5. Check database connectivity
6. Retry with corrected approach
7. Update TodoWrite with current status

### Example Usage
```bash
# Analyze issue with defaults
/analyze-issue 42

# Analyze issue from specific repo
/analyze-issue 123 "vanman2024/SynapseAI"

# Quick analysis mode
/analyze-issue 456 "DevLoopAI" "quick"
```

### Chain Commands
After analysis:
- `/create-task` - Create implementation tasks
- `/sdlc-workflow` - Start full development cycle
- `/estimate-effort` - Detailed time estimation

Remember: Good analysis prevents bad implementation. Take time to understand before coding.