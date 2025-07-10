---
allowed-tools: ALL
description: Create a new feature with full DevLoop workflow
---

# 🚀 Create Feature: $ARGUMENTS

## Feature Planning

**Think deeply** about the feature "$ARGUMENTS":
1. What problem does it solve?
2. How does it fit into the existing architecture?
3. What components need to be created/modified?
4. What are the testing requirements?

## Check Existing Context

### Database Check
Use **mcp__supabase-v3__execute_sql** with project_id "dkpwdljgnysqzjufjtnk":
```sql
SELECT t.name, t.status, m.name as milestone
FROM tasks t
JOIN modules mo ON t.module_id = mo.id
JOIN phases ph ON mo.phase_id = ph.id
JOIN milestones m ON ph.milestone_id = m.id
WHERE LOWER(t.name) LIKE LOWER('%$ARGUMENTS%')
LIMIT 5;
```

### GitHub Check
- Search issues: !`gh issue list --search "$ARGUMENTS" --repo vanman2024/DevLoopAI`
- Search PRs: !`gh pr list --search "$ARGUMENTS" --repo vanman2024/DevLoopAI`

### Codebase Check
- Search for related code: !`rg -i "$ARGUMENTS" --type-add 'code:*.{js,ts,tsx,py}' -t code -C 2`
- Check documentation: !`rg -i "$ARGUMENTS" docs/ -C 2`

## Implementation Plan

### 1. Create GitHub Issue
Use **mcp__github__create_issue**:
- owner: "vanman2024"
- repo: "DevLoopAI"
- title: "Feature: $ARGUMENTS"
- body: Detailed description based on analysis

### 2. Database Task Creation
Create task hierarchy for "$ARGUMENTS" feature

### 3. Branch Creation
!`git checkout -b feature/$ARGUMENTS-$(date +%Y%m%d)`

### 4. Component Generation
If UI needed, use **mcp__vercel-v0__generate_component**:
- description: "$ARGUMENTS component"
- Output to appropriate directory

### 5. Implementation Checklist
Use **TodoWrite** to create tasks:
- [ ] Design feature architecture
- [ ] Create database schema if needed
- [ ] Implement backend endpoints
- [ ] Create frontend components
- [ ] Add comprehensive tests
- [ ] Update documentation
- [ ] Create PR with full context

## Success Criteria
- Feature implements "$ARGUMENTS" completely
- All tests pass
- Documentation updated
- PR links to issue and tasks