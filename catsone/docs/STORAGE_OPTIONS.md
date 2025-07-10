# Storage Options for Multi-Agent Recruitment Architecture

## Overview

In a multi-agent MCP architecture, storage needs to support distributed agent communication, shared context, and efficient document processing. This guide outlines storage strategies optimized for agent-based recruitment workflows.

## Agent Storage Requirements

### 1. Shared Context Storage
Agents need fast, concurrent access to shared state and context.

### 2. Document Processing
Temporary storage for PDF/image conversion during analysis.

### 3. Agent Memory
Persistent storage for agent learning and preferences.

### 4. Audit Trail
Immutable logs of all agent decisions and actions.

## Recommended Architecture

### Primary: Distributed State Store (Redis/Valkey)

**Purpose:** Real-time shared context between agents

**Implementation:**
```python
# Agent shared context
class AgentContextStore:
    def __init__(self, redis_client):
        self.redis = redis_client
    
    async def share_context(self, key: str, context: dict, ttl: int = 3600):
        """Share context between agents with TTL"""
        await self.redis.setex(
            f"agent:context:{key}",
            ttl,
            json.dumps(context)
        )
    
    async def get_context(self, key: str) -> dict:
        """Retrieve shared context"""
        data = await self.redis.get(f"agent:context:{key}")
        return json.loads(data) if data else {}
    
    async def subscribe_to_updates(self, pattern: str):
        """Real-time context updates via pub/sub"""
        pubsub = self.redis.pubsub()
        await pubsub.psubscribe(f"agent:updates:{pattern}")
        return pubsub
```

**Benefits:**
- ✅ Sub-millisecond latency
- ✅ Pub/sub for real-time updates
- ✅ Automatic expiration
- ✅ Distributed locks for coordination

### Secondary: Object Storage (S3/GCS)

**Purpose:** Document storage and agent memory persistence

**Implementation:**
```python
# Document processing with agents
class DocumentStore:
    def __init__(self, s3_client):
        self.s3 = s3_client
        self.bucket = "recruitment-documents"
    
    async def store_temporary(self, doc_id: str, content: bytes):
        """Store with 1-hour expiration for processing"""
        await self.s3.put_object(
            Bucket=self.bucket,
            Key=f"temp/{doc_id}",
            Body=content,
            Metadata={"ttl": "3600"},
            StorageClass="INTELLIGENT_TIERING"
        )
    
    async def store_permanent(self, candidate_id: str, doc_type: str, content: bytes):
        """Permanent storage with encryption"""
        await self.s3.put_object(
            Bucket=self.bucket,
            Key=f"candidates/{candidate_id}/{doc_type}",
            Body=content,
            ServerSideEncryption="AES256"
        )
```

### Tertiary: Time-Series Database (InfluxDB/TimescaleDB)

**Purpose:** Agent decision tracking and analytics

**Implementation:**
```python
# Agent decision logging
class AgentAuditLog:
    def __init__(self, influx_client):
        self.influx = influx_client
    
    async def log_decision(self, agent_id: str, decision: dict):
        """Log agent decisions for analytics"""
        point = {
            "measurement": "agent_decisions",
            "tags": {
                "agent_id": agent_id,
                "decision_type": decision["type"],
                "candidate_id": decision.get("candidate_id")
            },
            "fields": {
                "score": decision.get("score", 0),
                "confidence": decision.get("confidence", 0),
                "processing_time_ms": decision.get("processing_time", 0)
            },
            "time": datetime.utcnow()
        }
        await self.influx.write_point(point)
```

## Agent-Specific Storage Patterns

### 1. Screening Agent Storage

```python
class ScreeningAgentStorage:
    """Storage optimized for document processing"""
    
    async def process_document(self, doc_url: str):
        # Stream directly to memory
        async with aiohttp.ClientSession() as session:
            async with session.get(doc_url) as resp:
                content = await resp.read()
        
        # Process in memory
        images = convert_pdf_to_images_in_memory(content)
        
        # Share results via Redis
        await self.context_store.share_context(
            f"candidate:{candidate_id}:analysis",
            analysis_results,
            ttl=7200  # 2 hours
        )
        
        # Archive if needed
        if self.config.archive_documents:
            await self.object_store.store_permanent(
                candidate_id, "resume", content
            )
```

### 2. Hiring Manager Agent Storage

```python
class HiringManagerAgentStorage:
    """Storage for communication and decisions"""
    
    async def store_interaction(self, interaction: dict):
        # Quick access via Redis
        await self.redis.lpush(
            f"manager:{manager_id}:pending",
            json.dumps(interaction)
        )
        
        # Audit trail
        await self.audit_log.log_decision({
            "type": "manager_notification",
            "manager_id": manager_id,
            "candidate_id": interaction["candidate_id"]
        })
```

### 3. Analytics Agent Storage

