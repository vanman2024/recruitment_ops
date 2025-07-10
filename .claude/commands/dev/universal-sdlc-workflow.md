---
allowed-tools: Task(*), mcp__github-http__*, mcp__vercel-v0-http__*, mcp__supabase-http__*, mcp__docker-http__*, mcp__vercel-deploy-http__*, mcp__uiux-design-http__*, mcp__sequential-thinking-http__*, mcp__ide__*, mcp__postman-official__*, Write(*), Read(*), Edit(*), MultiEdit(*), Bash(*), Grep(*), Glob(*), TodoWrite(*), WebFetch(*), LS(*)
description: Universal SDLC workflow that works with any project type, organization, and deployment strategy - from issue creation to production deployment.
---

# Universal SDLC Complete Workflow Command

## Context Loading (Dynamic)
- Current directory: !`pwd`
- Git status: !`git status --porcelain`
- Current branch: !`git branch --show-current`
- Recent commits: !`git log --oneline -5`
- Project structure: !`find . -maxdepth 2 -type d | head -10`

## Project Detection
Load universal project detection functions:
@.claude/commands/dev/universal-project-detection.md

## Extended Thinking Trigger
Thinkhard through this universal SDLC workflow:
1. Detect project characteristics (language, framework, test tools)
2. Identify organization and repository context
3. Discover available templates and workflows
4. Adapt implementation approach to project constraints
5. Plan deployment strategy based on detected infrastructure
6. Design testing approach using detected frameworks
7. Map workflow to available agent architecture

## Your Task
First, detect project characteristics and gather user input, then launch the universal SDLC workflow.

### STEP 1: Project Detection and Analysis
Run project detection to understand the current environment:

```bash
# Source the detection functions
source <(grep -A 100 "detect_project_language()" .claude/commands/dev/universal-project-detection.md | sed -n '/```bash/,/```/p' | sed '1d;$d')

# Detect project characteristics
LANGUAGE=$(detect_project_language)
FRAMEWORK=$(detect_framework)
TEST_FRAMEWORK=$(detect_test_framework)
TEST_COMMANDS=$(get_test_commands)
ORGANIZATION=$(get_default_organization)
REPOSITORY=$(detect_repository_name)
DEPLOYMENT_STRATEGIES=($(detect_deployment_strategy))
ENVIRONMENTS=($(detect_environments))

# Discover templates
ISSUE_TEMPLATE=$(discover_issue_template)
PR_TEMPLATE=$(discover_pr_template)
WORKFLOW_FILES=$(discover_workflow_files)

# Display detected configuration
echo "🔍 Project Detection Results:"
echo "Language: $LANGUAGE"
echo "Framework: $FRAMEWORK"
echo "Test Framework: $TEST_FRAMEWORK"
echo "Organization: $ORGANIZATION"
echo "Repository: $REPOSITORY"
echo "Deployment: ${DEPLOYMENT_STRATEGIES[*]}"
echo "Environments: ${ENVIRONMENTS[*]}"
echo "Issue Template: $ISSUE_TEMPLATE"
echo "PR Template: $PR_TEMPLATE"
```

### STEP 2: Ask the User for Input
Ask the user:

**"Are you working with an existing issue, creating a new feature, or continuing interrupted work?"**

**If they say "continue" or "continuing"**, ask:
1. What's the PR number or branch name you were working on?
2. What step were you at when interrupted? Choose from:
   - "planning" → Resume at Step 3 (Extended Planning)
   - "coding" → Resume at Step 6 (Development)
   - "testing" → Resume at Step 9 (Testing)
   - "PR created" → Resume at Step 10 (Monitor CI/CD)
   - "CI/CD failing" → Resume at Step 10 (Monitor and Fix)
   - "deploying" → Resume at Step 11 (Deployment)
   - "preview deployment" → Resume at Step 12 (Preview Testing)
   - "ready to merge" → Resume at Step 13 (Final Merge)
3. Any specific error or issue to address?

