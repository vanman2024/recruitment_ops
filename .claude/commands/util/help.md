---
allowed-tools: Read, Bash(ls:*)
description: List all available slash commands and their purposes
---

## Available Slash Commands

### 📝 How to Use
Commands use Claude Code format: `/command-name [arguments]`
- File references: Use `@filename` to include file contents
- Bash execution: Use `!command` to run bash and include output
- MCP tools: Commands integrate with MCP servers when available

### 🚀 Development Workflow
- `/dev-start [issue#]` - Start work on issue with branch setup
- `/dev-check-progress` - Check development progress
- `/workflow-manager` - Unified workflow orchestration system

### 🧪 Testing Commands  
- `/test-pre-commit` - Run LOCAL tests before commit
- `/test-complete` - Run ALL tests in order (unit→integration→e2e)
- `/test-unit` - Run unit tests only
- `/test-integration` - Test API endpoints
- `/test-e2e` - Run end-to-end tests
- `/test-validate-pr` - Validate PR requirements

### 🔄 Workflow & Git
- `/git-branch-status` - Show local/remote status
- `/pr-create` - Create PR with validations
- `/pr-complete-flow` - Full PR workflow (test→commit→push→PR)
- `/rollback [target]` - Rollback changes safely

### 🐛 Analysis & Debugging
- `/analyze-complex-issue [issue#]` - Extended thinking for complex issues
- `/debug-issue [description]` - Systematic debugging approach

### 🤖 GitHub Actions
- `/github-actions-status` - Monitor workflows

### 🔮 Synapse Advanced
- `/synapse-init-project [name]` - Initialize Synapse project
- `/synapse-sync-check` - Check GitHub-Database sync
- `/synapse-analyze-issue [issue#]` - AI build plan creation

### ❓ Help Commands
- `/help` - This command
- `/help-testing` - Testing reference
- `/help-venv` - Virtual environment help

## Key Concepts:
1. **Commands prepare for success** - Run tests locally before push
2. **GitHub Actions validate** - Automated checks on push/PR
3. **Commands monitor status** - Track workflow progress
4. **No duplication** - Commands complement, not replace, automation

## Quick Start:
```bash
/dev-start 84        # Start on issue #84
/test-pre-commit     # Test before committing
/pr-create           # Create PR when ready
/github-actions-status  # Monitor CI/CD
```