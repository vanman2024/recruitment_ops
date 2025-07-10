# 🔄 DevLoopAI Workflow Commands

## Core Development Flow

The slash commands support this development workflow:

```
1. Context Recovery → 2. Issue Analysis → 3. Development → 
4. Testing → 5. PR Creation → 6. Deployment
```

## Essential Commands

### 1. Context & Recovery
- `/project:context:restore-ultra [focus]` - Restore current work context
- `/project:context:big-picture` - Understand overall vision
- `/project:context:health` - System health check

### 2. Issue Management  
- `/project:issue:analyze [number]` - Deep issue analysis
- `/project:issue:create [title]` - Create new issue

### 3. Development
- `/project:dev:start [issue]` - Start development on issue
- `/project:dev:progress` - Check development progress
- `/project:workflow:complete [issue]` - Full autonomous workflow

### 4. Testing
- `/project:test:complete` - Run full test suite
- `/project:test:run [type]` - Run specific tests

### 5. Pull Requests
- `/project:pr:create` - Create PR with context
- `/project:pr:complete` - Complete PR workflow

### 6. Deployment
- `/project:deploy:prepare` - Prepare deployment
- `/project:deploy:execute` - Execute deployment

### 7. Utilities
- `/project:cleanup` - Quick cleanup
- `/project:help` - Get help

## Workflow Examples

### Start New Feature
```bash
/project:context:restore-ultra
/project:issue:create "Add user authentication"
/project:dev:start 123
/project:test:complete
/project:pr:create
```

### Fix Bug
```bash
/project:issue:analyze 456
/project:dev:start 456
/project:test:run unit
/project:pr:create
```

### Complete Autonomous Flow
```bash
/project:workflow:complete 789
# This runs the entire workflow automatically
```

## Command Chaining

Commands are designed to flow into each other:
- Context commands → Issue commands
- Issue commands → Dev commands  
- Dev commands → Test commands
- Test commands → PR commands
- PR commands → Deploy commands

Each command provides "Next Steps" suggestions for natural workflow progression.