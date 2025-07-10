---
allowed-tools: Bash(git:*), mcp__github-http__list_branches
description: Check complete branch status - local, remote, and tracking relationships
---

## Claude Prompt:
```
I need to check the complete branch status including:
1. Local branches on this machine
2. Remote branches on GitHub
3. Tracking relationships between local and remote
4. Any unsynced changes
```

## Your task

Show comprehensive branch status:

1. **Local Branches**:
   ```bash
   # Show all LOCAL branches
   git branch -v
   
   # Show which remote each local branch tracks
   git branch -vv
   ```

2. **Remote Branches**:
   ```bash
   # Show all REMOTE branches
   git branch -r
   
   # Fetch latest remote branch info
   git fetch --all
   ```

3. **Compare Local vs Remote**:
   ```bash
   # Show ALL branches (local + remote)
   git branch -a
   
   # Check if current branch exists on remote
   git ls-remote --heads origin $(git branch --show-current)
   ```

4. **Tracking Status**:
   ```bash
   # Show tracking info for current branch
   git status -sb
   
   # Show commits ahead/behind for all branches
   git for-each-ref --format='%(refname:short) %(upstream:track)' refs/heads
   ```

5. **Unsynced Changes**:
   ```bash
   # Check unpushed commits on current branch
   git log origin/$(git branch --show-current)..HEAD --oneline
   
   # Check unpulled commits
   git log HEAD..origin/$(git branch --show-current) --oneline
   ```

## MCP Integration:
- Use `mcp__github-http__list_branches` to verify remote branches

## Understanding the Output:
- **Local only**: Branch exists only on your machine
- **Remote only**: Branch exists on GitHub but not locally  
- **[ahead 2]**: You have 2 commits not pushed to remote
- **[behind 3]**: Remote has 3 commits you haven't pulled
- **[gone]**: Remote branch was deleted

## Common Actions:
- Push local to remote: `git push -u origin branch-name`
- Pull remote to local: `git checkout -b branch-name origin/branch-name`
- Delete local: `git branch -d branch-name`
- Delete remote: `git push origin --delete branch-name`