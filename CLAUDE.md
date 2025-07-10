# Project-Specific Claude Instructions - Recruitment Operations System

## 🚨 CRITICAL SECURITY RULE - NEVER HARDCODE API KEYS 🚨
**ABSOLUTELY NO HARDCODED API KEYS OR SECRETS IN ANY FILE, EVER!**
- NEVER put API keys directly in code, even for "testing"
- ALWAYS use environment variables (os.getenv('KEY_NAME') or config files)
- Test files with hardcoded keys MUST NOT be committed
- If you create test files with keys, add them to .gitignore IMMEDIATELY
- Pre-commit hooks will block commits with exposed secrets

**Violation of this rule is a critical security failure.**

## CRITICAL: Todo Management
You MUST use TodoWrite frequently throughout every conversation:
- When user describes any task → Create todo immediately
- When you discover subtasks → Add them immediately  
- When work is completed → Mark completed immediately
- When session might end → Create detailed todos for continuity

## This is NOT optional - it's required for this project.

The user loses work when sessions end abruptly. Todos are the ONLY way to maintain continuity. Create them proactively, not reactively.

## Session Recovery Protocol
When starting a new session or recovering from an abrupt disconnect, IMMEDIATELY execute this sequence:

1. **Check Previous Session Todos**: Find and read the most recent todo file:
   ```bash
   ls -t /home/vanman2024/.claude/todos/*.json | head -5
   # Then read the most recent non-empty one with Read tool
   ```
2. **Check Current Todo List**: Use TodoRead to see current session todos (likely empty)
3. **Check Git Status**: Run `git status` and `git diff` to see any uncommitted changes
4. **Check Recent Files**: Use `ls -lt | head -20` to see recently modified files  
5. **Read Project State**: Check key files for current status
6. **Create Recovery Summary**: Based on the above, create new todos for any incomplete work

### Key Project Files:
- `catsone/config.py` - Central configuration for CATS API and system settings
- `catsone/integration/cats_integration.py` - CATS API client implementation
- `catsone/processors/intelligent_job_matcher.py` - AI-powered job matching logic
- `catsone/processors/gemini_helper.py` - Google Gemini AI integration
- `catsone/processors/batch_processor.py` - Batch processing for candidates
- `catsone/utils/webhook_server.py` - Webhook endpoint for real-time processing
- `catsone/utils/slack_notifier.py` - Slack notification system
- `.env` - Environment variables (NEVER commit this file)

### System Architecture:
```
CATS ATS → Webhook → Processor → AI Matcher → Results
                ↓                    ↓
           Batch Jobs          Gemini Analysis
                ↓                    ↓
          Slack Alerts         Smart Matching
```

### API Integrations:
✅ **CONFIGURED**: 
- **CATS API**: Applicant tracking system integration
- **Google Gemini**: Resume analysis and job matching
- **Slack API**: Team notifications
- **Webhook Server**: Real-time candidate processing

🔧 **REQUIRED SETUP**:
- CATS API credentials in `.env`
- Gemini API key in `.env`
- Slack webhook URL in `.env`

### Environment Variables:
```bash
# Required in .env file
CATS_API_KEY=your_api_key_here
CATS_API_URL=https://api.catsone.com/v3
GEMINI_API_KEY=your_gemini_key_here
SLACK_WEBHOOK_URL=your_slack_webhook_here
```

### Session Recovery Checklist:
When recovering from a crash, check these in order:

```bash
# 1. Check current directory and git status
pwd
git status
git log --oneline -5

# 2. Find previous session todos (CRITICAL)
ls -t /home/vanman2024/.claude/todos/*.json | head -5
# Use Read tool on the most recent non-empty file

# 3. Check current session todos (likely empty)
# Use TodoRead tool

# 4. Check recent file modifications  
ls -lt catsone/ | head -20

# 5. Check system logs
ls -lt logs/ 2>/dev/null | head -10

# 6. Check webhook server status
ps aux | grep webhook_server
```

