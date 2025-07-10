# Multi-Agent Recruitment Setup Guide

## Overview

This guide explains how to set up a multi-agent MCP architecture for recruitment, where specialized AI agents communicate through the Model Context Protocol to process candidates automatically when they reach specific pipeline stages in CATS ATS.

## Architecture Overview

Instead of traditional webhooks, the multi-agent system uses:
- **Candidate Screening Agent** - Processes documents and evaluates candidates
- **Hiring Manager Agent** - Manages approvals and communications
- **Event Gateway** - Translates CATS webhooks to agent events

## Prerequisites

1. MCP Server infrastructure
2. CATS API access with webhook permissions
3. Agent deployment environment (Kubernetes/Docker)
4. Redis/Valkey for shared context
5. API keys for:
   - CATS ATS
   - Gemini AI
   - Slack (optional)
   - Email service

## Step 1: Deploy MCP Infrastructure

### MCP Server Setup

```bash
# Clone MCP server repository
git clone https://github.com/modelcontextprotocol/server
cd server

# Configure for recruitment agents
cp config/example.yaml config/recruitment.yaml
```

Edit `config/recruitment.yaml`:
```yaml
agents:
  - name: candidate-screening-agent
    endpoint: http://screening-agent:8001
    capabilities:
      - analyze_resume
      - process_questionnaire
      - score_candidate
      
  - name: hiring-manager-agent
    endpoint: http://hiring-agent:8002
    capabilities:
      - send_for_review
      - collect_feedback
      - schedule_interview

context_store:
  type: redis
  url: redis://redis:6379
  
security:
  auth_required: true
  api_keys:
    - name: cats-gateway
      key: ${CATS_GATEWAY_API_KEY}
```

### Deploy with Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  mcp-server:
    image: mcp/server:latest
    volumes:
      - ./config/recruitment.yaml:/config/mcp.yaml
    ports:
      - "8080:8080"
    depends_on:
      - redis
      
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
      
  screening-agent:
    build: ./agents/screening
    environment:
      - MCP_SERVER=http://mcp-server:8080
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - CATS_API_KEY=${CATS_API_KEY}
    depends_on:
      - mcp-server
      
  hiring-agent:
    build: ./agents/hiring
    environment:
      - MCP_SERVER=http://mcp-server:8080
      - SLACK_API_TOKEN=${SLACK_API_TOKEN}
      - EMAIL_API_KEY=${EMAIL_API_KEY}
    depends_on:
      - mcp-server
      
  event-gateway:
    build: ./gateway
    ports:
      - "8000:8000"
    environment:
      - MCP_SERVER=http://mcp-server:8080
      - WEBHOOK_SECRET=${WEBHOOK_SECRET}
      - MANAGER_REVIEW_STATUS_ID=${MANAGER_REVIEW_STATUS_ID}
    depends_on:
      - mcp-server
    command: uvicorn app:app --host 0.0.0.0 --port 8000 --reload

volumes:
  redis_data:
```

## Step 2: Configure Agents

### Screening Agent Configuration

Create `agents/screening/config.yaml`:
```yaml
agent:
  id: screening-agent-001
  name: Candidate Screening Agent
  
mcp:
  server: ${MCP_SERVER}
  register_on_startup: true
  
services:
  gemini:
    api_key: ${GEMINI_API_KEY}
    model: gemini-1.5-pro
    
  cats:
    api_url: https://api.catsone.com/v3
    api_key: ${CATS_API_KEY}
    
processing:
  max_concurrent: 10
  timeout_seconds: 300
  
scoring:
  weights:
    skills_match: 0.4
    experience: 0.3
    certifications: 0.2
    education: 0.1
    
  thresholds:
    auto_approve: 85
    manager_review: 70
    auto_reject: 50
```

### Hiring Manager Agent Configuration

Create `agents/hiring/config.yaml`:
```yaml
agent:
  id: hiring-agent-001
  name: Hiring Manager Communication Agent
  
mcp:
  server: ${MCP_SERVER}
  register_on_startup: true
  
channels:
  slack:
    enabled: true
    default_channel: C_RECRUITMENT
    
  email:
    enabled: true
    from: recruitment@company.com
    
notifications:
  urgent_jobs:
    - slack
    - email
  standard_jobs:
    - email
    
templates:
  candidate_review: templates/review.html
  interview_invite: templates/interview.html
  rejection: templates/rejection.html
```

## Step 3: Create Event Gateway

The Event Gateway translates CATS webhooks into MCP agent events.

### Install Dependencies

```bash
# gateway/requirements.txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
httpx==0.25.2
python-multipart==0.0.6
```

### Dockerfile

```dockerfile
# gateway/Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Gateway Implementation

