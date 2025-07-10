---
allowed-tools: Bash(*), Read(*), Write(*), Grep(*), Glob(*), TodoWrite(*), mcp__filesystem-http__list_directory(*), mcp__filesystem-http__search_files(*), mcp__filesystem-http__get_file_info(*), mcp__filesystem-http__move_file(*), mcp__github-http__list_commits, mcp__github-http__get_file_contents, mcp__supabase-v3__insert_data, mcp__supabase-v3__select_data, mcp__sequential-thinking-http__sequentialthinking, mcp__memory-http__create_entities, mcp__memory-http__add_observations
description: Advanced cleanup with MCP integrations - executes in strict logical order for safety
---

@/home/gotime2022/devloop3/.claude/docs/WORKFLOW_SEQUENCES.md
@/home/gotime2022/devloop3/.claude/docs/WORKFLOW_DIAGRAMS.md

## Context

### Initial State Capture (Execute First)
- Working directory: !`pwd`
- Git status: !`git status --short | head -20`
- Current branch: !`git branch --show-current`
- Repository size: !`du -sh .git 2>/dev/null || echo "Not a git repository"`
- Last cleanup: !`cat .last-cleanup 2>/dev/null || echo "Never cleaned"`

### Quick Metrics (Execute Second)
- Python artifacts count: !`find . -type d -name "__pycache__" 2>/dev/null | wc -l`
- Node modules count: !`find . -type d -name "node_modules" 2>/dev/null | wc -l`
- Large files count: !`find . -type f -size +10M -not -path "./.git/*" 2>/dev/null | wc -l`
- Temporary files count: !`find . -name "*.tmp" -o -name "*.log" -o -name "*.bak" 2>/dev/null | wc -l`

### User Arguments
- Cleanup focus: $ARGUMENTS

## Your Task

**IMPORTANT**: Execute these phases in STRICT SEQUENTIAL ORDER. Do not skip ahead or execute out of order.

### 🔍 PHASE 1: Pre-Cleanup Safety Check (MANDATORY FIRST)

Execute these checks IN ORDER:

1. **Git Safety Check**:
   ```bash
   # 1.1 - Check for uncommitted changes
   git status --porcelain
   
   # 1.2 - If changes exist, STOP and ask user to commit first
   # DO NOT PROCEED if uncommitted changes exist
   ```

2. **Create Safety Checkpoint**:
   ```bash
   # 1.3 - Record current state
   echo "Cleanup started: $(date)" > .last-cleanup
   
   # 1.4 - Create archive directory
   mkdir -p .cleanup-archive/$(date +%Y%m%d_%H%M%S)
   ```

3. **Check Previous Cleanup History**:
   ```python
   # 1.5 - Use MCP to check database
   mcp__supabase-v3__select_data(
       table="cleanup_history",
       project_id="dkpwdljgnysqzjufjtnk",
       filters={"project_name": "DevLoopAI"},
       order_by="created_at.desc",
       limit=5
   )
   ```

### 📊 PHASE 2: Analysis and Learning (EXECUTE SECOND)

Execute IN THIS ORDER:

1. **Load Project Memory**:
   ```python
   # 2.1 - Check what we've learned before
   mcp__memory-http__search_nodes(
       query="DevLoopAI cleanup patterns"
   )
   ```

2. **Deep File System Scan**:
   ```python
   # 2.2 - Search for temporary files
   mcp__filesystem-http__search_files(
       path=".",
       pattern="*.tmp",
       exclude_patterns=[".git", ".cleanup-archive"]
   )
   
   # 2.3 - Search for cache files
   mcp__filesystem-http__search_files(
       path=".",
       pattern="*.cache",
       exclude_patterns=[".git", "node_modules"]
   )
   
   # 2.4 - Search for Python artifacts
   mcp__filesystem-http__search_files(
       path=".",
       pattern="__pycache__",
       exclude_patterns=[".git", "venv"]
   )
   ```

3. **Analyze Git History**:
   ```python
   # 2.5 - Check recent commits for cleanup patterns
   mcp__github-http__list_commits(
       owner="vanman2024",
       repo="DevLoopAI",
       per_page=20
   )
   ```

4. **Sequential Thinking Analysis**:
   ```python
   # 2.6 - Think about patterns
   mcp__sequential-thinking-http__sequentialthinking(
       thought="Analyzing file patterns to identify safe cleanup targets",
       thoughtNumber=1,
       totalThoughts=3,
       nextThoughtNeeded=True
   )
   ```

### 📝 PHASE 3: Categorization (EXECUTE THIRD)

Build cleanup lists IN THIS ORDER:

1. **Category 1 - Auto-Safe Files**:
   ```python
   # 3.1 - List files that are ALWAYS safe to clean
   auto_safe = []
   # Python: __pycache__, *.pyc, .pytest_cache
   # System: .DS_Store, Thumbs.db
   # Editor: *.swp, *~
   ```

2. **Category 2 - Size-Based Review**:
   ```python
   # 3.2 - Get file info for large files
   for large_file in large_files:
       mcp__filesystem-http__get_file_info(path=large_file)
   ```

3. **Category 3 - Project-Specific**:
   ```python
   # 3.3 - Check .gitignore for patterns
   mcp__github-http__get_file_contents(
       owner="vanman2024",
       repo="DevLoopAI",
       path=".gitignore"
   )
   ```

4. **Category 4 - Manual Review**:
   ```python
   # 3.4 - List untracked files
   # These need user confirmation
   ```

