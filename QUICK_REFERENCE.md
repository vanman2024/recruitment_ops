# Recruitment Operations - Quick Reference Guide

## 🚀 Essential Commands

### Process a Candidate
```bash
# Process specific candidate (finds job automatically)
python3 process_candidate.py 409281807

# Process candidate for specific job
python3 process_candidate.py 409281807 16612581
```

### Check Results
```bash
# View candidate notes in CATS
python3 scripts/check_notes.py

# Check all candidates with "Questionnaire Completed" tag
python3 scripts/check_and_process.py
```

### Run Tests
```bash
# Run comprehensive test suite
python3 run_tests.py

# Check logs
ls -la logs/
```

### Start Webhook (for pipeline status changes)
```bash
python3 status_webhook.py
```

## 📁 Project Structure

```
recruitment_ops/
├── process_candidate.py      # Main processing script
├── status_webhook.py         # Webhook for pipeline changes
├── run_tests.py             # Comprehensive test suite
├── scripts/                 # Utility scripts
│   ├── check_notes.py       # View candidate notes
│   ├── check_and_process.py # Batch processing
│   └── check_workflow_statuses.py
├── catsone/                 # Core system
│   ├── processors/          # AI and processing logic
│   │   ├── ai_notes_formatter.py      # Dynamic AI formatting
│   │   ├── claude_vision_analyzer.py  # Claude Opus 4 vision
│   │   └── intelligent_candidate_processor.py
│   └── integration/         # CATS API integration
├── logs/                    # All logs stored here
└── tests/                   # Test files
```

## 🔑 Key Features

1. **Claude Opus 4 Vision Analysis**
   - Extracts ALL questionnaire data (84+ responses)
   - Handles Dayforce PDFs with checkboxes and radio buttons
   - 4x resolution enhancement for better accuracy

2. **Dynamic AI Formatting**
   - Adapts to specific job requirements
   - Creates professional email-style summaries
   - Never makes up information

3. **Comprehensive Data Extraction**
   - Equipment experience and brands
   - All certifications (Red Seal, safety, etc.)
   - Work preferences and availability
   - Years of experience by category

## 🛠️ Common Tasks

### Finding Candidate IDs
```python
# In Python
from catsone.integration.cats_integration import CATSClient
client = CATSClient()
candidates = client.search_candidates_by_tag("Questionnaire Completed")
for c in candidates:
    print(f"{c['name']}: {c['id']}")
```

### Debugging
- Check logs in `logs/` directory
- Use `run_tests.py` to verify system health
- API keys must be in `.env` file

### Environment Variables (.env)
```
ANTHROPIC_API_KEY=sk-ant-api03-...
CATS_API_KEY=23ff55bbce3778ac88d7...
```

## 📊 Test Candidate IDs

- Craig Strucke: 409281807
- Other test candidates: Run `python3 scripts/check_and_process.py` to find more

## 🔧 Troubleshooting

1. **API Key Issues**: Check `.env` file exists and has valid keys
2. **No Questionnaire Found**: Verify candidate has "Recruiting - Dayforce.pdf" attachment
3. **Processing Timeout**: Claude Opus 4 can take 60-90 seconds for large PDFs
4. **Notes Not Updating**: Check CATS API permissions

## 📝 Notes

- Manual processing is recommended (CATS doesn't webhook on tag changes)
- System uses Claude Opus 4 with Sonnet fallback
- All dates/times must come from questionnaire data (no made-up info)
- Locations = where they're willing to work, not relocate