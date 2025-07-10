# MCP Multi-Agent Recruitment Architecture

## Overview

This document describes a multi-agent MCP architecture for recruitment, inspired by the travel booking multi-agent system. Instead of a traditional webhook approach, we use specialized agents that communicate through MCP to handle different aspects of the recruitment process.

## Architecture

```
                           LLM (GPT)
                             ↑
                             |
    ┌────────────────────────┴────────────────────────┐
    |                                                  |
    ↓                                                  ↓
┌─────────────────┐                          ┌─────────────────┐
│                 │     Model Context         │                 │
│  Candidate      │     Protocol (MCP)       │   Hiring        │
│  Screening      │ ←──────────────────────→ │   Manager       │
│  Agent          │                          │   Agent         │
│                 │                          │                 │
└────────┬────────┘                          └────────┬────────┘
         |                                            |
    ┌────┴────┬────────┬────────┐           ┌────────┴────┬────────┬────────┐
    ↓         ↓        ↓        ↓           ↓             ↓        ↓        ↓
 ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐   ┌──────────┐ ┌──────┐ ┌──────┐ ┌──────┐
 │CATS  │ │Gemini│ │Resume│ │Quest-│   │  Slack   │ │Email │ │Teams │ │Calendar│
 │ATS   │ │AI    │ │Parser│ │ionnaire│ │Messaging│ │System│ │Chat  │ │System │
 └──────┘ └──────┘ └──────┘ └──────┘   └──────────┘ └──────┘ └──────┘ └──────┘
```

## Agent Descriptions

### 1. Candidate Screening Agent

**Purpose**: Handles initial candidate processing and evaluation

**Capabilities**:
- Process incoming resumes and questionnaires
- Extract structured data from documents
- Score candidates against job requirements
- Make initial screening decisions

**MCP Tools**:
```json
{
  "name": "candidate-screening-agent",
  "tools": [
    {
      "name": "analyze_candidate",
      "description": "Analyze resume and questionnaire data",
      "parameters": {
        "resume_path": "string",
        "questionnaire_path": "string",
        "job_requirements": "object"
      }
    },
    {
      "name": "score_candidate",
      "description": "Score candidate against job requirements",
      "parameters": {
        "candidate_data": "object",
        "job_id": "string"
      }
    },
    {
      "name": "create_candidate_summary",
      "description": "Create detailed candidate summary for review",
      "parameters": {
        "candidate_id": "string",
        "include_recommendations": "boolean"
      }
    }
  ]
}
```

**Connected Services**:
- CATS ATS (candidate management)
- Gemini AI (document analysis)
- Resume Parser (structured extraction)
- Questionnaire Processor (checkbox detection)

### 2. Hiring Manager Agent

**Purpose**: Facilitates communication with hiring managers and decision-making

**Capabilities**:
- Present candidate summaries to hiring managers
- Collect feedback and approval decisions
- Schedule interviews
- Send notifications

**MCP Tools**:
```json
{
  "name": "hiring-manager-agent",
  "tools": [
    {
      "name": "send_candidate_for_review",
      "description": "Send candidate summary to hiring manager",
      "parameters": {
        "candidate_summary": "object",
        "manager_id": "string",
        "notification_channel": "string"
      }
    },
    {
      "name": "collect_feedback",
      "description": "Collect and process hiring manager feedback",
      "parameters": {
        "candidate_id": "string",
        "feedback": "object"
      }
    },
    {
      "name": "schedule_interview",
      "description": "Schedule interview with candidate",
      "parameters": {
        "candidate_id": "string",
        "manager_availability": "array",
        "interview_type": "string"
      }
    }
  ]
}
```

**Connected Services**:
- Slack (notifications and approvals)
- Email System (formal communications)
- Teams Chat (alternative messaging)
- Calendar System (interview scheduling)

## Agent Communication Flow

### Shared Context Through MCP

The agents share context and preferences through MCP, similar to the travel booking example:

```python
# Candidate Preferences (shared between agents)
candidate_context = {
    "requirements": {
        "equipment_brands": ["CAT", "Komatsu"],
        "min_experience": 5,
        "certifications": ["Red Seal", "Class 1"],
        "location_preference": "Remote sites OK"
    },
    "evaluation_criteria": {
        "technical_weight": 0.4,
        "experience_weight": 0.3,
        "cultural_fit_weight": 0.3
    },
    "workflow_preferences": {
        "auto_approve_score": 85,
        "manager_review_score": 70,
        "auto_reject_score": 50
    }
}
```

### Example Workflow

1. **Candidate Submission**
   ```python
   # Screening Agent receives new candidate
   screening_agent.analyze_candidate({
       "resume": "path/to/resume.pdf",
       "questionnaire": "path/to/questionnaire.pdf",
       "job_id": "JOB123"
   })
   ```