### ✅ PHASE 4: User Confirmation (EXECUTE FOURTH)

Present findings IN THIS ORDER:

1. **Create TodoWrite Plan**:
   ```python
   # 4.1 - Create detailed todo list
   TodoWrite(todos=[
       {"id": "1", "content": "Review Category 1 auto-safe files", "status": "pending", "priority": "high"},
       {"id": "2", "content": "Analyze large files for cleanup", "status": "pending", "priority": "medium"},
       {"id": "3", "content": "Check project-specific artifacts", "status": "pending", "priority": "medium"},
       {"id": "4", "content": "Manual review unclear files", "status": "pending", "priority": "low"}
   ])
   ```

2. **Present Cleanup Plan**:
   ```markdown
   # 4.2 - Show user what will be cleaned
   ## Cleanup Plan
   
   ### Category 1: Auto-Safe (X files, Y MB)
   - Will be archived automatically
   
   ### Category 2: Large Files (X files, Y MB)
   - Need your review
   
   ### Category 3: Project Artifacts (X files, Y MB)
   - Based on project type
   
   ### Category 4: Unclear Purpose (X files, Y MB)
   - Require manual decision
   ```

3. **Get User Confirmation**:
   ```
   # 4.3 - WAIT for user approval before proceeding
   # DO NOT continue without explicit confirmation
   ```

### 🚀 PHASE 5: Execution (EXECUTE FIFTH - ONLY AFTER CONFIRMATION)

Execute cleanup IN THIS ORDER:

1. **Create Archive Structure**:
   ```bash
   # 5.1 - Set up archive directories
   ARCHIVE_PATH=".cleanup-archive/$(date +%Y%m%d_%H%M%S)"
   mkdir -p "$ARCHIVE_PATH/auto-safe"
   mkdir -p "$ARCHIVE_PATH/size-based"
   mkdir -p "$ARCHIVE_PATH/project-specific"
   mkdir -p "$ARCHIVE_PATH/manual"
   ```

2. **Archive Category 1 (Auto-Safe)**:
   ```python
   # 5.2 - Move auto-safe files
   for file in auto_safe_files:
       mcp__filesystem-http__move_file(
           source=file,
           destination=f"{archive_path}/auto-safe/{file}"
       )
   ```

3. **Process Category 2-4** (Only approved files):
   ```python
   # 5.3 - Move only user-approved files
   for file in approved_files:
       mcp__filesystem-http__move_file(
           source=file,
           destination=f"{archive_path}/{category}/{file}"
       )
   ```

4. **Update Todo Status**:
   ```python
   # 5.4 - Mark todos as completed
   TodoWrite(todos=[
       {"id": "1", "content": "Review Category 1 auto-safe files", "status": "completed", "priority": "high"},
       # ... update all todos
   ])
   ```

### 📊 PHASE 6: Verification (EXECUTE SIXTH)

Verify results IN THIS ORDER:

1. **Compare Before/After**:
   ```python
   # 6.1 - List directory after cleanup
   mcp__filesystem-http__list_directory(path=".")
   ```

2. **Calculate Metrics**:
   ```bash
   # 6.2 - Show space recovered
   du -sh "$ARCHIVE_PATH"
   ```

3. **Run Tests**:
   ```bash
   # 6.3 - Ensure nothing broke
   # Run appropriate test command based on project
   ```

### 💾 PHASE 7: Recording and Learning (EXECUTE LAST)

Save results IN THIS ORDER:

1. **Update Database**:
   ```python
   # 7.1 - Log cleanup session
   mcp__supabase-v3__insert_data(
       table="cleanup_history",
       project_id="dkpwdljgnysqzjufjtnk",
       data={
           "project_name": "DevLoopAI",
           "files_cleaned": file_count,
           "space_recovered": total_size,
           "archive_path": archive_path,
           "patterns_found": patterns,
           "created_at": datetime.now()
       }
   )
   ```

2. **Update Memory**:
   ```python
   # 7.2 - Remember patterns for next time
   mcp__memory-http__add_observations(
       entityName="DevLoopAI_cleanup_patterns",
       observations=[
           f"Safe patterns: {safe_patterns}",
           f"Project artifacts: {project_artifacts}",
           f"Never delete: {protected_files}"
       ]
   )
   ```

3. **Generate Report**:
   ```markdown
   # 7.3 - Create final report
   ## Cleanup Complete!
   
   - Files archived: X
   - Space recovered: Y MB
   - Archive location: .cleanup-archive/YYYYMMDD
   - New patterns learned: Z
   
   ### Suggestions:
   - Add to .gitignore: [list]
   - Regular cleanup: [frequency]
   ```

4. **Create Follow-up Todos**:
   ```python
   # 7.4 - Final todos
   TodoWrite(todos=[
       {"id": "follow-1", "content": "Update .gitignore with new patterns", "status": "pending", "priority": "medium"},
       {"id": "follow-2", "content": "Review archive in 30 days for deletion", "status": "pending", "priority": "low"}
   ])
   ```

## ⚠️ CRITICAL EXECUTION RULES:

1. **NEVER skip phases** - Each phase depends on the previous
2. **STOP if git has uncommitted changes** - Safety first
3. **WAIT for user confirmation** - Never auto-execute cleanup
4. **ARCHIVE don't delete** - Always move to archive first
5. **TEST after cleanup** - Ensure nothing broke
6. **LOG everything** - Track all operations

Remember: Execute phases 1-7 in EXACT order. No parallel execution. No skipping ahead.