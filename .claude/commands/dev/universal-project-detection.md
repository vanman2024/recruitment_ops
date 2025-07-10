# Universal Project Detection System

## Overview
This system detects project characteristics dynamically instead of using hardcoded values, making the SDLC command work with any project type, organization, and deployment strategy.

## Project Detection Functions

### 1. Language and Framework Detection
```bash
detect_project_language() {
    if [ -f "package.json" ]; then
        echo "javascript"
    elif [ -f "requirements.txt" ] || [ -f "pyproject.toml" ]; then
        echo "python"
    elif [ -f "go.mod" ]; then
        echo "go"
    elif [ -f "Cargo.toml" ]; then
        echo "rust"
    elif [ -f "pom.xml" ] || [ -f "build.gradle" ]; then
        echo "java"
    elif [ -f "composer.json" ]; then
        echo "php"
    else
        echo "unknown"
    fi
}

detect_framework() {
    local language=$(detect_project_language)
    case $language in
        "javascript")
            if grep -q "next" package.json; then echo "nextjs"
            elif grep -q "react" package.json; then echo "react"
            elif grep -q "vue" package.json; then echo "vue"
            elif grep -q "angular" package.json; then echo "angular"
            elif grep -q "svelte" package.json; then echo "svelte"
            else echo "vanilla"; fi
            ;;
        "python")
            if [ -f "manage.py" ]; then echo "django"
            elif grep -q "flask" requirements.txt 2>/dev/null; then echo "flask"
            elif grep -q "fastapi" requirements.txt 2>/dev/null; then echo "fastapi"
            else echo "python"; fi
            ;;
        "go")
            if grep -q "gin" go.mod; then echo "gin"
            elif grep -q "echo" go.mod; then echo "echo"
            else echo "go"; fi
            ;;
        *)
            echo "$language"
            ;;
    esac
}
```

### 2. Test Framework Detection
```bash
detect_test_framework() {
    local language=$(detect_project_language)
    case $language in
        "javascript")
            if grep -q "jest" package.json; then echo "jest"
            elif grep -q "mocha" package.json; then echo "mocha"
            elif grep -q "vitest" package.json; then echo "vitest"
            else echo "npm test"; fi
            ;;
        "python")
            if [ -d "tests" ] && command -v pytest >/dev/null; then echo "pytest"
            elif grep -q "unittest" requirements.txt 2>/dev/null; then echo "unittest"
            else echo "pytest"; fi
            ;;
        "go")
            echo "go test"
            ;;
        "rust")
            echo "cargo test"
            ;;
        "java")
            if [ -f "pom.xml" ]; then echo "mvn test"
            elif [ -f "build.gradle" ]; then echo "gradle test"
            else echo "mvn test"; fi
            ;;
        *)
            echo "unknown"
            ;;
    esac
}

get_test_commands() {
    local test_framework=$(detect_test_framework)
    case $test_framework in
        "jest")
            echo "npm test -- --coverage --coverage-reporters=text-summary"
            ;;
        "pytest")
            echo "pytest tests/ -xvs --cov=. --cov-report=term-missing --cov-fail-under=90"
            ;;
        "go test")
            echo "go test -v -coverprofile=coverage.out ./..."
            ;;
        "cargo test")
            echo "cargo test"
            ;;
        "mvn test")
            echo "mvn test"
            ;;
        "gradle test")
            echo "gradle test"
            ;;
        *)
            echo "echo 'No test framework detected'"
            ;;
    esac
}
```

### 3. Organization and Repository Detection
```bash
detect_git_organization() {
    local remote_url=$(git remote get-url origin 2>/dev/null)
    if [[ $remote_url =~ github\.com[:/]([^/]+)/([^/]+)\.git ]]; then
        echo "${BASH_REMATCH[1]}"
    elif [[ $remote_url =~ github\.com[:/]([^/]+)/([^/]+) ]]; then
        echo "${BASH_REMATCH[1]}"
    else
        echo "unknown"
    fi
}

detect_repository_name() {
    local remote_url=$(git remote get-url origin 2>/dev/null)
    if [[ $remote_url =~ github\.com[:/]([^/]+)/([^/]+)\.git ]]; then
        echo "${BASH_REMATCH[2]}"
    elif [[ $remote_url =~ github\.com[:/]([^/]+)/([^/]+) ]]; then
        echo "${BASH_REMATCH[2]}"
    else
        basename "$(pwd)"
    fi
}

get_default_organization() {
    local detected_org=$(detect_git_organization)
    if [ "$detected_org" != "unknown" ]; then
        echo "$detected_org"
    else
        echo "vanman2024"  # Fallback for current project
    fi
}
```

