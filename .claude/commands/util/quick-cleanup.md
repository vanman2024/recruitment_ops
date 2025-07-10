---
allowed-tools: Bash(*), Glob(*), TodoWrite(*)
description: Quick cleanup for common temporary files
---

## Context
- Current directory: !`pwd`
- Git status: !`git status --short 2>/dev/null || echo "Not a git repo"`

## Your task

Perform a quick cleanup of common temporary files:

1. Find and remove (with confirmation):
   - Python: `__pycache__`, `.pyc`, `.pytest_cache`
   - System: `.DS_Store`, `Thumbs.db`
   - Editor: `*.swp`, `*~`, `.*.swp`

2. Report but don't delete:
   - Log files older than 7 days
   - Backup files (`*.bak`, `*.backup`)
   - Large files (>50MB)

Arguments: $ARGUMENTS

Always ask for confirmation before deleting anything!