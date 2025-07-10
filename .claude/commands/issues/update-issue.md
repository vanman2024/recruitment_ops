---
allowed-tools: mcp__github-http__*, mcp__supabase-v4__*, TodoWrite(*), mcp__sequential-thinking-http__sequentialthinking, Bash(*), Read(*), Write(*), Task(*)
description: Update GitHub issue with progress, sync database status, and maintain DevLoop hierarchy
---

# Update Issue Command

## Context Loading
- Current directory: !`pwd`
- Git status: !`git status --porcelain`
- Current branch: !`git branch --show-current`
- Recent commits: !`git log --oneline -5`
- Active PRs: !`gh pr list --repo vanman2024/DevLoopAI --json number,title,state --limit 5`
- Database hierarchy: @/home/gotime2022/devloop3/backend/HIERARCHY_UPDATE_SUMMARY.md
- Issue templates: @.github/ISSUE_TEMPLATE/
- Recent activities: !`git log --since="2 hours ago" --oneline`

## Extended Thinking Trigger
Thinkhard about this step by step:
1. Analyze the current issue state and what needs updating
2. Gather all progress information from various sources
3. Calculate completion percentage across the hierarchy
4. Identify blockers or issues that need attention
5. Determine appropriate label and status updates
6. Plan next steps based on current progress

## Your Task
Update issue $ARGUMENTS[0] with current progress, sync database status, and provide clear next steps.

### GitHub Configuration
- Owner: vanman2024
- Repo: DevLoopAI
- Fallback: gh CLI if MCP tool fails

### Requirements Analysis
Based on $ARGUMENTS:
- Issue Number: $ARGUMENTS[0]
- Update Type: $ARGUMENTS[1] (progress/status/blocked/completed, default: progress)
- Additional Info: $ARGUMENTS[2] (optional message or context)

### Implementation Steps

1. **Parse Issue Information**
   ```javascript
   const issueNum = $ARGUMENTS[0].match(/#?(\d+)/)[1];
   const updateType = $ARGUMENTS[1] || 'progress';
   const context = $ARGUMENTS[2] || '';
   ```

2. **Fetch Current Issue State**
   - Primary: Use mcp__github-http__get_issue with owner="vanman2024" and repo="DevLoopAI"
   - Fallback: If MCP server fails, use GitHub CLI:
     ```bash
     gh issue view --repo vanman2024/DevLoopAI ${issueNum} --json title,body,labels,milestone,assignees,state
     ```
   - Current title, body, labels, milestone
   - Assignees and current status
   - Linked PRs and dependencies

3. **Gather Progress Data from Database**
   Use mcp__supabase-v4__execute_sql with project_id "dkpwdljgnysqzjufjtnk":
   ```sql
   -- Get comprehensive progress for this issue
   WITH issue_tasks AS (
     SELECT 
       t.*,
       m.name as module_name,
       ph.name as phase_name,
       ml.name as milestone_name
     FROM tasks t
     JOIN modules m ON t.module_id = m.id
     JOIN phases ph ON m.phase_id = ph.id
     JOIN milestones ml ON ph.milestone_id = ml.id
     WHERE t.github_issue_number = $1
   )
   SELECT 
     COUNT(*) as total_tasks,
     COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_tasks,
     COUNT(CASE WHEN status = 'in_progress' THEN 1 END) as in_progress_tasks,
     COUNT(CASE WHEN status = 'blocked' THEN 1 END) as blocked_tasks,
     COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_tasks,
     ROUND(COUNT(CASE WHEN status = 'completed' THEN 1 END)::numeric / 
           NULLIF(COUNT(*), 0) * 100, 2) as completion_percentage,
     STRING_AGG(DISTINCT module_name, ', ') as affected_modules,
     STRING_AGG(DISTINCT phase_name, ', ') as phases,
     MAX(milestone_name) as milestone
   FROM issue_tasks;
   ```

4. **Gather Git Activity**
   ```bash
   # Recent commits for this issue
   COMMITS=$(git log --grep="#${issueNum}" --oneline -10 --format="%h %s")
   
   # Related PRs
   PRS=$(gh pr list --repo vanman2024/DevLoopAI --search "${issueNum}" --json number,title,state,url)
   
   # Changed files
   FILES=$(git log --grep="#${issueNum}" --name-only --pretty=format: | sort -u | head -20)
   ```

5. **Check Test Coverage**
   If implementation tasks exist:
   ```bash
   # Check test coverage if available
   if [ -f "coverage/coverage-summary.json" ]; then
     COVERAGE=$(cat coverage/coverage-summary.json | jq '.total.lines.pct')
   fi
   ```