### 4. Template Discovery
```bash
discover_issue_template() {
    if [ -f ".github/ISSUE_TEMPLATE/feature_request.yaml" ]; then
        echo ".github/ISSUE_TEMPLATE/feature_request.yaml"
    elif [ -f ".github/ISSUE_TEMPLATE/feature_request.yml" ]; then
        echo ".github/ISSUE_TEMPLATE/feature_request.yml"
    elif [ -f ".github/ISSUE_TEMPLATE/feature_request.md" ]; then
        echo ".github/ISSUE_TEMPLATE/feature_request.md"
    elif [ -f ".github/ISSUE_TEMPLATE.md" ]; then
        echo ".github/ISSUE_TEMPLATE.md"
    else
        echo "none"
    fi
}

discover_pr_template() {
    if [ -f ".github/PULL_REQUEST_TEMPLATE.md" ]; then
        echo ".github/PULL_REQUEST_TEMPLATE.md"
    elif [ -f ".github/pull_request_template.md" ]; then
        echo ".github/pull_request_template.md"
    elif [ -f "PULL_REQUEST_TEMPLATE.md" ]; then
        echo "PULL_REQUEST_TEMPLATE.md"
    else
        echo "none"
    fi
}

discover_workflow_files() {
    if [ -d ".github/workflows" ]; then
        find .github/workflows -name "*.yml" -o -name "*.yaml" | head -5
    else
        echo "none"
    fi
}
```

### 5. Deployment Strategy Detection
```bash
detect_deployment_strategy() {
    local strategies=()
    
    if [ -f "vercel.json" ] || [ -f ".vercel/project.json" ]; then
        strategies+=("vercel")
    fi
    
    if [ -f "netlify.toml" ] || [ -f "_redirects" ]; then
        strategies+=("netlify")
    fi
    
    if [ -f "Dockerfile" ]; then
        strategies+=("docker")
    fi
    
    if [ -f ".github/workflows/deploy.yml" ] || [ -f ".github/workflows/deploy.yaml" ]; then
        strategies+=("github-actions")
    fi
    
    if [ -f "railway.toml" ] || [ -f "railway.json" ]; then
        strategies+=("railway")
    fi
    
    if [ ${#strategies[@]} -eq 0 ]; then
        strategies+=("manual")
    fi
    
    echo "${strategies[@]}"
}

get_deployment_commands() {
    local strategies=($(detect_deployment_strategy))
    for strategy in "${strategies[@]}"; do
        case $strategy in
            "vercel")
                echo "vercel deploy --prod"
                ;;
            "netlify")
                echo "netlify deploy --prod"
                ;;
            "docker")
                echo "docker build -t app . && docker run -p 3000:3000 app"
                ;;
            "github-actions")
                echo "git push origin main  # Triggers GitHub Actions"
                ;;
            "railway")
                echo "railway deploy"
                ;;
            "manual")
                echo "echo 'Manual deployment required'"
                ;;
        esac
    done
}
```

### 6. Environment Detection
```bash
detect_environments() {
    local environments=()
    
    if [ -f ".env.local" ] || [ -f ".env.development" ]; then
        environments+=("development")
    fi
    
    if [ -f ".env.staging" ] || [ -f ".env.test" ]; then
        environments+=("staging")
    fi
    
    if [ -f ".env.production" ] || [ -f ".env.prod" ]; then
        environments+=("production")
    fi
    
    if [ ${#environments[@]} -eq 0 ]; then
        environments+=("development" "production")
    fi
    
    echo "${environments[@]}"
}

get_environment_config() {
    local env=$1
    case $env in
        "development")
            echo ".env.local .env.development .env"
            ;;
        "staging")
            echo ".env.staging .env.test"
            ;;
        "production")
            echo ".env.production .env.prod"
            ;;
        *)
            echo ".env"
            ;;
    esac
}
```

## Usage Example

```bash
# Detect project characteristics
LANGUAGE=$(detect_project_language)
FRAMEWORK=$(detect_framework)
TEST_FRAMEWORK=$(detect_test_framework)
TEST_COMMANDS=$(get_test_commands)
ORGANIZATION=$(get_default_organization)
REPOSITORY=$(detect_repository_name)
DEPLOYMENT_STRATEGIES=($(detect_deployment_strategy))
ENVIRONMENTS=($(detect_environments))

# Use detected values instead of hardcoded ones
echo "Detected project: $LANGUAGE ($FRAMEWORK)"
echo "Test framework: $TEST_FRAMEWORK"
echo "Repository: $ORGANIZATION/$REPOSITORY"
echo "Deployment strategies: ${DEPLOYMENT_STRATEGIES[*]}"
echo "Environments: ${ENVIRONMENTS[*]}"
```

## Integration with SDLC Workflow

This detection system replaces all hardcoded values in the SDLC command:

- `vanman2024` → `$(get_default_organization)`
- `DevLoopAI` → `$(detect_repository_name)`
- `pytest tests/unit/` → `$(get_test_commands)`
- `@.github/ISSUE_TEMPLATE/feature_request.yaml` → `@$(discover_issue_template)`
- `/home/gotime2022/devloop3/` → Dynamic environment detection

The SDLC command becomes truly universal while maintaining all its current functionality.