### Testing Guidelines:
- **Unit Tests**: Run with `pytest tests/`
- **Integration Tests**: Require API credentials
- **Webhook Testing**: Use ngrok for local testing
- **AI Testing**: Mock Gemini responses for consistency

### Common Development Tasks:

#### 1. Adding New Job Matching Criteria:
- Edit `catsone/processors/intelligent_job_matcher.py`
- Update matching algorithms
- Add tests in `tests/test_job_matcher.py`
- Update Gemini prompts if needed

#### 2. Webhook Endpoint Changes:
- Modify `catsone/utils/webhook_server.py`
- Test with curl/Postman locally
- Deploy and update CATS webhook configuration

#### 3. Batch Processing Updates:
- Edit `catsone/processors/batch_processor.py`
- Consider rate limits and API quotas
- Add progress tracking and error recovery

### Code Quality Standards:
- **Python Version**: 3.8+ required
- **Code Style**: Black formatter, isort for imports
- **Type Hints**: Use throughout for better IDE support
- **Docstrings**: Google style for all public functions
- **Error Handling**: Comprehensive try/except with logging

### Security Best Practices:
1. **API Keys**: Environment variables only
2. **PII Handling**: No candidate data in logs
3. **Input Validation**: Sanitize all webhook inputs
4. **Rate Limiting**: Implement for all endpoints
5. **Authentication**: Verify webhook signatures

### Deployment Considerations:
- **Webhook Server**: Needs public URL (use ngrok for dev)
- **Background Jobs**: Consider using Celery for production
- **Database**: SQLite for dev, PostgreSQL for production
- **Monitoring**: Set up alerts for API failures

### Emergency Recovery Commands:
```bash
# If completely lost, run these:
cd /home/vanman2024/recruitment_ops
git status
git branch
ls -la catsone/
cat catsone/config.py | head -20
# Then use TodoRead tool
```

## 🚨 CRITICAL: Git Branch Work Loss Prevention 🚨
**MANDATORY - Prevents work loss**

### Before ANY Branch Switch:
1. **ALWAYS commit current work first**
   ```bash
   git add .
   git commit -m "Work in progress - safe checkpoint"
   ```

2. **ALWAYS ask user about merge strategy**:
   - "Should I merge this work before switching branches?"
   - "Do you want to bring current changes to the target branch?"

### Branch Strategy:
- **Main branch**: `main` - Stable production code
- **Feature branches**: `feature/description` for new features
- **Bugfix branches**: `bugfix/issue-number` for fixes
- **Hotfix branches**: `hotfix/critical-fix` for urgent fixes

### Session End Protocol:
Before any session ends:
1. **Commit all work**: `git add . && git commit -m "Session progress"`
2. **Update todos**: Mark completed items, add new discovered tasks
3. **Document state**: Note any API issues or blockers
4. **Test status**: Run tests if changes were made
5. **RECORD CURRENT BRANCH**: Add branch info to todos

### Performance Optimization Tips:
- **Batch API Calls**: Process candidates in groups
- **Cache Results**: Store job matching scores
- **Async Processing**: Use asyncio for I/O operations
- **Rate Limiting**: Respect API limits to avoid blocks

### Debugging Tools:
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Profile slow code
import cProfile
cProfile.run('your_function()')

# Memory profiling
from memory_profiler import profile
@profile
def your_function():
    pass
```

### Next Steps for Enhancement:
1. Add more sophisticated AI matching algorithms
2. Implement candidate ranking system
3. Add support for multiple ATS systems
4. Build analytics dashboard
5. Create automated testing pipeline
6. Add multi-language resume support

## 🎯 Success Metrics
This system enables:
- **Automated candidate processing** with minimal manual intervention
- **Intelligent job matching** using AI/ML
- **Real-time notifications** for recruitment teams
- **Scalable batch processing** for high volume
- **Comprehensive audit trail** of all activities

This project streamlines recruitment operations through intelligent automation and AI-powered matching.