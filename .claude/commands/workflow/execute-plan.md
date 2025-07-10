---
allowed-tools: Read, Write, Bash, TodoWrite, mcp__github__create_issue, mcp__github__search_issues, mcp__supabase-v3__insert_data
description: Execute a plan that Claude just created with you
---

# 🎯 Execute Claude's Plan

**Arguments**: $ARGUMENTS

## Capture The Plan

!`echo "$ARGUMENTS" > /tmp/plan-name.txt`
!`PLAN=$(cat /tmp/plan-name.txt); echo "📋 Executing plan: $PLAN"`

## 1. Git Status & Branch Verification

**CRITICAL: Prevent work loss through proper git workflow**

!`echo "🔍 Checking current git status and branch..."`
!`git status --porcelain && echo "✅ Git status clean" || echo "⚠️ Uncommitted changes detected"`
!`git branch --show-current`
!`git log --oneline -3`

### Commit Current Work Before Planning
If uncommitted changes exist, commit them:
!`if [ -n "$(git status --porcelain)" ]; then
    echo "💾 Committing current work before plan execution..."
    git add .
    git commit -m "Work in progress - safe checkpoint before plan: $ARGUMENTS"
    echo "✅ Current work committed"
else
    echo "✅ No uncommitted changes to commit"
fi`

### Create Feature Branch for Plan
!`BRANCH_NAME="feat/plan-$(echo $ARGUMENTS | tr ' ' '-' | tr '[:upper:]' '[:lower:]')-$(date +%Y%m%d)"
echo "🌟 Creating feature branch: $BRANCH_NAME"
git checkout -b "$BRANCH_NAME" || git checkout "$BRANCH_NAME"
echo "✅ Now on branch: $(git branch --show-current)"`

## 2. Save Current Plan

First, let's save the plan we just discussed:

Use **Write** to create:
- File: `.claude/plans/$ARGUMENTS-$(date +%Y%m%d).md`
- Content: The comprehensive plan from our discussion

## 3. Check for Saved Plans

!`ls -la .claude/plans/*.md 2>/dev/null | tail -5 || echo "No saved plans found"`

## 4. Read Recent Plan

If a plan file exists, use **Read**:
- File: `.claude/plans/$ARGUMENTS-*.md` (most recent)

## 5. Extract Action Items

**Think deeply** about the plan we just discussed:
1. What were the key features identified?
2. What was the implementation order?
3. What milestones were defined?
4. What technical decisions were made?

## 6. Create Implementation Todos

Use **TodoWrite** to capture the EXACT plan we discussed:
- Major features from the plan
- Implementation phases
- Technical components
- Testing requirements
- Deployment steps

## 7. Check Existing Issues First

### Search for Related Issues
Use **mcp__github__search_issues**:
- q: "repo:vanman2024/DevLoopAI $ARGUMENTS"

### Check Recently Created
!`gh issue list --repo vanman2024/DevLoopAI --limit 10 --json number,title,createdAt | jq -r '.[] | "#\(.number): \(.title) (created: \(.createdAt))"' | head -10`

### Only Create Missing Issues
Based on our discussed plan:
- If issue exists → Link to it
- If issue missing → Create with **mcp__github__create_issue**
- Record issue numbers for next steps

## 8. Create Database Hierarchy

Use **mcp__supabase-v3__insert_data** to create the hierarchy matching our plan:
- Features discussed
- Milestones identified  
- Phases planned
- Modules designed
- Tasks broken down

## 9. Create UI Component Tasks

For any UI components identified in our plan:

!`echo "🎨 MUI Components to implement from plan:"`
!`echo "- Login form with OAuth buttons (MUI TextField, Button)"`
!`echo "- User dashboard with metrics (MUI Grid, Card, Typography)"`
!`echo "- Settings page with theme toggle (MUI Switch, FormControl)"`

**Note**: This project uses Material-UI (MUI), not V0 components!

Create tasks for each UI component:
- Component name and MUI components to use
- Props interface definition
- State management approach
- Integration with existing theme

## 10. Commit Plan Setup Work

**CRITICAL: Commit plan setup before implementation**

!`echo "💾 Committing plan setup and branch creation..."`
!`git add .claude/plans/
git add .`
!`git commit -m "feat: Setup plan execution for $ARGUMENTS

- Created feature branch for plan implementation
- Saved plan documentation
- Set up todos and database hierarchy
- Prepared GitHub issues for tracking

Plan ready for implementation phase"`
!`echo "✅ Plan setup committed to: $(git branch --show-current)"`

## 11. Link to Original Discussion

!`echo "📝 Plan created from discussion at: $(date)" > .claude/plans/$ARGUMENTS-context.txt`
!`echo "Session: $CLAUDE_SESSION_ID" >> .claude/plans/$ARGUMENTS-context.txt`

## 12. Git Workflow Summary

**Current State Summary**
!`echo "🔍 Plan execution git workflow summary:"`
!`echo "📂 Current branch: $(git branch --show-current)"`
!`echo "📝 Plan saved to: .claude/plans/$ARGUMENTS-$(date +%Y%m%d).md"`
!`echo "🎯 Ready for implementation phase"`

## Next Steps

Now that the plan is captured and properly branched:
- `/project:dev:start [issue]` - Start implementing the plan
- `/project:workflow:continue-plan $ARGUMENTS` - Continue from saved plan
- `/project:workflow:status` - Check plan progress

### When Implementation Complete
!`echo "🚀 When plan implementation is complete:"`
!`echo "1. Commit all implementation work"`
!`echo "2. Switch to master: git checkout master"`
!`echo "3. Merge feature branch: git merge $(git branch --show-current)"`
!`echo "4. Push to origin: git push origin master"`
!`echo "5. Clean up branch: git branch -d $(git branch --show-current)"`

### Emergency Recovery
If you need to recover this plan later:
!`echo "📋 Plan recovery commands:"`
!`echo "git checkout $(git branch --show-current)  # Return to plan branch"`
!`echo "cat .claude/plans/$ARGUMENTS-$(date +%Y%m%d).md  # View saved plan"`
!`echo "TodoRead  # View implementation todos"`

## Cleanup
!`rm -f /tmp/plan-name.txt`

## Important Note

This command CONTINUES from our discussion rather than starting fresh. Use it immediately after planning with Claude to maintain context and proper git workflow!