---
allowed-tools: Read, Bash, mcp__github__get_repository, mcp__supabase-v3__execute_sql, TodoWrite
description: Understand the big picture - what DevLoopAI/SynapseAI is building and why
---

# 🌍 Big Picture Context - DevLoopAI → SynapseAI Vision

**Arguments**: $ARGUMENTS

## 1. Project Vision & Architecture

### Core Documentation
- Project vision: @docs/SYNAPSEAI_POSITIONING.md
- Product features: @docs/SYNAPSEAI_PRODUCT_FEATURES.md
- Workflow architecture: @docs/workflows/COMPREHENSIVE_DEVLOOP_WORKFLOW.md
- Parallel system design: @docs/workflows/SYNAPSE_PARALLEL_SYSTEM.md
- Master workflow: @docs/workflows/MASTER_SYNAPSE_WORKFLOW.md

### Repository Overview
Use **mcp__github__get_repository**:
- owner: "vanman2024"
- repo: "DevLoopAI"

## 2. What We're Building

**Think deeply** about the DevLoopAI → SynapseAI transformation:

### The Vision
DevLoopAI is transforming into **SynapseAI** - an autonomous software development platform that enables:
- 🤖 **100+ parallel Claude instances** working autonomously
- 📊 **< 5% human intervention** required
- 🔄 **24/7 continuous development** capability
- 🎯 **Predictable delivery** based on task estimates
- 🔧 **Self-healing** through automated issue detection

### Architecture Components
1. **MCP Server Ecosystem** (20+ servers)
   - Tools for every development need
   - Seamless integration between services
   - Real-time collaboration capabilities

2. **Database-Driven Workflow**
   - Hierarchy: Project → Milestone → Phase → Module → Task
   - Every action tracked and coordinated
   - Dependencies automatically managed

3. **GitHub Integration**
   - Issues automatically converted to tasks
   - PRs linked to development work
   - Webhooks drive automation

4. **Claude Orchestration**
   - Multiple Claude instances per project
   - Specialized agents for different tasks
   - Memory and context persistence

## 3. Current State Assessment

### Database Overview
Use **mcp__supabase-v3__execute_sql** with project_id "dkpwdljgnysqzjufjtnk":
```sql
-- High-level project metrics
SELECT 
  COUNT(DISTINCT p.id) as total_projects,
  COUNT(DISTINCT m.id) as total_milestones,
  COUNT(DISTINCT t.id) as total_tasks,
  COUNT(DISTINCT CASE WHEN t.status = 'completed' THEN t.id END) as completed_tasks,
  COUNT(DISTINCT CASE WHEN t.assigned_specialist IS NOT NULL THEN t.assigned_specialist END) as active_specialists,
  COUNT(DISTINCT t.session_id) as unique_sessions
FROM projects p
LEFT JOIN milestones m ON p.id = m.project_id
LEFT JOIN phases ph ON m.id = ph.milestone_id
LEFT JOIN modules mo ON ph.id = mo.phase_id
LEFT JOIN tasks t ON mo.id = t.module_id
WHERE p.name IN ('DevLoopAI', 'SynapseAI');
```

### Development Velocity
!`echo "📈 Recent development activity:"`
!`git log --since="1 week ago" --pretty=format:"%h %s" --abbrev-commit | head -10`
!`echo -e "\n📊 Code changes last 7 days:"`
!`git log --since="1 week ago" --pretty=tformat: --numstat | awk '{ add += $1; subs += $2; loc += $1 - $2 } END { printf "Added: %s, Removed: %s, Net: %s\n", add, subs, loc }'`

## 4. The Development Philosophy

### Key Principles
1. **Everything is a Workflow** - From issue to deployment
2. **Database is Truth** - All state tracked in Supabase
3. **Parallel by Default** - Multiple agents working simultaneously
4. **Self-Documenting** - Code and docs generated together
5. **Continuous Validation** - Tests run automatically

### MCP Tools Enable
- **Rapid Prototyping**: V0 for UI components
- **Automated Testing**: Multiple test frameworks
- **Seamless Deployment**: Vercel integration
- **Real-time Collaboration**: GitHub + Supabase sync

## 5. Strategic Priorities

**Think harder** about current priorities based on:
- Migration status from DevLoopAI to SynapseAI
- Technical debt that needs addressing
- Features that unlock more automation
- Integration gaps between systems

### Focus Areas
!`FOCUS=$(echo "$ARGUMENTS" | tr '[:upper:]' '[:lower:]'); case "$FOCUS" in`
!`  "migration") echo "🔄 Focus: DevLoopAI → SynapseAI migration status" ;;`
!`  "automation") echo "🤖 Focus: Automation capabilities and gaps" ;;`
!`  "integration") echo "🔗 Focus: System integration points" ;;`
!`  *) echo "🎯 Focus: Overall system architecture" ;;`
!`esac`

## 6. How Everything Connects

### The Flow
```
GitHub Issue → Database Task → Claude Assignment → 
Development → Testing → PR Creation → Review → 
Deployment → Monitoring → Feedback Loop
```

### Key Integrations
- **GitHub ↔ Database**: Issues become tasks automatically
- **Claude ↔ MCP**: Tools provide capabilities
- **Database ↔ Frontend**: Real-time dashboards
- **Testing ↔ Deployment**: Automated quality gates

## 7. Success Metrics

**Think more deeply** about how we measure success:
- Task completion rates
- Time from issue to deployment
- Test coverage percentages
- System uptime and reliability
- Developer productivity multipliers

## Output

Provide a comprehensive understanding including:

### 🏗️ What We're Building
- The SynapseAI vision and goals
- How it revolutionizes development
- Key differentiators

### 📊 Current Progress
- Migration status
- Feature completeness
- System maturity

### 🎯 Strategic Direction
- Next major milestones
- Critical path items
- Innovation opportunities

### 💡 Insights
- Patterns observed
- Opportunities identified
- Risks to mitigate

Use **TodoWrite** to capture any strategic initiatives or big-picture tasks identified.

Remember: This command provides the **why** behind everything we're doing, not just the **what**.