**If they say "existing issue"**, ask:
1. What's the issue number? (e.g., 42 or #42)
2. Repository owner? (press Enter for detected: $ORGANIZATION)
3. Repository name? (press Enter for detected: $REPOSITORY)

**If they say "new feature"**, ask:
1. What feature do you want to build? (describe it)
2. Repository owner? (press Enter for detected: $ORGANIZATION)
3. Repository name? (press Enter for detected: $REPOSITORY)
4. Which module? (Backend API, Frontend UI, Database, Infrastructure, Testing, Documentation, DevOps/CI-CD, MCP Servers)
5. Priority? (Critical, High, Medium, Low)
6. Estimated hours?

### STEP 3: Process User Responses and Launch Universal Workflow

After gathering user input, use the Task tool with this universal prompt:

## UNIVERSAL TASK LAUNCH

```yaml
description: "Universal SDLC workflow for: {issue_or_feature} in {detected_language} {detected_framework}"
prompt: |
  EXECUTE UNIVERSAL SDLC WORKFLOW FOR: {issue_or_feature}
  
  DETECTED PROJECT CONFIGURATION:
  - Language: {detected_language}
  - Framework: {detected_framework}
  - Test Framework: {detected_test_framework}
  - Organization: {detected_organization}
  - Repository: {detected_repository}
  - Deployment: {detected_deployment_strategies}
  - Issue Template: {detected_issue_template}
  - PR Template: {detected_pr_template}
  
  USER INPUTS:
  - Issue/Feature: {issue_or_feature}
  - Owner: {owner}
  - Repo: {repo}
  - Module: {module}
  - Priority: {priority}
  - Hours: {hours}
  
  ### STEP 0: Universal Pre-flight Checks
  Ensure environment is ready for any project type:
  1. Verify we're in a git repository:
     ```bash
     pwd
     ls .git || (echo "ERROR: Not a git repository" && exit 1)
     ```
  2. Check git status and ensure clean working directory:
     ```bash
     git status
     CURRENT_BRANCH=$(git branch --show-current)
     if [ -n "$(git status --porcelain)" ]; then
       echo "WARNING: Uncommitted changes detected"
       git stash push -m "Universal SDLC auto-stash $(date)"
     fi
     ```
  3. Verify required tools based on detected project:
     ```bash
     # Universal tool checks
     which gh || echo "ERROR: GitHub CLI not installed"
     which git || echo "ERROR: Git not installed"
     
     # Language-specific tool checks
     case "{detected_language}" in
       "javascript")
         which node || echo "ERROR: Node.js not installed"
         which npm || echo "ERROR: npm not installed"
         ;;
       "python")
         which python3 || echo "ERROR: Python 3 not installed"
         which pip || echo "ERROR: pip not installed"
         ;;
       "go")
         which go || echo "ERROR: Go not installed"
         ;;
       "rust")
         which cargo || echo "ERROR: Cargo not installed"
         ;;
       "java")
         which javac || echo "ERROR: Java compiler not installed"
         ;;
     esac
     ```
  
  ### STEP 1: Universal Issue Creation or Retrieval
  **For Existing Issues:**
  1. Fetch issue from source repository using mcp__github-http__get_issue
  2. Create working issue in target repository if different
  3. Link issues with cross-references
  
  **For New Features:**
  Create GitHub issue using mcp__github-http__create_issue:
  - Title: "[{detected_framework}] {issue_or_feature}"
  - Labels: ["language:{detected_language}", "framework:{detected_framework}", "module:{module}", "priority:{priority}"]
  - Use detected issue template if available
  
  ### STEP 2: Universal Extended Planning
  Use available planning agent (Gemini if available, Claude if not):
  1. Analyze requirements in context of detected project type
  2. Plan implementation using detected framework patterns
  3. Consider deployment to detected infrastructure
  4. Account for detected testing framework
  
  ### STEP 3: Universal Database Schema (if needed)
  Detect database technology and apply appropriate changes:
  ```bash
  # Detect database type
  if grep -q "supabase" package.json 2>/dev/null || [ -f "supabase/config.toml" ]; then
    echo "Database: Supabase"
    # Use mcp__supabase-v4__* tools
  elif grep -q "prisma" package.json 2>/dev/null || [ -f "prisma/schema.prisma" ]; then
    echo "Database: Prisma"
    # Use Prisma CLI tools
  elif [ -f "migrations" ] || [ -f "alembic.ini" ]; then
    echo "Database: SQL with migrations"
    # Use appropriate migration tools
  else
    echo "Database: None detected"
  fi
  ```
  
  ### STEP 4: Universal Development Phase
  Use detected framework patterns for development:
  
  **Backend Development (if applicable):**
  - Create API endpoints using detected framework conventions
  - Follow detected project structure patterns
  - Use detected testing framework for unit tests
  
  **Frontend Development (if applicable):**
  - Use mcp__vercel-v0-http__generate_component for React/Vue/Angular
  - Follow detected component library patterns
  - Implement using detected styling approach
  
  **Universal Code Quality:**
  - Follow detected linting configuration
  - Use detected formatting tools
  - Implement according to detected architecture patterns
  
  ### STEP 5: Universal Branch and Commit Strategy
  ```bash
  # Create feature branch using detected conventions
  BRANCH_NAME="feat/{task_id}-{sanitized_description}"
  git checkout -b $BRANCH_NAME
  
  # Commit using detected project patterns
  git add .
  git commit -m "{detected_framework}: {description}"
  git push -u origin $BRANCH_NAME
  ```
  
  ### STEP 6: Universal Testing Phase
  Execute tests using detected framework:
  ```bash
  # Run tests using detected test framework
  {detected_test_commands}
  
  # Language-specific coverage and quality checks
  case "{detected_language}" in
    "javascript")
      npm run lint || echo "No lint script found"
      npm run type-check || echo "No type-check script found"
      ;;
    "python")
      python -m flake8 . || echo "flake8 not configured"
      python -m mypy . || echo "mypy not configured"
      ;;
    "go")
      go vet ./...
      go fmt ./...
      ;;
    "rust")
      cargo clippy
      cargo fmt --check
      ;;
  esac
  ```
  
  ### STEP 7: Universal Pull Request Creation
  Create PR using detected template:
  ```bash
  # Use detected PR template
  PR_TEMPLATE="{detected_pr_template}"
  if [ "$PR_TEMPLATE" != "none" ]; then
    TEMPLATE_CONTENT=$(cat "$PR_TEMPLATE")
  else
    TEMPLATE_CONTENT="## Description\n\n## Testing\n\n## Changes"
  fi
  
  # Create PR with universal format
  gh pr create \
    --title "{detected_framework}: {description}" \
    --body "$TEMPLATE_CONTENT" \
    --label "language:{detected_language}" \
    --label "framework:{detected_framework}"
  ```
  
  ### STEP 8: Universal CI/CD Monitoring
  Monitor CI/CD using detected workflow files:
  ```bash
  # Get PR number
  PR_NUMBER=$(gh pr view --json number -q ".number")
  
  # Monitor all detected workflows
  while true; do
    STATUS=$(gh pr view $PR_NUMBER --json statusCheckRollup -q ".statusCheckRollup.state")
    
    if [ "$STATUS" = "SUCCESS" ]; then
      echo "✅ All checks passed!"
      break
    elif [ "$STATUS" = "FAILURE" ]; then
      echo "❌ Checks failed. Analyzing..."
      gh pr view $PR_NUMBER --json statusCheckRollup -q ".statusCheckRollup[] | select(.conclusion==\"FAILURE\")"
      
      # Auto-fix common issues based on detected tools
      case "{detected_language}" in
        "javascript")
          npm run lint:fix || echo "No lint:fix script"
          ;;
        "python")
          python -m autopep8 --in-place -r . || echo "autopep8 not available"
          ;;
        "go")
          go fmt ./...
          ;;
        "rust")
          cargo fmt
          ;;
      esac
      
      # Commit fixes and retry
      git add -A
      git commit -m "fix: Auto-fix linting and formatting issues"
      git push
      
      sleep 30
    else
      echo "⏳ Checks running... Status: $STATUS"
      sleep 30
    fi
  done
  ```
  
  ### STEP 9: Universal Deployment
  Deploy using detected deployment strategies:
  ```bash
  # Deploy to each detected strategy
  STRATEGIES=({detected_deployment_strategies})
  for strategy in "${STRATEGIES[@]}"; do
    case $strategy in
      "vercel")
        echo "🚀 Deploying to Vercel..."
        # Use mcp__vercel-deploy-http__create_deployment
        ;;
      "netlify")
        echo "🚀 Deploying to Netlify..."
        netlify deploy --prod
        ;;
      "github-actions")
        echo "🚀 GitHub Actions will handle deployment"
        ;;
      "docker")
        echo "🚀 Building Docker image..."
        docker build -t {detected_repository}:latest .
        ;;
      "manual")
        echo "📝 Manual deployment required"
        ;;
    esac
  done
  ```
  
  ### STEP 10: Universal Final Merge and Cleanup
  ```bash
  # Final verification
  gh pr view $PR_NUMBER --json mergeable,statusCheckRollup
  
  # Merge PR
  gh pr merge $PR_NUMBER --merge --delete-branch
  
  # Clean up
  git checkout main
  git pull origin main
  git branch -d $BRANCH_NAME
  ```
  
  ### STEP 11: Universal Success Summary
  Create universal summary:
  ```bash
  echo "🎉 Universal SDLC Workflow Complete!"
  echo "Project: {detected_language} {detected_framework}"
  echo "Issue: {issue_or_feature}"
  echo "PR: {owner}/{repo}#$PR_NUMBER"
  echo "Deployments: {detected_deployment_strategies}"
  echo "Environments: {detected_environments}"
  ```
  
  EXECUTE ALL STEPS AUTONOMOUSLY FOR ANY PROJECT TYPE.
  
  CRITICAL UNIVERSAL PRINCIPLES:
  - Adapt to detected project characteristics
  - Use detected tools and frameworks
  - Follow detected patterns and conventions
  - Support any organization and repository
  - Work with any deployment strategy
  - Integrate with available agent architecture
  
  Use TodoWrite to track progress.
  Continue through all steps without manual intervention.
  UNIVERSAL COMPATIBILITY IS KEY!
```

