# Agent Workflow Patterns

## Overview
This document extracts reusable patterns from the DevLoop workflow documentation and structures them for use by specialized agents in the multi-agent architecture.

## Database Agent Patterns
*Extracted from COMPREHENSIVE_DEVLOOP_WORKFLOW.md and MILESTONE_CONTROL_SYSTEM.md*

### Pattern: Database Schema Evolution
```yaml
database_agent_knowledge:
  schema_design:
    - hierarchy: "Project → Milestone → Phase → Module → Task"
    - relationships: "Foreign keys with cascade rules"
    - indexing: "Index on frequently queried columns"
    - constraints: "NOT NULL for required fields"
  
  migration_strategy:
    - versioning: "Sequential migration files"
    - rollback: "Always include DOWN migration"
    - data_preservation: "Migrate data, don't lose it"
    - testing: "Test migrations on copy of production data"
  
  orm_patterns:
    supabase:
      - rls_policies: "Row-level security for multi-tenancy"
      - real_time: "Use real-time subscriptions for live updates"
      - edge_functions: "Business logic in edge functions"
    
    prisma:
      - schema_file: "Single source of truth in schema.prisma"
      - migrations: "prisma migrate dev for development"
      - client: "Generated client with type safety"
    
    django:
      - models: "One model per business entity"
      - migrations: "python manage.py makemigrations"
      - admin: "Auto-generated admin interface"
```

### Pattern: Database Task Workflow
```yaml
database_task_execution:
  planning:
    - analyze_requirements: "Understand data model needs"
    - design_schema: "Plan tables, relationships, indexes"
    - consider_performance: "Query optimization from start"
  
  implementation:
    - create_migrations: "Write migration files"
    - apply_locally: "Test on local database"
    - seed_data: "Create test data for validation"
  
  validation:
    - test_queries: "Ensure queries perform well"
    - verify_constraints: "Check data integrity"
    - load_testing: "Test with realistic data volume"
```

## Frontend Agent Patterns
*Extracted from V0_MCP_INTEGRATION_WORKFLOW.md and UI generation patterns*

### Pattern: Component Generation
```yaml
frontend_agent_knowledge:
  component_architecture:
    react:
      - structure: "components/, hooks/, utils/, types/"
      - naming: "PascalCase for components, camelCase for hooks"
      - props: "TypeScript interfaces for all props"
      - state: "useState for local, context for global"
    
    vue:
      - structure: "components/, composables/, utils/, types/"
      - naming: "PascalCase for components, camelCase for composables"
      - props: "defineProps with TypeScript"
      - state: "ref/reactive for local, pinia for global"
    
    angular:
      - structure: "components/, services/, models/, guards/"
      - naming: "kebab-case for files, PascalCase for classes"
      - props: "@Input() decorators"
      - state: "RxJS observables and services"
  
  styling_approaches:
    tailwind:
      - utilities: "Utility-first CSS approach"
      - responsive: "Mobile-first responsive design"
      - dark_mode: "Support light/dark themes"
    
    css_modules:
      - scoped: "Locally scoped CSS classes"
      - naming: "camelCase for class names"
      - composition: "Compose styles from base classes"
    
    styled_components:
      - components: "Styled components with props"
      - themes: "ThemeProvider for global theming"
      - animations: "CSS-in-JS animations"
```

### Pattern: UI Generation Workflow
```yaml
frontend_task_execution:
  analysis:
    - understand_requirements: "Parse UI/UX requirements"
    - identify_components: "Break down into reusable components"
    - plan_state_management: "Design data flow"
  
  generation:
    - use_v0_mcp: "Generate initial component structure"
    - apply_design_system: "Use consistent design tokens"
    - implement_interactions: "Add user interactions"
  
  integration:
    - connect_apis: "Integrate with backend services"
    - handle_loading: "Add loading and error states"
    - optimize_performance: "Implement lazy loading, memoization"
```

## Backend Agent Patterns
*Extracted from API development patterns and service architecture*

### Pattern: API Development
```yaml
backend_agent_knowledge:
  api_design:
    rest:
      - endpoints: "RESTful resource-based URLs"
      - methods: "GET, POST, PUT, DELETE semantics"
      - status_codes: "Proper HTTP status codes"
      - versioning: "URL versioning (/api/v1/)"
    
    graphql:
      - schema: "Schema-first development"
      - resolvers: "Field-level data fetching"
      - subscriptions: "Real-time updates"
      - caching: "Query result caching"
    
    grpc:
      - protobuf: "Protocol buffer definitions"
      - services: "Service-oriented architecture"
      - streaming: "Bidirectional streaming"
      - load_balancing: "Client-side load balancing"
  
  authentication:
    jwt:
      - tokens: "Short-lived access tokens"
      - refresh: "Refresh token rotation"
      - claims: "User permissions in claims"
    
    oauth2:
      - flows: "Authorization code flow"
      - scopes: "Permission-based scopes"
      - providers: "Google, GitHub, etc."
    
    session:
      - cookies: "Secure, HttpOnly cookies"
      - storage: "Redis for session storage"
      - expiry: "Automatic session expiry"
```

### Pattern: Service Architecture
```yaml
backend_service_patterns:
  microservices:
    - single_responsibility: "One service, one business function"
    - api_gateway: "Central entry point"
    - service_discovery: "Dynamic service registration"
    - circuit_breaker: "Fault tolerance patterns"
  
  monolith:
    - modular: "Clear module boundaries"
    - layers: "Presentation, business, data layers"
    - dependency_injection: "Loose coupling"
    - testing: "Unit, integration, e2e tests"
  
  serverless:
    - functions: "Single-purpose functions"
    - event_driven: "Event-triggered execution"
    - stateless: "No persistent state"
    - cold_start: "Optimize for cold starts"
```