```python
# gateway/app.py
from fastapi import FastAPI, Request, HTTPException, Form
from fastapi.responses import JSONResponse
import json
import os
from mcp_client import MCPClient

app = FastAPI(title="Recruitment Event Gateway")
mcp = MCPClient(os.environ['MCP_SERVER'])

MANAGER_REVIEW_STATUS_ID = os.environ.get('MANAGER_REVIEW_STATUS_ID')

@app.post("/webhook/cats")
async def handle_cats_webhook(request: Request):
    """Convert CATS webhook to agent event"""
    data = await request.json()
    
    # Verify webhook signature
    signature = request.headers.get('X-Webhook-Signature')
    if not await verify_webhook_signature(await request.body(), signature):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    # Route to appropriate agent based on event
    if data['event'] == 'candidate.pipeline_status_changed':
        if data['new_status_id'] == MANAGER_REVIEW_STATUS_ID:
            # Trigger screening agent
            result = await mcp.call_agent(
                'candidate-screening-agent',
                'process_new_candidate',
                {
                    'candidate_id': data['candidate_id'],
                    'job_id': data['job_id'],
                    'resume_url': data['resume_url'],
                    'questionnaire_url': data.get('questionnaire_url')
                }
            )
            
    return JSONResponse({"status": "processed", "agent_result": result})

@app.post("/webhook/slack")
async def handle_slack_interaction(payload: str = Form(...)):
    """Handle Slack button clicks and interactions"""
    interaction_data = json.loads(payload)
    
    if interaction_data['type'] == 'interactive_message':
        # Manager clicked approve/reject
        result = await mcp.call_agent(
            'hiring-manager-agent',
            'process_manager_decision',
            {
                'interaction': interaction_data,
                'candidate_id': interaction_data['callback_id'].split('_')[-1]
            }
        )
    
    return JSONResponse({"status": "ok"})

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "event-gateway"}

# Additional helper functions
async def verify_webhook_signature(body: bytes, signature: str) -> bool:
    """Verify webhook signature from CATS"""
    import hmac
    import hashlib
    
    secret = os.environ.get('WEBHOOK_SECRET', '').encode()
    expected = hmac.new(secret, body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)
```

## Step 4: Register CATS Webhook

### Find Required IDs

```python
# scripts/find_cats_ids.py
import requests

# Get pipeline statuses
response = requests.get(
    "https://api.catsone.com/v3/pipelines",
    headers={"Authorization": f"Token {CATS_API_KEY}"}
)

print("Pipeline Statuses:")
for status in response.json()['_embedded']['statuses']:
    print(f"  {status['id']}: {status['name']}")

# Get custom fields
response = requests.get(
    "https://api.catsone.com/v3/candidates/custom_fields",
    headers={"Authorization": f"Token {CATS_API_KEY}"}
)

print("\nCustom Fields:")
for field in response.json()['_embedded']['custom_fields']:
    print(f"  {field['id']}: {field['name']}")
```

### Register Webhook

```python
# scripts/register_webhook.py
webhook_config = {
    "url": "https://your-domain.com/webhook/cats",
    "events": [
        "candidate.created",
        "candidate.pipeline_status_changed",
        "candidate.updated"
    ],
    "active": True,
    "secret": os.environ['WEBHOOK_SECRET']
}

response = requests.post(
    "https://api.catsone.com/v3/webhooks",
    headers={
        "Authorization": f"Token {CATS_API_KEY}",
        "Content-Type": "application/json"
    },
    json=webhook_config
)

print(f"Webhook registered: {response.json()}")
```

## Step 5: Configure Shared Context

### Define Context Schema

```python
# shared/context_schema.py
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class JobRequirements(BaseModel):
    job_id: str
    title: str
    required_skills: List[str]
    preferred_skills: List[str]
    min_experience_years: int
    certifications: List[str]
    urgency: str  # low, medium, high, critical

class CandidateState(BaseModel):
    candidate_id: str
    score: float
    stage: str  # screening, review, interview, offer, rejected
    assigned_to: Optional[str]
    last_action: datetime
    notes: List[str]

class SharedContext(BaseModel):
    job_requirements: JobRequirements
    candidate_state: CandidateState
    workflow_rules: dict
    processing_history: List[dict]
```

## Step 6: Deploy Slack App (Optional)

### Create Slack App

1. Go to https://api.slack.com/apps
2. Create new app with:
   - Interactive Components enabled
   - Request URL: `https://your-domain.com/webhook/slack`
   - OAuth scopes: `chat:write`, `channels:read`, `users:read`

### Configure Interactive Messages

```javascript
// Slack app manifest
{
  "display_information": {
    "name": "Recruitment Assistant",
    "description": "AI-powered recruitment agent"
  },
  "features": {
    "bot_user": {
      "display_name": "Recruitment Bot"
    }
  },
  "oauth_config": {
    "scopes": {
      "bot": [
        "chat:write",
        "channels:read",
        "im:write",
        "users:read"
      ]
    }
  },
  "settings": {
    "interactivity": {
      "is_enabled": true,
      "request_url": "https://your-domain.com/webhook/slack"
    }
  }
}
```