2. **Agent Communication**
   ```python
   # Screening Agent shares analysis with Hiring Manager Agent
   mcp.share_context({
       "candidate_id": "CAND456",
       "analysis": {
           "score": 82,
           "matching_skills": ["CAT", "Mining", "10+ years"],
           "missing_skills": ["Komatsu certification"],
           "recommendation": "Strong candidate - recommend manager review"
       }
   })
   ```

3. **Hiring Manager Notification**
   ```python
   # Hiring Manager Agent creates interactive review
   hiring_manager_agent.send_candidate_for_review({
       "candidate_summary": screening_results,
       "manager_id": "MGR789",
       "notification_channel": "slack"
   })
   ```

4. **Decision Making**
   ```python
   # Goal-driven behavior based on manager preferences
   if screening_score >= workflow_preferences["auto_approve_score"]:
       hiring_manager_agent.auto_approve_candidate()
   elif screening_score >= workflow_preferences["manager_review_score"]:
       hiring_manager_agent.request_manager_review()
   else:
       screening_agent.send_rejection_notice()
   ```

## Implementation Benefits

### 1. Autonomous Operation
- Agents can make decisions based on predefined criteria
- Reduces manual intervention for routine cases
- Escalates only when necessary

### 2. Parallel Processing
- Screening Agent can process multiple candidates simultaneously
- Hiring Manager Agent can handle multiple manager interactions
- No bottlenecks in the system

### 3. Flexible Integration
- Easy to add new services (e.g., background check systems)
- Agents can adapt to different ATS systems
- Support for multiple communication channels

### 4. Intelligent Routing
- Candidates routed to appropriate managers based on job type
- Priority handling for urgent positions
- Load balancing across multiple reviewers

## Technical Implementation

### Agent Framework
```python
from mcp import Agent, Context, Tool

class CandidateScreeningAgent(Agent):
    def __init__(self):
        super().__init__("candidate-screening")
        self.register_tools([
            self.analyze_candidate,
            self.score_candidate,
            self.create_summary
        ])
    
    @Tool()
    async def analyze_candidate(self, resume_path: str, questionnaire_path: str):
        # Use Gemini to analyze documents
        resume_data = await self.mcp.call("gemini", "analyze_document", {
            "path": resume_path,
            "prompt": RESUME_ANALYSIS_PROMPT
        })
        
        questionnaire_data = await self.mcp.call("gemini", "analyze_questionnaire", {
            "path": questionnaire_path,
            "prompt": QUESTIONNAIRE_PROMPT
        })
        
        # Share results with other agents
        await self.mcp.share_context({
            "candidate_analysis": {
                "resume": resume_data,
                "questionnaire": questionnaire_data
            }
        })
        
        return {"status": "analyzed", "data": combined_data}

class HiringManagerAgent(Agent):
    def __init__(self):
        super().__init__("hiring-manager")
        self.register_tools([
            self.send_for_review,
            self.collect_feedback,
            self.schedule_interview
        ])
    
    @Tool()
    async def send_for_review(self, candidate_summary: dict, manager_id: str):
        # Get shared context from screening agent
        context = await self.mcp.get_context("candidate_analysis")
        
        # Create interactive Slack message
        slack_blocks = self.create_approval_blocks(candidate_summary)
        
        result = await self.mcp.call("slack", "post_interactive_message", {
            "channel": self.get_manager_channel(manager_id),
            "blocks": slack_blocks
        })
        
        return {"status": "sent", "message_ts": result["ts"]}
```

## Deployment Architecture

```yaml
# docker-compose.yml
version: '3.8'

services:
  screening-agent:
    image: recruitment/screening-agent
    environment:
      - MCP_SERVER_URL=http://mcp-server:8080
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - CATS_API_KEY=${CATS_API_KEY}
    
  hiring-manager-agent:
    image: recruitment/hiring-manager-agent
    environment:
      - MCP_SERVER_URL=http://mcp-server:8080
      - SLACK_API_TOKEN=${SLACK_API_TOKEN}
      - EMAIL_SMTP_SERVER=${EMAIL_SMTP_SERVER}
    
  mcp-server:
    image: modelcontextprotocol/server
    ports:
      - "8080:8080"
    volumes:
      - ./mcp-config.yaml:/config/mcp-config.yaml
```

## Next Steps

1. **Define Agent Behaviors**
   - Create detailed decision trees for each agent
   - Define escalation criteria
   - Set up preference learning

2. **Implement MCP Tools**
   - Build tool implementations for each agent
   - Create shared context schemas
   - Set up inter-agent communication

3. **Integration Testing**
   - Test agent communication flows
   - Verify decision-making logic
   - Ensure proper error handling

4. **Deploy and Monitor**
   - Set up agent monitoring
   - Track decision metrics
   - Implement feedback loops

This multi-agent approach provides a more scalable and intelligent recruitment system that can adapt to different workflows and requirements while maintaining the flexibility to integrate with various services.