---
allowed-tools: Task(*), mcp__github-http__*, mcp__vercel-v0-http__*, mcp__supabase-http__*, mcp__docker-http__*, mcp__vercel-deploy-http__*, mcp__uiux-design-http__*, mcp__sequential-thinking-http__*, mcp__ide__*, mcp__postman-official__*, Write(*), Read(*), Edit(*), MultiEdit(*), Bash(*), Grep(*), Glob(*), TodoWrite(*), WebFetch(*), LS(*)
description: Execute complete SDLC workflow from issue creation to production deployment with continuous autonomous execution.
---

# SDLC Complete Workflow Command - Strategic Hierarchy Integration

## Context Loading
- Current directory: !`pwd`
- Git status: !`git status --porcelain`
- Current branch: !`git branch --show-current`
- Recent commits: !`git log --oneline -5`
- Project structure: !`find . -maxdepth 2 -type d | head -10`
- Package info: @package.json
- Issue template: @.github/ISSUE_TEMPLATE/feature_request.yaml
- PR template: @.github/PULL_REQUEST_TEMPLATE.md
- GitHub workflow: @.github/workflows/automated-pr-validation.yml
- MCP workflow guide: @.claude/docs/MCP_WORKFLOW_GUIDE.md
- Hierarchy context: Load current project → milestone → phase → module status

## Extended Thinking Trigger
Thinkhard through this SDLC workflow step by step with STRATEGIC HIERARCHY INTEGRATION:
1. Analyze the feature requirements from $ARGUMENTS
2. Understand the project structure and existing patterns
3. **Map feature to strategic hierarchy: Project → Milestone → Phase → Module**
4. **Assess strategic alignment with current milestone objectives**
5. Plan the implementation approach with proper module separation
6. Consider GitHub Actions integration points
7. Design test strategy and deployment plan
8. **Ensure continuous hierarchy progress tracking**
9. Map out the complete workflow from issue to production
10. Identify potential bottlenecks and mitigation strategies
11. **Maintain strategic coherence throughout execution**

## Your Task
First, gather the required information from the user, then launch the SDLC workflow with their responses.

### STEP 1: Ask the User for Input
Ask the user:

**"Are you working with an existing issue, creating a new feature, or continuing interrupted work?"**

**If they say "continue" or "continuing"**, ask:
1. What's the PR number or branch name you were working on?
2. What step were you at when interrupted? Choose from:
   - "planning" → Resume at Step 3 (Extended Planning)
   - "coding" → Resume at Step 6 (Backend/Frontend Development)
   - "testing" → Resume at Step 9 (Comprehensive Testing)
   - "PR created" → Resume at Step 10 (Monitor GitHub Actions)
   - "GitHub Actions failing" → Resume at Step 10 (Monitor and Fix)
   - "deploying to DevLoop3" → Resume at Step 11 (DevLoop3 Deployment)
   - "preview deployment" → Resume at Step 12 (Preview Deployment)
   - "ready to merge" → Resume at Step 13 (Final PR Merge)
3. Any specific error or issue to address?

Then check:
- Current git branch: `git branch --show-current`
- Git status: `git status`
- Recent todos: Use TodoRead to see current session todos
- PR status if applicable: `gh pr view {PR_NUMBER} --json state,statusCheckRollup`

**If they say "existing issue"**, ask:
1. What's the issue number? (e.g., 42 or #42)
2. Repository owner? (press Enter for default: vanman2024)
3. Repository name? (press Enter for default: DevLoopAI)

**If they say "new feature"**, ask:
1. What feature do you want to build? (describe it)
2. Repository owner? (press Enter for default: vanman2024)  
3. Repository name? (press Enter for default: mcp-kernel-new)
4. Which module? (Backend API, Frontend UI, Database, Infrastructure, Testing, Documentation, DevOps/CI-CD, MCP Servers)
5. Priority? (Critical, High, Medium, Low)
6. Estimated hours?

### STEP 2: Process User Responses
Take the user's answers and store them as variables to use in the Task prompt:

**Example for continuation:**
- User says: "continue"
- User provides: "PR #123", "GitHub Actions failing", "test coverage too low"
- You check current state and set: continuation_mode = true, pr_number = "123", resume_at_step = "10", specific_issue = "test coverage"
- Launch Task with special continuation prompt that jumps to Step 10 (Monitor GitHub Actions)

**Example for existing issue:**
- User says: "existing issue"
- User provides: "42", "", "" (using defaults)
- You set: issue_or_feature = "#42", owner = "vanman2024", repo = "DevLoopAI"

**Example for new feature:**
- User says: "new feature"  
- User provides: "Add OAuth2 authentication", "", "", "Backend API", "High", "24"
- You set: issue_or_feature = "Add OAuth2 authentication", owner = "vanman2024", repo = "mcp-kernel-new", module = "Backend API", priority = "High", hours = "24"

## IMMEDIATE TASK LAUNCH  
After gathering the information from the user, use one of these Task prompts:

