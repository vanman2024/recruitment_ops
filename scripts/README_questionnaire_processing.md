# Questionnaire Processing Scripts

## Overview
These scripts handle processing candidates who have completed questionnaires in CATS.

## Scripts

### 1. questionnaire_monitor.py
Monitors for candidates with "Questionnaire Completed" tag and processes them automatically.

**Usage:**
```bash
# Run continuous monitoring (checks every 5 minutes)
python3 scripts/questionnaire_monitor.py

# Run once
python3 scripts/questionnaire_monitor.py --once

# Custom interval (e.g., every 60 seconds)
python3 scripts/questionnaire_monitor.py --interval 60
```

**Features:**
- Checks recent candidates (updated in last 48 hours)
- Looks for "Questionnaire Completed" tag
- Processes candidates and generates AI notes
- Adds "ai_notes_generated" tag when complete
- Maintains cache to avoid reprocessing

### 2. process_specific_candidate.py
Process a specific candidate by ID (useful for older candidates).

**Usage:**
```bash
python3 scripts/process_specific_candidate.py <candidate_id>

# Example:
python3 scripts/process_specific_candidate.py 409284264
```

**Features:**
- Checks if candidate has "Questionnaire Completed" tag
- Processes and generates AI notes
- Adds "ai_notes_generated" tag when complete

### 3. start_questionnaire_monitor.sh
Starts the monitor as a background process.

**Usage:**
```bash
./scripts/start_questionnaire_monitor.sh
```

## Important Notes

1. **Tag Names Must Match Exactly:**
   - Looking for: "Questionnaire Completed"
   - Adds when done: "ai_notes_generated"

2. **Only Recent Candidates:**
   - Monitor only checks candidates updated in last 48 hours
   - For older candidates, use process_specific_candidate.py

3. **Rate Limits:**
   - Scripts include delays to avoid API rate limits
   - Don't run multiple instances simultaneously

## Logs
- Monitor logs: `/home/gotime2022/recruitment_ops/logs/questionnaire_monitor.log`
- Live output: `/home/gotime2022/recruitment_ops/logs/questionnaire_monitor_live.log`
- Processed cache: `/home/gotime2022/recruitment_ops/logs/processed_candidates.json`