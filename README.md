# Recruitment Operations System

AI-powered recruitment analysis system using Claude Opus 4 vision analysis and dynamic formatting for comprehensive candidate assessment.

## Quick Start

```bash
# Process a candidate
python3 process.py <candidate_id>

# Run quick test
./test.sh

# View documentation
cat docs/QUICK_REFERENCE.md
```

## Features

- **Claude Opus 4 Vision Analysis**: Extracts all questionnaire data (84+ responses) from Dayforce PDFs
- **Dynamic AI Formatting**: Adapts summaries based on job requirements
- **Comprehensive Data Extraction**: Equipment, certifications, experience, preferences
- **CATS Integration**: Seamless integration with CATS ATS
- **Professional Email Summaries**: Hiring manager-ready candidate overviews

## Project Structure

```
recruitment_ops/
├── process.py              # Entry point for processing
├── test.sh                 # Quick test script
├── scripts/                # All executable scripts
│   ├── process_candidate.py
│   ├── status_webhook.py
│   ├── run_tests.py
│   ├── check_notes.py
│   └── check_and_process.py
├── catsone/                # Core system modules
│   ├── processors/         # AI and processing logic
│   └── integration/        # CATS API integration
├── docs/                   # Documentation
│   ├── QUICK_REFERENCE.md
│   └── PROCESSING_GUIDE.md
├── logs/                   # All logs stored here
└── tests/                  # Test suites
```

## Setup

1. Clone the repository
2. Create virtual environment: `python3 -m venv venv`
3. Activate: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Copy `.env.example` to `.env` and add your API keys

## Environment Variables

```bash
ANTHROPIC_API_KEY=your_claude_api_key
CATS_API_KEY=your_cats_api_key
```

## Usage

See `docs/QUICK_REFERENCE.md` for detailed usage instructions.

## License

Proprietary - All rights reserved