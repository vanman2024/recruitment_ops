---
allowed-tools: Bash(git:*), Read, TodoWrite, mcp__github-http__list_commits, mcp__supabase-v3__select_data
description: Rollback changes to a previous state or commit
---

## Context
- Current branch: !`git branch --show-current`
- Git status: !`git status --short`
- Recent commits: !`git log --oneline -5`

## Claude Prompt:
```
I need to rollback changes. I will:
1. Identify what needs to be rolled back
2. Choose appropriate rollback strategy
3. Preserve any important work
4. Update todos and database accordingly
```

## Your task

Rollback to state specified by $ARGUMENTS (commit hash, "last", or "clean"):

### Option 1: Rollback to specific commit
```bash
# If $ARGUMENTS is a commit hash
git log --oneline -10  # Show recent commits
git reset --hard $ARGUMENTS  # Hard reset to that commit
```

### Option 2: Rollback uncommitted changes
```bash
# If $ARGUMENTS is "clean"
git status --short
git checkout -- .  # Discard all changes
git clean -fd      # Remove untracked files
```

### Option 3: Rollback last commit (keep changes)
```bash
# If $ARGUMENTS is "last"
git reset --soft HEAD~1  # Undo last commit but keep changes
```

### Option 4: Selective rollback
```bash
# For specific files
git checkout -- path/to/file
# Or restore from a commit
git checkout $COMMIT_HASH -- path/to/file
```

## MCP Integration:
1. **Check commit history**:
   - Use `mcp__github-http__list_commits` to see remote commits
   
2. **Update database if needed**:
   - Use `mcp__supabase-v3__select_data` to find affected tasks
   - Update task status if rolling back feature work

3. **Create rollback todo**:
   - Document what was rolled back
   - Note any follow-up work needed

## Safety checklist:
- [ ] Important work saved/stashed
- [ ] Rollback target identified correctly
- [ ] Database tasks updated if needed
- [ ] Team notified if shared branch
- [ ] Todos created for any follow-up

## Common rollback scenarios:
- `rollback clean` - Remove all uncommitted changes
- `rollback last` - Undo last commit softly
- `rollback HEAD~3` - Go back 3 commits
- `rollback abc123` - Go to specific commit

Always confirm before hard reset!