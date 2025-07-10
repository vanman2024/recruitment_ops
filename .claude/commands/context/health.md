---
allowed-tools: Bash, mcp__vercel-deploy__list_deployments, mcp__vercel-deploy__get_deployment_status, mcp__supabase-v3__execute_sql, mcp__github__list_pull_requests, mcp__docker__list_containers
description: Quick health check of all DevLoopAI services and deployments
---

## Context
- Current time: !`date`
- Running services: !`ps aux | grep -E "(python|node)" | grep -v grep | wc -l` processes
- Docker status: !`docker ps --format "table {{.Names}}\t{{.Status}}" 2>/dev/null | head -5 || echo "Docker not running"`

## Your task

Perform a comprehensive health check of all DevLoop3 services:

### 1. Frontend Deployment Status
Use Vercel MCP to check:
```python
# Get latest production deployment
deployments = mcp__vercel-deploy-http__list_deployments(
    limit=3,
    target="production",
    state="READY"
)

# Check deployment health
if deployments:
    latest = deployments[0]
    print(f"✅ Production: {latest['url']} - {latest['state']}")
    print(f"   Deployed: {latest['created']}")
    
    # Check for recent errors
    logs = mcp__vercel-deploy-http__get_deployment_logs(
        deployment_id=latest['id'],
        type="error",
        limit=10
    )
    if logs:
        print(f"⚠️  Recent errors detected in logs")
```

### 2. Backend Services
```bash
# Check if backend is running
curl -s http://localhost:8891/health || echo "❌ Backend not responding"

# Check unified backend
lsof -i :8891 | grep LISTEN || echo "❌ Port 8891 not listening"

# Check webhook endpoint
curl -s http://localhost:8891/api/github/webhook-status || echo "❌ Webhook endpoint down"
```

### 3. Database Health
Use Supabase MCP:
```sql
-- Check database connectivity and recent activity
SELECT 
    'Database Status' as check_type,
    COUNT(*) as total_tasks,
    SUM(CASE WHEN created_at > NOW() - INTERVAL '1 hour' THEN 1 ELSE 0 END) as recent_tasks,
    SUM(CASE WHEN status = 'in_progress' THEN 1 ELSE 0 END) as active_tasks
FROM tasks;

-- Check for sync issues
SELECT 
    'Sync Status' as check_type,
    COUNT(*) as sync_errors,
    MAX(created_at) as last_error
FROM github_sync_log
WHERE status = 'error' 
AND created_at > NOW() - INTERVAL '24 hours';
```

### 4. GitHub Integration
Check recent PR/issue activity:
- List recent merged PRs to verify deployment pipeline
- Check for stuck PRs awaiting review
- Verify webhook deliveries succeeded

### 5. Docker Services (if applicable)
```python
# Check running containers
containers = mcp__docker-http__docker_list_containers(all=False)
for container in containers:
    print(f"🐳 {container['name']}: {container['status']}")
```

### Health Report Format:
```
🏥 DevLoop3 Health Check - [timestamp]

✅ Frontend (Vercel)
   Status: READY
   URL: https://devloop.vercel.app
   Last Deploy: 2h ago
   Errors: None

✅ Backend API
   Status: Running on :8891
   Uptime: 14h 23m
   Active Connections: 3

⚠️ Database
   Status: Connected
   Active Tasks: 12
   Sync Errors: 2 (investigating)

✅ GitHub Integration  
   Webhooks: Active
   Recent PRs: 3 merged today
   
Overall Health: 🟡 OPERATIONAL WITH WARNINGS
```

### Action Items:
Based on health check results, suggest:
1. Services that need restart
2. Deployments that need rollback
3. Logs that need investigation
4. Sync issues to resolve

This provides a quick operational status check!