### For New Work or Existing Issues:
```yaml
description: "Complete SDLC workflow for: {issue_or_feature}"
prompt: |
  EXECUTE COMPLETE SDLC WORKFLOW FOR: {issue_or_feature}
  
  Repository: {owner}/{repo}
  Module: {module} (if provided)
  Priority: {priority} (if provided) 
  Estimated Hours: {hours} (if provided)

### For Continuation of Interrupted Work:
```yaml
description: "Continue SDLC workflow - PR #{pr_number} at {resume_at_step}"
prompt: |
  CONTINUE INTERRUPTED SDLC WORKFLOW
  
  Current Status:
  - PR Number: {pr_number}
  - Branch: {current_branch}
  - Last Known Step: {resume_at_step}
  - Specific Issue: {specific_issue}
  
  IMPORTANT: Skip directly to {resume_at_step} - do not repeat completed steps!
  
  First, verify current state:
  1. Check git status and current branch
  2. Review PR status: gh pr view {pr_number} --json state,statusCheckRollup
  3. Check todos for context: Use TodoRead
  4. Identify exact point of failure/interruption
  
  Then continue from {resume_at_step}:
  
  ### STEP 0: Pre-flight Checks with Strategic Context
  Ensure environment is ready AND load strategic hierarchy context:
  1. Verify we're in the correct directory:
     ```bash
     pwd  # Must be in mcp-kernel-new
     ls .git  # Verify git repository exists
     ```
  2. Check git status and current branch:
     ```bash
     git status
     CURRENT_BRANCH=$(git branch --show-current)
     if [ "$CURRENT_BRANCH" != "master" ]; then
       git checkout master
       git pull origin master
     fi
     ```
  3. Ensure clean working directory:
     ```bash
     if [ -n "$(git status --porcelain)" ]; then
       echo "WARNING: Uncommitted changes detected"
       git stash push -m "SDLC workflow auto-stash $(date)"
     fi
     ```
  4. Verify required tools installed:
     ```bash
     which gh || echo "ERROR: GitHub CLI not installed"
     which claude || echo "ERROR: Claude CLI not installed"
     which pytest || echo "ERROR: pytest not installed"
     ```
  5. **Load Strategic Hierarchy Context**:
     ```bash
     # Load current project hierarchy from database
     PROJECT_CONTEXT=$(mcp__supabase-v4__execute_sql "SELECT p.name, p.vision, p.status FROM projects p WHERE p.name = 'DevLoopAI' OR p.name = 'SynapseAI' LIMIT 1")
     
     # Load current milestone status
     MILESTONE_CONTEXT=$(mcp__supabase-v4__execute_sql "SELECT m.name, m.target_date, m.completion_percentage, m.status FROM milestones m JOIN projects p ON m.project_id = p.id WHERE p.name IN ('DevLoopAI', 'SynapseAI') AND m.status = 'active' ORDER BY m.target_date LIMIT 1")
     
     # Load current phase context
     PHASE_CONTEXT=$(mcp__supabase-v4__execute_sql "SELECT ph.name, ph.phase_type, ph.status FROM phases ph JOIN milestones m ON ph.milestone_id = m.id WHERE m.status = 'active' AND ph.status IN ('active', 'pending') ORDER BY ph.order_index LIMIT 1")
     
     echo "📊 Strategic Context Loaded:"
     echo "Project: $PROJECT_CONTEXT"
     echo "Milestone: $MILESTONE_CONTEXT"
     echo "Phase: $PHASE_CONTEXT"
     ```
  
  ### STEP 1: Workflow Entry Point Detection
  Check if {issue_or_feature} is an existing issue number or new feature:
  - If {issue_or_feature} matches #<number> pattern, fetch existing issue from {owner}/{repo}
  - Otherwise, create new issue in mcp-kernel-new
  
  ### STEP 2: Issue Creation or Retrieval with Strategic Hierarchy Integration
  **For Existing Issues:**
  1. Fetch issue from source repository using mcp__github-http__get_issue with owner={owner} and repo={repo}
  2. Extract key information:
     - Title, description, labels, assignees
     - Module from labels (e.g., "module:backend-api")
     - Priority from labels (e.g., "priority:high")
  3. **Analyze Strategic Hierarchy Placement using Intelligent Feature Intake**:
     ```sql
     -- Create feature request for AI analysis
     INSERT INTO feature_requests (project_id, user_input, context, request_type)
     VALUES ('{project_id}', '{issue_description}', '{strategic_context}', 'existing_issue');
     
     -- Get AI placement recommendation
     SELECT 
       ai_analysis,
       placement_recommendation,
       target_milestone_id,
       target_phase_id,
       target_module_id
     FROM feature_requests WHERE id = '{request_id}';
     ```
  4. Create mirrored issue in vanman2024/mcp-kernel-new using mcp__github-http__create_issue:
     - Title: "[Mirror] {original_title} (from {owner}/{repo}#{number})"
     - Body: Include original issue link, full requirements, AND strategic context
     - Labels: Copy all relevant labels from source + strategic labels
     - **Milestone**: Link to current strategic milestone
  5. **Create Database Records for Strategic Tracking**:
     ```sql
     -- Create feature record in hierarchy
     INSERT INTO features (name, description, module_id, project_id, priority, github_issue_number)
     VALUES ('{feature_name}', '{description}', '{target_module_id}', '{project_id}', '{priority}', '{github_issue_number}');
     
     -- Create tasks for atomic work units
     INSERT INTO tasks (name, description, feature_id, module_id, priority, github_issue_number)
     VALUES ('{task_name}', '{task_description}', '{feature_id}', '{module_id}', '{priority}', '{github_issue_number}');
     ```
  6. Link both issues with cross-references:
     - Comment on source: "Implementation tracked in vanman2024/mcp-kernel-new#{new_issue_number}"
     - Comment on mirror: "Implementing {owner}/{repo}#{original_number} | Strategic Context: {milestone_name} → {phase_name} → {module_name}"
  
  **For New Features:**
  1. **Process through Intelligent Feature Intake System**:
     ```sql
     -- Create feature request for AI analysis
     INSERT INTO feature_requests (project_id, user_input, context, request_type)
     VALUES ('{project_id}', '{issue_or_feature}', '{strategic_context}', 'new_feature');
     
     -- Wait for AI analysis and placement recommendation
     SELECT 
       ai_analysis,
       similarity_scores,
       placement_recommendation,
       decision_type,
       target_milestone_id,
       target_phase_id,
       target_module_id
     FROM feature_requests WHERE id = '{request_id}';
     ```
  2. Create GitHub issue using mcp__github-http__create_issue in user name: vanman2024 Repo, mcp-kernel-new
     - Title: "[Feature]: {issue_or_feature}"
     - Body: Detailed feature description with acceptance criteria AND strategic context
     - Labels: ["module:{module}", "priority:{priority}", "milestone:{milestone_name}", "phase:{phase_name}"]
     - Milestone: Current strategic milestone from AI analysis
     - Estimated Hours: {hours} (add to body)
  3. **Create Strategic Database Records**:
     ```sql
     -- Create feature record with strategic placement
     INSERT INTO features (name, description, module_id, project_id, priority, github_issue_number, complexity_score)
     VALUES ('{feature_name}', '{description}', '{ai_recommended_module_id}', '{project_id}', '{priority}', '{github_issue_number}', '{ai_complexity_score}');
     
     -- Create atomic tasks from AI decomposition
     INSERT INTO tasks (name, description, feature_id, module_id, priority, estimated_hours, github_issue_number)
     SELECT 
       task_name,
       task_description,
       '{feature_id}',
       '{module_id}',
       '{priority}',
       estimated_hours,
       '{github_issue_number}'
     FROM jsonb_array_elements('{ai_generated_tasks}');
     ```
  4. **Update Strategic Progress Tracking**:
     ```sql
     -- Update module progress
     UPDATE modules SET 
       status = 'active',
       updated_at = NOW()
     WHERE id = '{target_module_id}';
     
     -- Update phase progress
     UPDATE phases SET 
       status = 'active',
       started_at = COALESCE(started_at, NOW())
     WHERE id = '{target_phase_id}';
     
     -- Update milestone progress
     UPDATE milestones SET 
       status = 'active',
       updated_at = NOW()
     WHERE id = '{target_milestone_id}';
     ```
  
  ### STEP 3: Extended Planning with Sequential Thinking and Strategic Alignment
  Use mcp__sequential-thinking-http__sequentialthinking to plan implementation with strategic context:
  - **Strategic Alignment Check**: Verify feature supports milestone objectives
  - **Hierarchy Impact Analysis**: Assess impact on current phase and module
  - Break down technical requirements with strategic priorities
  - Identify API changes needed with strategic implications
  - Plan UI/UX modifications aligned with project vision
  - Consider breaking changes and strategic timing
  - Map dependencies within strategic hierarchy
  - **Strategic Progress Planning**: Plan how this work advances milestone completion
  - **Resource Allocation**: Ensure work aligns with strategic resource allocation
  - **Risk Assessment**: Identify strategic risks and mitigation strategies
  
  **Strategic Context Integration**:
  ```sql
  -- Load full strategic context for planning
  SELECT 
    p.name as project_name,
    p.vision as project_vision,
    m.name as milestone_name,
    m.target_date as milestone_deadline,
    ph.name as phase_name,
    ph.phase_type as phase_type,
    mod.name as module_name,
    mod.module_type as module_type,
    f.name as feature_name,
    f.complexity_score as complexity_score
  FROM projects p
  JOIN milestones m ON m.project_id = p.id
  JOIN phases ph ON ph.milestone_id = m.id
  JOIN modules mod ON mod.phase_id = ph.id
  JOIN features f ON f.module_id = mod.id
  WHERE f.id = '{feature_id}' AND m.status = 'active';
  ```
  
  **Strategic Planning Questions**:
  1. How does this feature advance the current milestone?
  2. What's the impact on phase completion timeline?
  3. Does this align with module strategic objectives?
  4. What are the strategic dependencies and risks?
  5. How does this support the overall project vision?
  
  ### STEP 4: Database Schema and Migrations with Strategic Impact Assessment
  If database changes required, assess strategic impact:
  1. **Strategic Impact Assessment**:
     ```sql
     -- Assess impact on other features in the hierarchy
     SELECT 
       f.name as affected_feature,
       f.status as feature_status,
       mod.name as affected_module,
       COUNT(t.id) as affected_tasks
     FROM features f
     JOIN modules mod ON f.module_id = mod.id
     LEFT JOIN tasks t ON t.feature_id = f.id
     WHERE mod.id IN (SELECT DISTINCT module_id FROM features WHERE id = '{current_feature_id}')
     GROUP BY f.id, f.name, f.status, mod.name;
     ```
  2. Design schema changes using mcp__supabase-v4__execute_sql with strategic considerations
  3. Create migration files using mcp__supabase-v4__apply_migration with rollback strategy
  4. Test migrations locally and assess strategic impact
  5. Update Supabase schema with strategic change tracking:
     ```sql
     -- Track strategic schema changes
     INSERT INTO activities (event_type, title, description, project_id, milestone_id, phase_id, module_id, context)
     VALUES ('database_migration', 'Schema Migration for {feature_name}', 'Strategic database changes for {feature_name}', '{project_id}', '{milestone_id}', '{phase_id}', '{module_id}', '{migration_context}');
     ```
  
  ### STEP 5: MCP Server Development (if needed)
  If feature requires new MCP server:
  - Follow FastMCP patterns from build-complete-fastmcp-server.md
  - Test server locally before integration
  - Configure server with claude mcp add
  
  ### STEP 6: Backend API Development
  Create/update API endpoints:
  - Define request/response schemas
  - Implement business logic
  - Add validation and error handling
  - Create unit tests
  - Document API changes
  
  ### STEP 7: Frontend UI Development
  If UI changes needed:
  - Use mcp__vercel-v0-http__generate_component to generate components
  - Implement state management
  - Connect to backend APIs
  - Add loading and error states
  - Create component tests
  
  ### STEP 8: Create Feature Branch and Initial Commit with Strategic Context
  CRITICAL: Create branch and commit configuration updates FIRST with strategic tracking:
  1. Create feature branch in mcp-kernel-new with strategic naming:
     ```bash
     # Strategic branch naming: milestone-phase-module-feature
     git checkout -b feat/m{milestone_id}-p{phase_id}-{module_name}-{feature_name}
     ```
  2. Update all config files if needed:
     - servers/configs/mcp-http-config-versioned.json (if adding new MCP server)
     - .claude/settings.local.json (if adding new permissions)
     - package.json dependencies
     - Any other configuration files
  3. **Update Strategic Progress Tracking**:
     ```sql
     -- Update task status to in_progress
     UPDATE tasks SET 
       status = 'in_progress',
       assigned_specialist = 'development-agent',
       github_branch = 'feat/m{milestone_id}-p{phase_id}-{module_name}-{feature_name}',
       updated_at = NOW()
     WHERE feature_id = '{feature_id}';
     
     -- Create activity record
     INSERT INTO activities (event_type, title, description, project_id, milestone_id, phase_id, module_id, task_id, context)
     VALUES ('development_started', 'Development Started: {feature_name}', 'Strategic development work began for {feature_name}', '{project_id}', '{milestone_id}', '{phase_id}', '{module_id}', '{task_id}', '{strategic_context}');
     ```
  4. Commit configuration changes separately:
     ```bash
     git add servers/configs/ .claude/settings.local.json package.json
     git commit -m "chore: Update configurations for {description} | Strategic Context: {milestone_name} → {phase_name} → {module_name}"
     ```
  5. Commit implementation code:
     ```bash
     git add .
     git commit -m "feat: {description} - Implementation | Strategic Context: {milestone_name} → {phase_name} → {module_name} | Advances milestone {completion_percentage}%"
     git push -u origin feat/m{milestone_id}-p{phase_id}-{module_name}-{feature_name}
     ```
  6. Verify push successful and branch tracking set
  7. **Update Strategic Branch Tracking**:
     ```sql
     -- Update module branch tracking
     UPDATE modules SET 
       branch_name = 'feat/m{milestone_id}-p{phase_id}-{module_name}-{feature_name}',
       branch_status = 'active',
       updated_at = NOW()
     WHERE id = '{module_id}';
     ```
  
  ### STEP 9: Comprehensive Testing Phase in mcp-kernel-new
  Execute all tests in mcp-kernel-new repository with HIGH coverage requirements:
  
  **Coverage Targets:**
  - Critical modules (auth, payments, data): 95%+ coverage
  - Core business logic: 90%+ coverage  
  - API endpoints: 90%+ coverage
  - Utility functions: 85%+ coverage
  - UI components: 85%+ coverage
  - Overall project: 90%+ coverage (not just 80%)
  
  **Testing Strategy:**
  1. Unit tests with coverage:
     ```bash
     pytest tests/unit/ -xvs --cov=. --cov-report=term-missing --cov-fail-under=90
     ```
  2. Integration tests: pytest tests/integration/ -xvs
  3. Security scanning: 
     - grep -r "sk-" . --exclude-dir=venv
     - Run security linters (bandit for Python, npm audit for JS)
  4. E2E testing: pytest tests/e2e/ -xvs
  5. Performance tests: Check response times < 200ms
  6. Edge case testing: Test error paths, boundary conditions
  7. MCP server testing if applicable
  
  **If coverage is below target:**
  - Identify uncovered lines with --cov-report=html
  - Add tests for error handling paths
  - Test edge cases and boundary conditions
  - Add parameterized tests for multiple scenarios
  - Ensure all public methods have tests
  - Mock external dependencies properly
  
  ### STEP 9: Create Pull Request with Strategic Context
  Create PR using mcp__github-http__create_pull_request in mcp-kernel-new with strategic information:
  - **Title**: "[{milestone_name}] {feature_name} - {description}"
  - **Body**: Include strategic context:
    ```markdown
    ## Strategic Context
    - **Milestone**: {milestone_name} ({milestone_completion}% complete)
    - **Phase**: {phase_name} ({phase_type})
    - **Module**: {module_name} ({module_type})
    - **Strategic Impact**: {strategic_impact_description}
    - **Milestone Advancement**: This PR advances milestone completion by {advancement_percentage}%
    
    ## Issue Reference
    Fixes #{issue_number}
    
    ## Strategic Alignment
    - [x] Aligns with current milestone objectives
    - [x] Supports phase deliverables
    - [x] Integrates with target module
    - [x] Advances strategic project vision
    
    ## Description
    {complete_description}
    
    ## Test Checklist
    - [ ] Unit tests passing
    - [ ] Integration tests passing
    - [ ] Strategic alignment verified
    - [ ] Hierarchy progress updated
    
    ## Screenshots
    {screenshots_if_applicable}
    ```
  - **Labels**: ["milestone:{milestone_name}", "phase:{phase_name}", "module:{module_name}", "priority:{priority}"]
  - **Milestone**: Link to GitHub milestone
  - Ensure PR shows all config updates and strategic context
  - **Update Strategic Database**:
    ```sql
    -- Update task with PR information
    UPDATE tasks SET 
      github_pr_number = '{pr_number}',
      status = 'in_review',
      updated_at = NOW()
    WHERE feature_id = '{feature_id}';
    
    -- Create activity record
    INSERT INTO activities (event_type, title, description, project_id, milestone_id, phase_id, module_id, task_id, external_url, context)
    VALUES ('pull_request_created', 'Pull Request Created: {feature_name}', 'Strategic PR created for {feature_name}', '{project_id}', '{milestone_id}', '{phase_id}', '{module_id}', '{task_id}', '{pr_url}', '{strategic_context}');
    ```
  
  ### STEP 10: Monitor GitHub Actions Until ALL Pass
  CRITICAL: Do NOT proceed until ALL GitHub Actions pass:
  1. Get PR details and wait for initial checks to start:
     ```bash
     # Get PR number
     PR_NUMBER=$(gh pr list --head feat/task-{id}-{description} --json number --jq '.[0].number')
     
     # Wait for checks to initialize (GitHub needs time)
     sleep 10
     ```
  2. Monitor PR status continuously using polling loop:
     ```bash
     WHILE true:
       # Get current status
       STATUS=$(gh pr view $PR_NUMBER --json statusCheckRollup --jq '.statusCheckRollup.state')
       
       if STATUS == "SUCCESS":
         break  # All checks passed!
       elif STATUS == "FAILURE" or STATUS == "ERROR":
         # Get failed checks
         gh pr view $PR_NUMBER --json statusCheckRollup --jq '.statusCheckRollup[] | select(.conclusion=="FAILURE")'
         
         # Get run ID of failed workflow
         RUN_ID=$(gh run list --workflow="automated-pr-validation.yml" --json databaseId,conclusion --jq '.[] | select(.conclusion=="failure") | .databaseId' | head -1)
         
         # Analyze failure logs
         gh run view $RUN_ID --log-failed > failure_logs.txt
         
         # Common fixes:
         - Linting errors: Run autopep8/black/eslint --fix
         - Test failures: Fix broken tests and update
         - Type errors: Fix TypeScript/Python type issues
         - Missing deps: Update package.json/requirements.txt
         
         # Commit fixes
         git add -A
         git commit -m "fix: Address GitHub Actions failures"
         git push
         
         # Wait for new run
         sleep 30
       else:
         # Status is PENDING or null - keep waiting
         echo "Checks still running... Current status: $STATUS"
         sleep 30
     ```
  3. Verify final success before proceeding:
     - All required checks must show ✅
     - PR must be mergeable
     - No conflicts with base branch
  
  ### STEP 11: DevLoop3 Deployment (After mcp-kernel-new Update)
  ONLY after mcp-kernel-new is fully updated, deploy to DevLoop3:
  1. Verify mcp-kernel-new has all latest changes committed
  2. Copy updated files from mcp-kernel-new to DevLoop3:
     - Copy servers/configs/mcp-http-config-versioned.json → /home/gotime2022/devloop3/servers/configs/
     - Copy .claude/settings.local.json → /home/gotime2022/devloop3/.claude/
     - Copy any new MCP servers → /home/gotime2022/devloop3/servers/
     - Copy updated commands → /home/gotime2022/devloop3/.claude/commands/
  3. Update DevLoop3 configurations to match mcp-kernel-new
  4. Start services in DevLoop3
  5. Validate deployment in DevLoop3 environment
  6. Ensure DevLoop3 matches mcp-kernel-new exactly
  
  ### STEP 12: Preview Deployment and Testing
  After DevLoop3 validation matches mcp-kernel-new:
  - Deploy to Vercel preview using mcp__vercel-deploy-http__create_deployment
  - Run E2E tests on preview
  - Performance validation
  - Ensure preview deployment uses configs from mcp-kernel-new
  
  ### STEP 13: Final PR Merge and Production Deployments with Strategic Completion
  1. Final GitHub Actions verification before merge:
     ```bash
     # Verify ALL checks are still passing
     gh pr view {PR_NUMBER} --json statusCheckRollup,mergeable
     ```
  2. **Strategic Completion Verification**:
     ```sql
     -- Verify strategic alignment and completion
     SELECT 
       f.name as feature_name,
       f.status as feature_status,
       COUNT(t.id) as total_tasks,
       COUNT(CASE WHEN t.status = 'completed' THEN 1 END) as completed_tasks,
       (COUNT(CASE WHEN t.status = 'completed' THEN 1 END) * 100.0 / COUNT(t.id)) as completion_percentage
     FROM features f
     LEFT JOIN tasks t ON t.feature_id = f.id
     WHERE f.id = '{feature_id}'
     GROUP BY f.id, f.name, f.status;
     ```
  3. Only merge when ALL conditions met:
     - ✅ All GitHub Actions passing
     - ✅ DevLoop3 deployment successful
     - ✅ Preview deployment successful
     - ✅ All tests passing
     - ✅ Strategic objectives achieved
     - ✅ Hierarchy progress updated
  4. **Strategic Completion Database Updates**:
     ```sql
     -- Mark feature as completed
     UPDATE features SET 
       status = 'completed',
       completed_at = NOW(),
       branch_status = 'merged'
     WHERE id = '{feature_id}';
     
     -- Mark all tasks as completed
     UPDATE tasks SET 
       status = 'completed',
       completed_at = NOW(),
       github_pr_number = '{pr_number}'
     WHERE feature_id = '{feature_id}';
     
     -- Update module progress
     UPDATE modules SET 
       status = CASE 
         WHEN (SELECT COUNT(*) FROM features WHERE module_id = '{module_id}' AND status != 'completed') = 0 
         THEN 'completed' 
         ELSE 'in_progress' 
       END,
       updated_at = NOW()
     WHERE id = '{module_id}';
     
     -- Update phase progress
     UPDATE phases SET 
       status = CASE 
         WHEN (SELECT COUNT(*) FROM modules WHERE phase_id = '{phase_id}' AND status != 'completed') = 0 
         THEN 'completed' 
         ELSE 'in_progress' 
       END,
       completed_at = CASE 
         WHEN (SELECT COUNT(*) FROM modules WHERE phase_id = '{phase_id}' AND status != 'completed') = 0 
         THEN NOW() 
         ELSE NULL 
       END
     WHERE id = '{phase_id}';
     
     -- Update milestone progress
     UPDATE milestones SET 
       completion_percentage = (
         SELECT COALESCE(AVG(
           CASE 
             WHEN ph.status = 'completed' THEN 100
             WHEN ph.status = 'in_progress' THEN 50
             ELSE 0
           END
         ), 0)
         FROM phases ph 
         WHERE ph.milestone_id = '{milestone_id}'
       ),
       status = CASE 
         WHEN (SELECT COUNT(*) FROM phases WHERE milestone_id = '{milestone_id}' AND status != 'completed') = 0 
         THEN 'completed' 
         ELSE 'in_progress' 
       END,
       updated_at = NOW()
     WHERE id = '{milestone_id}';
     ```
  5. Merge PR using mcp__github-http__merge_pull_request
  6. **Create Strategic Completion Activity**:
     ```sql
     INSERT INTO activities (event_type, title, description, project_id, milestone_id, phase_id, module_id, task_id, context)
     VALUES ('feature_completed', 'Feature Completed: {feature_name}', 'Strategic feature {feature_name} completed and merged. Milestone advancement: {milestone_completion}%', '{project_id}', '{milestone_id}', '{phase_id}', '{module_id}', '{task_id}', '{strategic_completion_context}');
     ```
  
  4. PRODUCTION DEPLOYMENT TO DEVLOOP3:
     ```bash
     # Deploy merged changes to DevLoop3 production
     cd /home/gotime2022/devloop3
     git checkout master
     git pull origin master
     
     # Copy production configs from mcp-kernel-new
     cp /home/gotime2022/mcp-kernel-new/servers/configs/* ./servers/configs/
     cp /home/gotime2022/mcp-kernel-new/.claude/settings.local.json ./.claude/
     
     # Restart DevLoop3 services
     ./scripts/restart-services.sh
     
     # Validate DevLoop3 production deployment
     curl http://localhost:3000/health || echo "DevLoop3 deployment needs attention"
     ```
  
  5. PRODUCTION DEPLOYMENT TO VERCEL:
     ```bash
     # Deploy to Vercel production using MCP
     mcp__vercel-deploy-http__create_deployment with production=true
     
     # Monitor Vercel deployment
     mcp__vercel-deploy-http__get_deployment_status
     
     # If deployment succeeds, promote to production
     mcp__vercel-deploy-http__promote_deployment
     ```
  
  6. Monitor BOTH production deployments:
     ```bash
     # Monitor GitHub Actions production workflow
     gh run list --workflow="production-deploy" --limit=1
     gh run view {PROD_RUN_ID} --json status,conclusion
     
     # Monitor Vercel production
     vercel ls --prod
     
     # Check both production endpoints
     curl https://production.vercel.app/health
     curl http://devloop3.local/health
     ```
  
  7. If either production deployment fails:
     - Use mcp__github-http__create_issue for hotfix
     - Rollback if necessary (both DevLoop3 and Vercel)
     - Fix and redeploy to BOTH environments
     - Continue monitoring until BOTH succeed
  
  8. Final validation and completion:
     - ✅ DevLoop3 production working
     - ✅ Vercel production working
     - ✅ Both environments in sync
     - Update all issues with completion status
     - Mark all todos complete
  
  ### STEP 14: Final Summary and Handoff
  Create comprehensive summary for future reference:
  1. Generate implementation summary:
     ```bash
     echo "## SDLC Workflow Summary - $(date)" > sdlc_summary.md
     echo "Issue: $ARGUMENTS[0]" >> sdlc_summary.md
     echo "PR: vanman2024/mcp-kernel-new#$PR_NUMBER" >> sdlc_summary.md
     echo "Branch: feat/task-{id}-{description}" >> sdlc_summary.md
     ```
  2. Document all changes made:
     - List of modified files
     - New MCP servers added
     - Configuration changes
     - Test coverage achieved
  3. Create handoff notes using TodoWrite:
     - What was implemented
     - Any known issues or limitations
     - Follow-up tasks needed
     - Performance metrics
  4. Close workflow:
     - Ensure all todos marked complete
     - Return to master branch
     - Clean up any temporary files
  
  ### STEP 15: MCP Server Configuration (If Needed)
  Only if new MCP servers were added during implementation:
  1. Configure newly added MCP servers with claude mcp add:
     ```bash
     # For each new MCP server added during development
     claude mcp add --transport http NAME URL
     
     # Examples:
     claude mcp add --transport http vercel-v0-http http://localhost:8010
     claude mcp add --transport http github-http http://localhost:8011
     claude mcp add --transport http docker-http http://localhost:8020
     ```
  2. Verify MCP servers are running:
     ```bash
     # Check server status
     ps aux | grep "mcp-server"
     netstat -tulpn | grep LISTEN
     ```
  3. Test newly configured servers:
     ```bash
     # Test server connectivity
     claude mcp list
     ```
  4. Update documentation:
     - Add new server to MCP server documentation
     - Update workflow guides with new capabilities
     - Document any special configuration requirements
  
  EXECUTE ALL STEPS AUTONOMOUSLY WITHOUT STOPPING.
  CRITICAL FAILURE HANDLING:
  - NEVER skip failed GitHub Actions - fix and retry until ALL pass
  - Use continuous monitoring loops with GitHub MCP tools
  - Auto-fix common issues and re-trigger workflows
  - Only proceed to next step when current step is 100% successful
  - If persistent failures, create detailed issue with logs
  
  Use TodoWrite frequently to track progress.
  Reference templates with @ symbol when needed.
  Continue through all steps without manual intervention.
  PERSISTENCE IS KEY - keep trying until everything passes!