## Success Criteria (Universal)
- [ ] Works with any programming language and framework
- [ ] Adapts to any organization and repository structure
- [ ] Uses detected testing frameworks and tools
- [ ] Follows detected project conventions
- [ ] Supports any deployment strategy
- [ ] Integrates with available agent architecture
- [ ] Maintains high code quality standards
- [ ] Provides consistent workflow regardless of project type

## Integration with Agent Architecture
This universal SDLC integrates with any agent architecture:
- **Single Agent (Claude Code):** Uses Claude Code for all development tasks
- **Multi-Agent (SynapseAI):** Coordinates with specialized agents
- **Hybrid:** Adapts to available agent capabilities

## Examples of Universal Adaptation

### React/Next.js Project
```bash
# Detected: javascript, nextjs, jest, vercel
TEST_COMMANDS="npm test -- --coverage"
DEPLOYMENT="vercel deploy --prod"
FRAMEWORK_PATTERNS="Next.js API routes, React components"
```

### Python/Django Project
```bash
# Detected: python, django, pytest, docker
TEST_COMMANDS="pytest tests/ --cov=. --cov-report=html"
DEPLOYMENT="docker build -t app . && docker push"
FRAMEWORK_PATTERNS="Django views, models, serializers"
```

### Go Project
```bash
# Detected: go, gin, go test, github-actions
TEST_COMMANDS="go test -v -coverprofile=coverage.out ./..."
DEPLOYMENT="git push origin main  # Triggers GitHub Actions"
FRAMEWORK_PATTERNS="Go handlers, middleware, services"
```

This universal SDLC workflow maintains all the power and automation of the original while working with any project type, organization, and deployment strategy.