## Step 7: Test the System

### Unit Test Agents

```python
# tests/test_screening_agent.py
async def test_candidate_scoring():
    agent = ScreeningAgent()
    
    candidate_data = {
        "skills": ["CAT", "Komatsu", "Mining"],
        "experience_years": 10,
        "certifications": ["Red Seal"]
    }
    
    job_requirements = {
        "required_skills": ["CAT", "Mining"],
        "min_experience_years": 5
    }
    
    score = await agent.score_candidate(candidate_data, job_requirements)
    assert score >= 80
```

### Integration Test

```bash
# Send test webhook
curl -X POST https://localhost:8000/webhook/cats \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Signature: test-signature" \
  -d '{
    "event": "candidate.pipeline_status_changed",
    "candidate_id": "12345",
    "job_id": "67890",
    "new_status_id": "manager_review",
    "resume_url": "https://example.com/resume.pdf"
  }'

# Check API documentation
open http://localhost:8000/docs
```

### End-to-End Test

1. Upload test candidate to CATS
2. Move to "Manager Review" status
3. Verify:
   - Screening Agent processes candidate
   - Context shared via MCP
   - Hiring Manager Agent sends notification
   - Manager can approve/reject
   - CATS updated with decision

## Step 8: Production Deployment

### Kubernetes Deployment

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: recruitment-agents
spec:
  replicas: 3
  selector:
    matchLabels:
      app: recruitment
  template:
    metadata:
      labels:
        app: recruitment
    spec:
      containers:
      - name: screening-agent
        image: recruitment/screening-agent:latest
        env:
        - name: MCP_SERVER
          value: "http://mcp-server:8080"
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
            
      - name: hiring-agent
        image: recruitment/hiring-agent:latest
        env:
        - name: MCP_SERVER
          value: "http://mcp-server:8080"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
```

### Monitoring Setup

```yaml
# monitoring/prometheus-rules.yaml
groups:
  - name: recruitment_agents
    rules:
    - alert: HighProcessingTime
      expr: agent_processing_time_seconds > 300
      annotations:
        summary: "Agent processing taking too long"
        
    - alert: LowAgentAvailability
      expr: up{job="recruitment-agents"} < 0.9
      annotations:
        summary: "Recruitment agents availability below 90%"
        
    - alert: HighErrorRate
      expr: rate(agent_errors_total[5m]) > 0.1
      annotations:
        summary: "Agent error rate above 10%"
```

## Step 9: Security Hardening

### API Gateway Configuration

```nginx
# nginx/recruitment-api.conf
server {
    listen 443 ssl;
    server_name api.recruitment.company.com;
    
    ssl_certificate /etc/ssl/certs/recruitment.crt;
    ssl_certificate_key /etc/ssl/private/recruitment.key;
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=webhook:10m rate=10r/s;
    
    location /webhook/cats {
        limit_req zone=webhook burst=20;
        
        # IP whitelist for CATS
        allow 54.243.123.0/24;  # CATS IP range
        deny all;
        
        proxy_pass http://event-gateway:8000;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Webhook-Signature $http_x_webhook_signature;
    }
}
```

### Secrets Management

```yaml
# k8s/secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: recruitment-secrets
type: Opaque
stringData:
  cats-api-key: ${CATS_API_KEY}
  gemini-api-key: ${GEMINI_API_KEY}
  slack-token: ${SLACK_API_TOKEN}
  webhook-secret: ${WEBHOOK_SECRET}
```

## Troubleshooting

### Agent Communication Issues

```bash
# Check MCP server logs
kubectl logs -f deployment/mcp-server

# Verify agent registration
curl http://mcp-server:8080/agents

# Test agent directly
curl -X POST http://mcp-server:8080/agent/screening-agent/call \
  -H "Content-Type: application/json" \
  -d '{"method": "health_check"}'
```

### Context Sharing Problems

```bash
# Check Redis connectivity
redis-cli -h redis ping

# Monitor context updates
redis-cli -h redis MONITOR | grep "agent:context"

# Clear stale context
redis-cli -h redis --scan --pattern "agent:context:*" | xargs redis-cli DEL
```

### Performance Tuning

```python
# Adjust agent concurrency
AGENT_CONFIG = {
    "max_concurrent_tasks": 20,
    "batch_size": 5,
    "processing_timeout": 300,
    "retry_attempts": 3,
    "retry_delay": 10
}
```

## Best Practices

1. **Agent Health Checks** - Implement regular health checks
2. **Circuit Breakers** - Prevent cascade failures
3. **Idempotency** - Ensure operations can be safely retried
4. **Audit Logging** - Log all agent decisions
5. **Graceful Degradation** - Handle service outages
6. **Load Testing** - Test with realistic candidate volumes
7. **Backup Agents** - Deploy across availability zones

This multi-agent architecture provides a scalable, intelligent recruitment system that processes candidates automatically while maintaining flexibility and reliability.