```

## Success Criteria
- [ ] Original issue fetched from source repository (if existing issue)
- [ ] Mirrored issue created in vanman2024/mcp-kernel-new with proper labels
- [ ] All code implemented according to requirements
- [ ] Tests written and passing with HIGH coverage:
  - [ ] Critical modules: 95%+ coverage
  - [ ] Core logic & APIs: 90%+ coverage
  - [ ] Overall project: 90%+ coverage minimum
  - [ ] All error paths tested
  - [ ] Performance benchmarks met (< 200ms response times)
- [ ] Security scanning passed (no exposed secrets, no vulnerabilities)
- [ ] PR created and approved
- [ ] Preview deployment successful (Vercel preview environment)
- [ ] Production deployments completed:
  - [ ] DevLoop3 production deployment successful
  - [ ] Vercel production deployment successful
  - [ ] Both production environments verified working
  - [ ] Environments are in sync
- [ ] Both issues updated with completion status
- [ ] All todos marked complete

### Error Recovery
If any step fails:
1. Use extended thinking to analyze failure
2. Check GitHub Actions logs: !`gh run view --log-failed`
3. Review test failures: !`npm test -- --verbose`
4. Retry failed step with corrections
5. Update TodoWrite with current status
6. Continue workflow from recovery point

### Monitoring Points
GitHub Actions will automatically:
- Validate PR has milestone
- Run backend/frontend tests
- Deploy to preview environment
- Run E2E tests on preview
- Update task status in database
- Deploy to production on merge
- Send completion notifications

### Integration with Existing Commands
This workflow integrates with:
- `/mcp-test-server` - For testing MCP servers
- `/mcp-quick-deploy` - For server deployments
- `/mcp-fix-and-deploy` - For hotfixes
- GitHub templates via @ references
- Automated PR validation workflow

### Example Usage - Interactive Flow

#### Example 1: Working with Existing Issue
```
User: /sdlc-workflow
Claude: Are you working with an existing issue or creating a new feature?
User: existing issue
Claude: What's the issue number? (e.g., 42 or #42)
User: 42
Claude: Repository owner? (press Enter for default: vanman2024)
User: [Enter]
Claude: Repository name? (press Enter for default: DevLoopAI)  
User: [Enter]

