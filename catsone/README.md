# CatsOne ATS Integration

This directory contains the CatsOne Applicant Tracking System (ATS) integration for automated recruitment processing.

## Overview

The CatsOne integration provides automated candidate processing capabilities including:
- PDF resume and questionnaire parsing using Gemini AI
- Intelligent job matching based on skills and experience
- Automated candidate creation and pipeline management
- Webhook support for real-time processing
- Slack notifications for hiring managers

## Directory Structure

```
catsone/
├── integration/        # Core CATS API integration
│   └── cats_integration.py
├── processors/         # Document processing modules
│   ├── process_candidate.py
│   ├── gemini_helper.py
│   ├── batch_processor.py
│   └── intelligent_job_matcher.py
├── utils/             # Utility modules
│   ├── slack_notifier.py
│   └── webhook_server.py
├── prompts/           # AI prompts for document analysis
│   └── questionnaire_analyzer.txt
├── docs/              # Documentation
│   ├── README.md (original)
│   ├── RECRUITMENT_MCP_SUITE_PROPOSAL.md
│   ├── WEBHOOK_SETUP_GUIDE.md
│   ├── STORAGE_OPTIONS.md
│   └── MCP_HTTP_WORKFLOW.md
└── config.py          # Configuration settings
```

## Key Features

### 1. Document Processing
- Converts PDF resumes and questionnaires to images for accurate analysis
- Uses Gemini AI to extract structured data from documents
- Identifies checked boxes, filled fields, and relevant information
- Merges multi-page documents into comprehensive candidate profiles

### 2. CATS API Integration
- Full integration with CATS v3 API
- Candidate creation and management
- Job order retrieval and matching
- Pipeline status updates
- Activity logging

### 3. Intelligent Job Matching
- Scores candidates against job requirements
- Matches based on:
  - Equipment brands and experience
  - Years of experience
  - Certifications and licenses
  - Skills and qualifications

### 4. Automation Features
- Webhook server for real-time document processing
- Batch processing for multiple candidates
- Slack notifications for hiring managers
- Automated email generation

## Setup

1. Create a `.env` file with required API keys:
```env
GEMINI_API_KEY=your_gemini_api_key
CATS_API_KEY=your_cats_api_key
CATS_COMPANY_ID=your_company_id
SLACK_WEBHOOK_URL=your_slack_webhook_url
```

2. Install dependencies:
```bash
pip install PyMuPDF python-dotenv requests
```

## Usage

### Process a Single Candidate
```python
from processors.process_candidate import process_candidate_documents

result = process_candidate_documents(
    resume_path="path/to/resume.pdf",
    questionnaire_path="path/to/questionnaire.pdf",
    candidate_name="John Doe"
)
```

### Batch Processing
```python
from processors.batch_processor import BatchProcessor

processor = BatchProcessor()
processor.process_folder("path/to/candidate/documents")
```

### Job Matching
```python
from processors.intelligent_job_matcher import match_candidate_to_jobs

matches = match_candidate_to_jobs(candidate_data)
```

## Integration with MCP

This system is designed to work with MCP (Model Control Protocol) for enhanced AI capabilities. The Gemini helper module provides MCP-compatible interfaces for document analysis.

## Architecture Approaches

### Multi-Agent MCP Architecture (Recommended)
See [MCP Multi-Agent Recruitment](docs/MCP_MULTI_AGENT_RECRUITMENT.md) for the recommended approach using specialized agents that communicate through MCP, similar to modern AI agent architectures.

### Traditional Webhook Approach
See [MCP HTTP Workflow](docs/MCP_HTTP_WORKFLOW.md) for the webhook-based integration approach.

## See Also

- [Original Documentation](docs/README.md)
- [MCP Suite Proposal](docs/RECRUITMENT_MCP_SUITE_PROPOSAL.md)
- [Webhook Setup Guide](docs/WEBHOOK_SETUP_GUIDE.md)
- [Storage Options](docs/STORAGE_OPTIONS.md)