6. **Generate Progress Update**
   Use mcp__sequential-thinking-http__sequentialthinking to create comprehensive update:
   - Summarize work completed
   - Highlight current focus
   - Identify any blockers
   - Suggest next steps

7. **Create Progress Comment**
   - Primary: Use mcp__github-http__add_issue_comment with owner="vanman2024" and repo="DevLoopAI"
   - Fallback: If MCP server fails, use GitHub CLI:
     ```bash
     gh issue comment --repo vanman2024/DevLoopAI ${issueNum} --body "${progress_update}"
     ```
   ```markdown
   ## 📊 Progress Update - {timestamp}
   
   ### 🎯 Overall Progress
   - **Completion**: {completion}% ({completed}/{total} tasks)
   - **Status**: {derive_status_from_progress}
   - **Milestone**: {milestone}
   - **Phases**: {phases}
   
   ### 📈 Task Breakdown
   - ✅ Completed: {completed_tasks} tasks
   - 🔄 In Progress: {in_progress_tasks} tasks
   - 📋 Pending: {pending_tasks} tasks
   - 🚧 Blocked: {blocked_tasks} tasks
   
   ### 🏗️ Affected Modules
   {affected_modules}
   
   ### 💻 Recent Activity
   **Commits**:
   {recent_commits}
   
   **Pull Requests**:
   {related_prs}
   
   **Files Modified**:
   {changed_files}
   
   ### 📊 Test Coverage
   {coverage_info}
   
   ### 🚀 Next Steps
   {next_steps_based_on_progress}
   
   ### 🔗 Related Links
   - [View Tasks](#) 
   - [PR #{pr_number}]({pr_url})
   - [Test Results](#)
   
   {additional_context}
   ```

8. **Update Issue Labels and Metadata**
   - Primary: Use mcp__github-http__update_issue with owner="vanman2024" and repo="DevLoopAI" based on progress
   - Fallback: If MCP server fails, use GitHub CLI:
     ```bash
     gh issue edit --repo vanman2024/DevLoopAI ${issueNum} --add-label "${labels}"
     ```
   ```javascript
   const labels = [];
   if (completion >= 90) labels.push('ready-for-review');
   else if (completion >= 50) labels.push('in-progress');
   else if (completion >= 25) labels.push('development');
   else labels.push('planning');
   
   if (blockedTasks > 0) labels.push('blocked');
   if (updateType === 'blocked') labels.push('help-wanted');
   ```

9. **Update Database Status**
   Sync any status changes back to database:
   ```sql
   -- Update task statuses if needed
   UPDATE tasks 
   SET 
     updated_at = NOW(),
     last_github_sync = NOW()
   WHERE github_issue_number = $1;
   
   -- Log the update activity
   INSERT INTO activities (
     type, description, metadata, created_at
   ) VALUES (
     'issue_update',
     'GitHub issue #' || $1 || ' updated',
     jsonb_build_object(
       'issue_number', $1,
       'update_type', $2,
       'completion_percentage', $3
     ),
     NOW()
   );
   ```

10. **Update or Create Todos**
    Use TodoWrite to track remaining work:
    - Outstanding implementation tasks
    - Blocked items needing attention
    - Testing requirements
    - Documentation updates

### Update Types

#### Progress Update (default)
- Show completion percentage
- List recent activities
- Highlight current focus
- Suggest next steps

#### Status Update
- Change issue state (open/closed)
- Update labels
- Modify milestone
- Reassign if needed

#### Blocked Update
- Highlight blocking issues
- Add 'blocked' and 'help-wanted' labels
- Tag relevant team members
- Create action items

#### Completed Update
- Mark as ready for review
- Summary of work done
- Link to PRs
- Request review

### Success Criteria
- Issue updated with accurate progress
- Database synchronized with GitHub
- Clear next steps identified
- Appropriate labels applied
- Team informed of status
- Todos updated for remaining work

### Error Handling
If any step fails:
1. Use extended thinking to analyze the failure
2. Check GitHub API limits: !`gh api rate_limit`
3. Verify issue exists: !`gh issue view --repo vanman2024/DevLoopAI {issueNum}`
4. If MCP server fails, use GitHub CLI for all operations as fallback
5. Check database connectivity
6. Retry with corrected approach
7. Update TodoWrite with current status

### Example Usage
```bash
# Standard progress update
/update-issue 42

# Mark as blocked with reason
/update-issue 42 blocked "Waiting for API design approval"

# Mark as completed
/update-issue 42 completed

# Custom status update
/update-issue 42 status "Ready for QA testing"
```

### Chain Commands
After update:
- `/analyze-issue` - If blocked, analyze dependencies
- `/create-task` - If more work needed
- `/create-pr` - If ready for review
- `/notify-team` - If blocked or completed

Remember: Regular updates keep everyone informed and projects moving forward.