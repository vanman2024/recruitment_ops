# Recruitment Operations Processing Guide

## Overview
This system processes candidate questionnaires using Claude 4 Opus vision analysis and AI-powered formatting to extract comprehensive information from Dayforce questionnaires.

## Processing Methods

### 1. Manual Processing (Recommended)
Since CATS doesn't trigger webhooks for tag changes, use manual processing:

```bash
source venv/bin/activate
python3 process_candidate.py <candidate_id> [job_id]
```

Example:
```bash
python3 process_candidate.py 409281807
```

### 2. Batch Processing
Check for all candidates with "Questionnaire Completed" tag:

```bash
python3 check_and_process.py
```

### 3. Webhook Processing (Pipeline Status Changes)
The system has a webhook configured for pipeline status changes:
- Endpoint: `https://cats.ngrok.app/webhook/pipeline`
- Triggers on: "Hiring Manager Approved" or "Submitted to Hiring Manager" status changes

Start webhook:
```bash
source venv/bin/activate
python3 status_webhook.py
```

## AI Models Used

1. **Claude 4 Opus (claude-opus-4-20250514)**
   - Primary model for vision analysis
   - Primary model for notes formatting
   - Best accuracy for checkbox/radio button detection

2. **Claude 4 Sonnet (claude-sonnet-4-20250514)**
   - Fallback model if Opus is unavailable

## What Gets Extracted

The system extracts and formats:
- Personal and contact details
- All certifications (Red Seal, safety certs, licenses)
- Years of experience by category
- All equipment brands and models worked with
- Work preferences (shifts, camp work, travel)
- Availability and employment status
- Additional qualifications and preferences

## Troubleshooting

### If processing fails:
1. Check API keys in `.env` file
2. Ensure virtual environment is activated
3. Check logs for specific errors
4. Verify candidate has questionnaire attachment

### Common Issues:
- **"No module named 'anthropic'"**: Run `pip install anthropic`
- **API authentication errors**: Check ANTHROPIC_API_KEY in .env
- **No job ID found**: Specify job ID manually as second parameter

## Environment Variables Required

In `.env` file:
```
ANTHROPIC_API_KEY=sk-ant-api03-...
CATS_API_KEY=23ff55bbce3778ac88d7...
```

## Key Files

- `process_candidate.py` - Manual processing script
- `check_and_process.py` - Batch processing for tagged candidates
- `status_webhook.py` - Webhook handler for pipeline status changes
- `catsone/processors/ai_notes_formatter.py` - AI-powered formatting
- `catsone/processors/claude_vision_analyzer.py` - Vision analysis

## Notes Update Format

The system creates comprehensive notes with 7 sections:
1. Personal and Contact Details
2. Licenses, Certifications, and Related Qualifications
3. Specialized Skills and Expertise
4. Familiarity with Specific Tools, Brands, or Technologies
5. Experience in Specific Roles or Environments
6. Current Employment and Transition Reasons
7. Additional Important Information

All 84+ questionnaire responses are organized into these sections for easy recruiter review.