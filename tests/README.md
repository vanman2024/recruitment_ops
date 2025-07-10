# Recruitment Ops Tests

This directory contains test scripts and utilities for the recruitment operations system.

## Test Files

### API Exploration
- `cats_api_explorer.py` - Explores CATS API endpoints and attachment handling
- `search_all_candidates.py` - Tests candidate search functionality
- `find_gaetan_id.py` - Specific candidate lookup tests

### Integration Tests  
- `test_webhook_server.py` - Tests webhook server functionality
- `test_manual_processing.py` - Tests manual candidate processing endpoints
- `manual_notes_test.py` - Tests CATS notes update functionality

### Analysis Tests
- `job_match_analysis.py` - Tests job matching algorithms
- `resume_job_match.py` - Tests resume parsing and job matching

## Running Tests

```bash
# Run individual test
python tests/test_webhook_server.py

# Run all tests (when pytest is configured)
pytest tests/
```

## Test Data

Test output files (*.txt, *.json) are stored in this directory and ignored by git.