---
allowed-tools: mcp__vercel-deploy-http__*, mcp__github-http__list_pull_requests, mcp__github-http__list_commits, Bash(*), TodoWrite, Read(*), mcp__supabase-v3__insert_data, mcp__supabase-v3__select_data
description: Advanced deployment operations, monitoring, and incident response using Vercel MCP
---

@/home/gotime2022/devloop3/.claude/docs/VERCEL_DEPLOY_MCP_INTEGRATION.md

## Context

### Real-time Deployment Status
- Latest production: !`echo "Check with vercel_list_deployments(target='production', limit=1)"`
- Recent deploys: !`echo "Use vercel_list_deployments(limit=10) for history"`
- Active domains: !`echo "Verify with vercel_list_domains()"`

### GitHub Integration
- Recent merges: !`gh pr list --state merged --limit 3 --json number,title,mergedAt,headRefName | jq -r '.[] | "#\(.number): \(.title) [\(.headRefName)]"'`
- Master commits: !`git log origin/master --oneline -5 --no-decorate`

## Your Task: Deployment Operations

### 1. 🏥 Deployment Health Check

Perform comprehensive deployment verification:

```python
# Get latest production deployment
prod_deployments = mcp__vercel-deploy-http__list_deployments(
    limit=1,
    target="production",
    state="READY"
)

if prod_deployments:
    latest = prod_deployments[0]
    
    # Get detailed status
    status = mcp__vercel-deploy-http__get_deployment_status(
        deployment_id=latest["id"]
    )
    
    # Check deployment age
    # If older than 24h, might need update
    
    # Verify it matches latest master
    # Compare deployment commit with git log
    
    # Check for errors
    error_logs = mcp__vercel-deploy-http__get_deployment_logs(
        deployment_id=latest["id"],
        type="error",
        limit=50
    )
```

### 2. 🚨 Emergency Rollback Procedure

When production issues are detected:

```python
# Step 1: Find stable deployment
deployments = mcp__vercel-deploy-http__list_deployments(
    project_id="devloop-frontend",  # Or get from project list
    target="production",
    state="READY",
    limit=5
)

# Step 2: Identify rollback target
print("Recent production deployments:")
for i, dep in enumerate(deployments):
    print(f"{i}: {dep['created']} - {dep['url']} [{dep['id']}]")

# Step 3: Execute rollback
rollback_to = deployments[1]["id"]  # Previous deployment
result = mcp__vercel-deploy-http__rollback_deployment(
    project_id="devloop-frontend",
    to_deployment_id=rollback_to
)

# Step 4: Document in database
mcp__supabase-v3__insert_data(
    table="deployment_events",
    data={
        "event_type": "emergency_rollback",
        "from_deployment": deployments[0]["id"],
        "to_deployment": rollback_to,
        "reason": "Production incident - [describe issue]",
        "performed_by": "deployment-ops-command",
        "timestamp": "now()"
    }
)

# Step 5: Create GitHub issue
mcp__github-http__create_issue(
    owner="vanman2024",
    repo="DevLoopAI",
    title="🚨 Emergency Rollback Performed",
    body=f"Rolled back from {deployments[0]['id']} to {rollback_to}",
    labels=["incident", "deployment", "production"]
)
```

### 3. 🔧 Environment Variable Management

Sync and manage environment variables:

```python
# List all environments
for target in ["production", "preview", "development"]:
    vars = mcp__vercel-deploy-http__list_env_variables(
        project_id="devloop-frontend",
        target=target
    )
    print(f"\n{target.upper()} Environment ({len(vars)} vars):")
    for var in vars:
        print(f"  - {var['key']}: {'*' * 8} [{var['type']}]")

# Sync missing variables
required_vars = [
    "NEXT_PUBLIC_SUPABASE_URL",
    "NEXT_PUBLIC_SUPABASE_ANON_KEY",
    "DATABASE_URL",
    "JWT_SECRET"
]

for var_name in required_vars:
    if var_name not in [v['key'] for v in prod_vars]:
        print(f"⚠️  Missing: {var_name}")
        # Create it with proper value
```

### 4. 🔍 Deployment Debugging

Investigate failed or problematic deployments:

```python
# Find recent failed deployments
failed = mcp__vercel-deploy-http__list_deployments(
    limit=10,
    state="ERROR"
)

for deployment in failed:
    print(f"\n❌ Failed: {deployment['id']}")
    
    # Get build logs
    build_logs = mcp__vercel-deploy-http__get_deployment_logs(
        deployment_id=deployment['id'],
        type="build",
        limit=100
    )
    
    # Analyze common issues:
    # - Missing env vars
    # - Build errors
    # - Dependency issues
    # - Memory limits
```

### 5. 💰 Preview Deployment Cleanup

Optimize costs by removing old previews:

```python
# Get all preview deployments
previews = mcp__vercel-deploy-http__list_deployments(
    target="preview",
    limit=50
)

# Find old ones (>7 days)
old_previews = []
for preview in previews:
    created = parse_date(preview['created'])
    age_days = (now() - created).days
    if age_days > 7:
        old_previews.append(preview)

print(f"Found {len(old_previews)} old preview deployments")

# Clean up closed PR previews
merged_prs = mcp__github-http__list_pull_requests(
    state="closed",
    limit=20
)

for preview in old_previews:
    # Match preview to PR
    # If PR is closed/merged, safe to remove
    # Cancel or delete preview deployment
```

### 6. 📊 Deployment Analytics

Track deployment patterns and performance:

```python
# Get deployment history
all_deployments = mcp__vercel-deploy-http__list_deployments(
    limit=100
)

# Calculate metrics
deployments_by_day = {}
failed_deployments = 0
avg_build_time = 0
deployment_frequency = {}

# Store in database for tracking
mcp__supabase-v3__insert_data(
    table="deployment_metrics",
    data={
        "date": "today()",
        "total_deployments": len(all_deployments),
        "failed_deployments": failed_deployments,
        "avg_build_time_seconds": avg_build_time,
        "preview_deployments": preview_count,
        "production_deployments": prod_count
    }
)
```

### 7. 🔄 Post-Merge Verification

Automatically verify deployments after PR merges:

```bash
# Get recently merged PRs
RECENT_MERGES=$(gh pr list --state merged --limit 5 --json number,title,mergedAt,headRefName)

# For each merged PR, verify deployment
```

Then verify deployment succeeded and matches the merge commit.

### Decision Tree

1. **Regular Check** → Health Check → Report status
2. **Production Issue** → Rollback → Document → Create issue
3. **Configuration Change** → Sync env vars → Trigger deployment
4. **Failed Deployment** → Debug logs → Fix issue → Retry
5. **Cost Concern** → Preview cleanup → Report savings

### Output Format

```markdown
# 🚀 Deployment Operations Report

## Current Status
- Production: [URL] - [Status] - [Age]
- Latest Deploy: [ID] - [Commit]
- Health: [✅ Healthy | ⚠️ Warning | ❌ Critical]

## Recent Activity
- [List recent deployments with status]

## Environment Variables
- Production: [X] vars configured
- Preview: [Y] vars configured
- Sync Status: [✅ Synced | ⚠️ Differences found]

## Recommendations
1. [Action items based on findings]
2. [Preventive measures]
3. [Optimization opportunities]

## Metrics
- Deployment Success Rate: [X]%
- Average Build Time: [X]s
- Active Previews: [X] ($[Y]/month)
```

Remember: This command handles operations that GitHub Actions can't or shouldn't handle automatically.