```python
class AnalyticsAgentStorage:
    """Optimized for metrics and reporting"""
    
    def __init__(self):
        self.metrics_buffer = []
        
    async def collect_metrics(self):
        # Batch write to time-series DB
        if len(self.metrics_buffer) >= 100:
            await self.influx.write_points(self.metrics_buffer)
            self.metrics_buffer = []
```

## Storage Architecture Patterns

### Pattern 1: Event Sourcing
```
Agent Action → Event Store → Event Processor → State Update
                    ↓
              Audit Trail
```

### Pattern 2: CQRS for Agents
```
Write Model (Redis)          Read Model (PostgreSQL)
     ↓                              ↑
Agent Updates ──────────────→ Materialized Views
```

### Pattern 3: Memory-First Processing
```
Document → Memory Buffer → AI Processing → Results
              ↓                               ↓
       (Optional Archive)              Shared Context
```

## Deployment Configurations

### Development Environment
```yaml
services:
  redis:
    image: redis:7-alpine
    volumes:
      - ./data/redis:/data
  
  localstack:
    image: localstack/localstack
    environment:
      - SERVICES=s3
  
  postgres:
    image: timescale/timescaledb:latest-pg15
    volumes:
      - ./data/postgres:/var/lib/postgresql/data
```

### Production Environment
```yaml
# AWS Example
storage:
  context_store:
    type: elasticache_redis
    cluster_mode: enabled
    node_type: cache.r6g.large
    
  object_store:
    type: s3
    bucket: recruitment-prod
    lifecycle_rules:
      - prefix: temp/
        expiration_days: 1
      - prefix: candidates/
        transition_to_glacier: 90
        
  metrics_store:
    type: timestream
    retention:
      memory: 24_hours
      magnetic: 30_days
```

## Cost Optimization

### Storage Tiers by Data Type

| Data Type | Storage | Retention | Cost/GB/Month |
|-----------|---------|-----------|---------------|
| Active Context | Redis | 24 hours | $0.096 |
| Processing Temp | Memory | 1 hour | $0.00 |
| Documents | S3 IA | 90 days | $0.0125 |
| Audit Logs | S3 Glacier | 7 years | $0.004 |
| Metrics | TimeStream | 30 days | $0.036 |

### Optimization Strategies

1. **Aggressive TTLs**: Set short expiration for temporary data
2. **Compression**: Compress documents before storage
3. **Tiering**: Move old data to cheaper storage automatically
4. **Caching**: Use Redis for frequently accessed data

## Security Considerations

### Encryption
```python
# All data encrypted at rest and in transit
class SecureStorage:
    def encrypt_pii(self, data: dict) -> bytes:
        """Encrypt PII before storage"""
        return self.kms.encrypt(
            json.dumps(data),
            key_id=self.pii_key_id
        )
```

### Access Control
```yaml
# IAM policies for agents
screening_agent_role:
  - s3:GetObject on temp/*
  - s3:PutObject on candidates/*/analysis/*
  - redis:read/write on agent:context:*

hiring_manager_agent_role:
  - s3:GetObject on candidates/*/summary/*
  - redis:read on agent:context:*
  - redis:write on manager:feedback:*
```

### Compliance
- PII isolation in separate encrypted stores
- Audit logs immutable and retained per regulations
- Right to deletion implemented via tombstones
- Geographic restrictions for data residency

## Migration from Legacy Storage

### Phase 1: Parallel Running
```python
# Adapter pattern for gradual migration
class StorageAdapter:
    async def store(self, key: str, value: dict):
        # Write to both systems
        await self.legacy_store.save(key, value)
        await self.new_store.share_context(key, value)
```

### Phase 2: Read Migration
- New agents read from new storage
- Legacy systems continue writing to both

### Phase 3: Write Migration
- Switch writes to new storage only
- Keep legacy as read-only backup

### Phase 4: Decommission
- Archive legacy data
- Remove legacy storage systems

## Monitoring and Alerts

### Key Metrics
```yaml
alerts:
  - name: redis_memory_usage
    threshold: 80%
    action: scale_up
    
  - name: s3_request_errors
    threshold: 1%
    action: page_oncall
    
  - name: context_ttl_misses
    threshold: 5%
    action: investigate_patterns
```

### Dashboard Views
1. Agent context sharing rates
2. Document processing latency
3. Storage cost by service
4. Cache hit rates
5. Audit log ingestion rate

## Best Practices

1. **Never store PII in Redis** - Use references only
2. **Stream large files** - Don't load entirely into memory
3. **Use presigned URLs** - For direct S3 access
4. **Implement circuit breakers** - For storage failures
5. **Regular backup tests** - Ensure recovery works
6. **Monitor costs** - Set up billing alerts
7. **Clean up regularly** - Automated cleanup jobs

This multi-agent storage architecture provides the performance, scalability, and reliability needed for enterprise recruitment workflows while maintaining security and compliance requirements.