# Recruitment Operations System

AI-powered recruitment analysis system that integrates with CATS ATS to provide intelligent candidate assessment, job matching, and automated processing.

## Features

- **Vision-Based Questionnaire Analysis**: Uses Gemini Vision API to extract checkbox selections from PDF questionnaires
- **Comprehensive Equipment Tracking**: Extracts and analyzes equipment experience, brands, and gaps
- **AI-Powered Job Matching**: Matches candidates against job requirements using Gemini AI
- **Resume Analysis**: Extracts and analyzes resume content for skills and experience
- **CATS Integration**: Seamless integration with CATS ATS for candidate management
- **Slack Notifications**: Real-time notifications for recruitment team
- **Manual Processing**: Controlled processing workflow for Canadian candidates

## System Architecture

```
CATS ATS → Webhook → Processor → AI Analysis → Results
              ↓                       ↓
         Manual Trigger          Equipment Gap Analysis
              ↓                       ↓
        Canadian Filter          Smart Matching → CATS Notes
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/vanman2024/recruitment_ops.git
cd recruitment_ops
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys:
# - CATS_API_KEY
# - CATS_API_URL
# - GEMINI_API_KEY
# - SLACK_WEBHOOK_URL
```

## Usage

### Manual Candidate Processing

Process a specific candidate:
```python
from catsone.processors.integrated_candidate_analyzer import IntegratedCandidateAnalyzer

analyzer = IntegratedCandidateAnalyzer()
result = analyzer.analyze_candidate(
    candidate_id=399702647,
    job_id=16612581  # Optional: for job matching
)
```

### Webhook Server

Start the webhook server to receive CATS events:
```bash
python catsone/utils/webhook_server_fastapi.py
```

For local development with ngrok:
```bash
./ngrok http 8000
```

## Key Components

### Processors
- `vision_questionnaire_analyzer.py` - Analyzes questionnaire images using vision AI
- `integrated_candidate_analyzer.py` - Complete analysis pipeline
- `resume_downloader.py` - Downloads and extracts resume content
- `gemini_helper.py` - AI analysis using Google Gemini

### Integration
- `cats_integration.py` - CATS API client
- `simple_slack_webhook.py` - Slack notifications
- `webhook_server_fastapi.py` - FastAPI webhook endpoint

### Utilities
- `candidate_matcher.py` - Candidate matching with accent handling
- `batch_processor.py` - Batch processing capabilities

## Equipment Analysis

The system now provides comprehensive equipment analysis:
- Extracts ALL available equipment options from questionnaires
- Identifies selected vs. non-selected brands
- Highlights gaps in required equipment experience
- Provides detailed CATS notes with equipment focus

Example output:
```
EQUIPMENT BRANDS - QUESTIONNAIRE RESPONSES:
Underground Machinery Brands Question:
  Options: Sandvik, Epiroc, Komatsu, Normet, Liebherr, Joy Global
  SELECTED: None of the above ❌
  
Specific Equipment:
  • Komatsu PC 5000 experience: NO ❌
```

## Testing

Run tests:
```bash
python -m pytest tests/
```

Individual test examples are in the `tests/` directory.

## Development

See `SYSTEM_DESIGN.md` for detailed system architecture and workflow.

See `CLAUDE.md` for AI assistant instructions and project context.

## License

Proprietary - All rights reserved