Claude then launches Task with:
- issue_or_feature = "#42"
- owner = "vanman2024"
- repo = "DevLoopAI"
```

#### Example 2: Creating New Feature
```
User: /sdlc-workflow
Claude: Are you working with an existing issue, creating a new feature, or continuing interrupted work?
User: new feature
Claude: What feature do you want to build? (describe it)
User: Add OAuth2 authentication with Google and GitHub
Claude: Repository owner? (press Enter for default: vanman2024)
User: [Enter]
Claude: Repository name? (press Enter for default: mcp-kernel-new)
User: [Enter]
Claude: Which module? (Backend API, Frontend UI, Database, etc.)
User: Backend API
Claude: Priority? (Critical, High, Medium, Low)
User: High
Claude: Estimated hours?
User: 24

Claude then launches Task with:
- issue_or_feature = "Add OAuth2 authentication with Google and GitHub"
- owner = "vanman2024"  
- repo = "mcp-kernel-new"
- module = "Backend API"
- priority = "High"
- hours = "24"
```

#### Example 3: Continuing Interrupted Work
```
User: /sdlc-workflow
Claude: Are you working with an existing issue, creating a new feature, or continuing interrupted work?
User: continue
Claude: What's the PR number or branch name you were working on?
User: PR 156
Claude: What step were you at when interrupted? Choose from:
   - "planning" → Resume at Step 3
   - "coding" → Resume at Step 6
   - "testing" → Resume at Step 9
   - "PR created" → Resume at Step 10
   - "GitHub Actions failing" → Resume at Step 10
   - "deploying to DevLoop3" → Resume at Step 11
   - "preview deployment" → Resume at Step 12
   - "ready to merge" → Resume at Step 13