## Testing Agent Patterns
*Extracted from comprehensive testing strategies*

### Pattern: Multi-Level Testing
```yaml
testing_agent_knowledge:
  test_pyramid:
    unit_tests:
      - coverage: "90%+ for critical business logic"
      - isolation: "Mock external dependencies"
      - fast: "Run in milliseconds"
      - focused: "Test single units of code"
    
    integration_tests:
      - apis: "Test API endpoints end-to-end"
      - database: "Test database interactions"
      - services: "Test service integration"
      - contracts: "Test service contracts"
    
    e2e_tests:
      - user_flows: "Test complete user journeys"
      - browsers: "Cross-browser testing"
      - devices: "Mobile and desktop testing"
      - performance: "Load and stress testing"
  
  test_frameworks:
    javascript:
      - jest: "Unit testing with mocking"
      - cypress: "E2E testing with real browsers"
      - storybook: "Component testing in isolation"
    
    python:
      - pytest: "Flexible testing with fixtures"
      - selenium: "Web browser automation"
      - locust: "Load testing framework"
    
    go:
      - testing: "Built-in testing package"
      - testify: "Assertion library"
      - ginkgo: "BDD testing framework"
```

## DevOps Agent Patterns
*Extracted from deployment and CI/CD workflows*

### Pattern: Deployment Pipeline
```yaml
devops_agent_knowledge:
  ci_cd:
    stages:
      - build: "Compile, bundle, optimize"
      - test: "Run all test suites"
      - security: "Security scanning"
      - deploy: "Deploy to environments"
      - monitor: "Post-deployment monitoring"
    
    environments:
      - development: "Local development environment"
      - staging: "Production-like testing"
      - production: "Live user environment"
      - canary: "Gradual rollout environment"
  
  deployment_strategies:
    blue_green:
      - parallel: "Run two identical environments"
      - switch: "Instant traffic switching"
      - rollback: "Quick rollback capability"
    
    rolling:
      - gradual: "Gradual instance replacement"
      - zero_downtime: "No service interruption"
      - health_checks: "Continuous health monitoring"
    
    canary:
      - percentage: "Route percentage of traffic"
      - monitoring: "Monitor key metrics"
      - automatic_rollback: "Auto-rollback on issues"
```

## Security Agent Patterns
*Extracted from security best practices*

### Pattern: Security-First Development
```yaml
security_agent_knowledge:
  secure_coding:
    input_validation:
      - sanitization: "Sanitize all user input"
      - parameterized: "Use parameterized queries"
      - whitelist: "Whitelist over blacklist"
    
    authentication:
      - strong_passwords: "Password complexity requirements"
      - mfa: "Multi-factor authentication"
      - rate_limiting: "Prevent brute force attacks"
    
    data_protection:
      - encryption: "Encrypt sensitive data"
      - https: "HTTPS everywhere"
      - secrets: "Never hardcode secrets"
  
  security_testing:
    static_analysis:
      - code_scanning: "Automated code vulnerability scanning"
      - dependency_check: "Check for vulnerable dependencies"
      - linting: "Security-focused linting rules"
    
    dynamic_analysis:
      - penetration_testing: "Simulated attacks"
      - fuzzing: "Input fuzzing for edge cases"
      - monitoring: "Runtime security monitoring"
```

## Agent Coordination Patterns
*Extracted from multi-agent orchestration workflows*

### Pattern: Agent Handoff
```yaml
agent_coordination:
  handoff_protocol:
    - context_sharing: "Share relevant context between agents"
    - state_verification: "Verify previous agent's work"
    - error_handling: "Handle handoff failures gracefully"
    - rollback_capability: "Ability to rollback to previous state"
  
  communication:
    - async_messaging: "Asynchronous message passing"
    - status_updates: "Real-time status updates"
    - error_reporting: "Centralized error reporting"
    - progress_tracking: "Detailed progress tracking"
  
  coordination_strategies:
    sequential:
      - order: "Predefined execution order"
      - dependencies: "Wait for dependencies"
      - validation: "Validate before next step"
    
    parallel:
      - concurrent: "Run independent tasks concurrently"
      - synchronization: "Synchronize at merge points"
      - resource_management: "Manage shared resources"
    
    event_driven:
      - triggers: "Event-based task triggering"
      - reactive: "React to system events"
      - pub_sub: "Publisher-subscriber pattern"
```

## Integration with Universal SDLC

These patterns are referenced by the universal SDLC workflow and can be used by specialized agents:

```yaml
# Example: Database Agent using patterns
database_agent_task:
  pattern: "database_agent_knowledge.schema_design"
  context: "detected_database_type"
  execution: "database_task_execution"

# Example: Frontend Agent using patterns
frontend_agent_task:
  pattern: "frontend_agent_knowledge.component_architecture[detected_framework]"
  context: "detected_styling_approach"
  execution: "frontend_task_execution"
```

This pattern system enables agents to:
1. **Adapt to any project type** using detected characteristics
2. **Follow proven patterns** from the workflow documentation
3. **Coordinate effectively** through standardized handoff protocols
4. **Maintain quality** through consistent pattern application
5. **Scale efficiently** by reusing proven approaches

The patterns are framework-agnostic but provide specific guidance for detected technologies, making the universal SDLC truly adaptable to any project while maintaining the quality and automation of the original workflow.