User: GitHub Actions failing
Claude: Any specific error or issue to address?
User: Jest tests failing with coverage below 80%

Claude checks current state:
- Runs: git branch --show-current (finds: feat/task-42-oauth)
- Runs: git status (finds: clean working directory)
- Uses: TodoRead (finds: incomplete testing tasks)
- Runs: gh pr view 156 --json state,statusCheckRollup

Claude then launches Task with continuation prompt:
- pr_number = "156"
- current_branch = "feat/task-42-oauth"
- resume_at_step = "Step 10: Monitor GitHub Actions"
- specific_issue = "Jest tests failing with coverage below 80%"

The Task agent will skip directly to Step 10 and focus on fixing the test coverage issue.
```

### Workflow Execution Notes
1. The Task tool ensures continuous execution without manual intervention
2. GitHub Actions runs automatically at each trigger point
3. All templates are referenced with @ for consistency
4. TodoWrite tracks progress throughout execution
5. Extended thinking handles complex planning phases
6. MCP tools provide direct integration with services
7. Validation occurs at each critical step
8. Recovery mechanisms handle failures gracefully

### Deployment Flow
1. **Development**: Work happens in mcp-kernel-new feature branch
2. **Preview**: Deploys to Vercel preview URL for testing
3. **After PR Merge**: TWO production deployments happen:
   - **DevLoop3 Production**: Local development environment at /home/gotime2022/devloop3
   - **Vercel Production**: Public production deployment
4. Both production environments must succeed and stay in sync

This command provides end-to-end automation of the complete SDLC workflow, from initial issue creation through production deployment and validation.