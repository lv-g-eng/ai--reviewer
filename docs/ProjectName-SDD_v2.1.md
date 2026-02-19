---
title: Software Design Document
project: AI-Based Code Reviewer
version: 2.1
date: 2026-02-16
authors: [BaiXuan Zhang]
reviewers: [Dr. Siraprapa]
status: In Review
last_updated: 2026-02-16
---

# AI-Based Reviewer on Project Code and Architecture
## Software Design Document (SDD)

**Version:** v2.1  
**Date:** 2026-02-16

## Document History

| Version | Date | Author | Reviewer | Changes |
|---------|------|--------|----------|---------|
| v1.0 | 2026-02-07 | BaiXuan Zhang | Dr. Siraprapa | Initial draft |
| v2.1 | 2026-02-16 | BaiXuan Zhang | Dr. Siraprapa | Added security design, deployment architecture, complete database design, API specs, architecture diagrams |

---

# Table of Contents

1. [Introduction](#1-introduction)
2. [System Architecture](#2-system-architecture)
3. [Database Design](#3-database-design)
4. [Component Design](#4-component-design)
5. [Security Design](#5-security-design)
6. [Interface Design](#6-interface-design)
7. [Deployment Architecture](#7-deployment-architecture)
8. [Technology Stack](#8-technology-stack)
9. [Architecture Decision Records](#9-architecture-decision-records)

---

# 1. Introduction

## 1.1 Purpose

This Software Design Document (SDD) describes the architectural and detailed design of the AI-Based Reviewer platform for automated code review and architectural analysis. It serves as a comprehensive guide for the development team, defining system architecture, component interactions, data structures, interface designs, and implementation specifications aligned with the requirements outlined in the Software Requirements Specification (SRS v2.1).

## 1.2 System Overview

The AI-Based Reviewer is a web-based platform that provides intelligent, automated code review and architectural analysis for software projects. The system leverages cutting-edge technologies including Abstract Syntax Trees (AST), graph databases, and Large Language Models (LLMs) to deliver comprehensive code quality assessment, architectural drift detection, and compliance verification.

### Core Capabilities

1. **Automated Pull Request Review** - AI-powered code analysis with inline comments
2. **Real-time Architectural Drift Detection** - Graph-based analysis using Neo4j
3. **Compliance Verification** - ISO/IEC 25010, ISO/IEC 23396, and industry standards
4. **Interactive Dependency Graph Visualization** - D3.js-powered interactive graphs
5. **Enterprise-grade Security** - RBAC, JWT authentication, audit logging

## 1.3 Design Principles

- **Modularity**: Microservices architecture with clear service boundaries
- **Scalability**: Horizontal scaling capability for all stateless components
- **Resilience**: Fault tolerance with graceful degradation
- **Security**: Defense in depth with multiple security layers
- **Maintainability**: Clean code, comprehensive documentation, automated testing
- **Performance**: Optimized for sub-second response times

## 1.4 Scope

This document covers:
- System architecture and component design
- Database schema and data models
- API specifications and interfaces
- Security architecture and controls
- Deployment topology and infrastructure
- Technology stack and tool selection

---

# 2. System Architecture

## 2.1 Architectural Overview

The system implements a multi-tier microservices architecture designed for modularity, scalability, and resilience. The architecture follows industry best practices including separation of concerns, horizontal scaling capability, and high availability patterns.

### Architecture Diagram

See: `docs/diagram/system-architecture.puml`

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Layer                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Browser    │  │    Mobile    │  │   CLI Tool   │          │
│  │  (React/Next)│  │     App      │  │              │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTPS/WSS
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API Gateway Layer                           │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  API Gateway (Kong/Nginx)                                │   │
│  │  - Rate Limiting  - Authentication  - Load Balancing     │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ Internal Network
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Application Layer                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │    Auth      │  │   Project    │  │   Analysis   │          │
│  │   Service    │  │   Manager    │  │   Service    │          │
│  │  (FastAPI)   │  │  (FastAPI)   │  │  (FastAPI)   │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  Code Review │  │ Architecture │  │   Agentic    │          │
│  │    Engine    │  │   Analyzer   │  │   AI Service │          │
│  │  (Python)    │  │  (Python)    │  │  (Python)    │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       Data Layer                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  PostgreSQL  │  │    Neo4j     │  │    Redis     │          │
│  │  (Relational)│  │    (Graph)   │  │  (Cache/Queue)│         │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    External Services                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   GitHub     │  │   OpenAI     │  │  Anthropic   │          │
│  │     API      │  │   GPT-4 API  │  │  Claude API  │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```


## 2.2 Logical Architecture

The system follows a multi-tier architecture with clear separation of concerns:

### Presentation Layer
- **Technology**: React 18, Next.js 14, Tailwind CSS
- **Responsibilities**:
  - Server-side rendering for SEO and performance
  - Interactive dashboards for code metrics and architecture visualization
  - Real-time updates via WebSocket connections
  - Responsive design for desktop and mobile
- **Components**:
  - Dashboard UI
  - Repository Management UI
  - Analysis Results Viewer
  - Dependency Graph Visualizer
  - Settings and Configuration UI

### Application Layer
- **Technology**: FastAPI (Python 3.11+), Pydantic for validation
- **Responsibilities**:
  - REST API endpoints for client requests
  - Business logic orchestration
  - Request validation and error handling
  - Authentication and authorization
- **Services**:
  - Auth Service: User authentication, JWT management, RBAC
  - Project Manager: Repository management, webhook configuration
  - Analysis Service: Analysis orchestration, result aggregation

### Service Layer
- **Technology**: Python 3.11+, Celery for async tasks
- **Responsibilities**:
  - Core business logic implementation
  - Integration with external services
  - Asynchronous task processing
- **Components**:
  - **AST Parser Service**: Generates abstract syntax trees from source code
  - **Graph Analysis Service**: Manages dependency graph operations in Neo4j
  - **LLM Integration Service**: Coordinates with AI APIs for code review
  - **GitHub Integration Service**: Handles webhooks and repository operations
  - **Metrics Service**: Calculates and aggregates quality metrics

### Data Layer
- **PostgreSQL**: Transactional data (users, projects, analyses, audit logs)
- **Neo4j**: Graph data (AST nodes, dependencies, architectural relationships)
- **Redis**: Caching and message queue for asynchronous tasks

## 2.3 Microservices Architecture

### Service Catalog

| Service Name | Technology | Port | Responsibilities | Dependencies |
|--------------|------------|------|------------------|--------------|
| **API Gateway** | Kong/Nginx | 80/443 | Routing, rate limiting, SSL termination | None |
| **Auth Service** | FastAPI | 8001 | Authentication, authorization, user management | PostgreSQL, Redis |
| **Project Manager** | FastAPI | 8002 | Repository management, project configuration | PostgreSQL, GitHub API |
| **Analysis Service** | FastAPI | 8003 | Analysis orchestration, result aggregation | PostgreSQL, Redis, Analysis Workers |
| **Code Review Engine** | Python/Celery | N/A | AST parsing, code analysis, issue detection | LLM API, PostgreSQL |
| **Architecture Analyzer** | Python/Celery | N/A | Dependency graph analysis, drift detection | Neo4j, PostgreSQL |
| **Agentic AI Service** | Python/Celery | N/A | LLM integration, prompt engineering | OpenAI API, Anthropic API |
| **Webhook Handler** | FastAPI | 8004 | GitHub webhook processing | Redis, GitHub API |
| **Metrics Service** | FastAPI | 8005 | Quality metrics calculation, reporting | PostgreSQL, Neo4j |

### Service Communication

- **Synchronous**: REST APIs over HTTP/HTTPS
- **Asynchronous**: Message queue (Redis/Celery) for long-running tasks
- **Event-driven**: Webhooks for external integrations

## 2.4 Data Flow Architecture

### Pull Request Review Flow

```
1. GitHub → Webhook Handler: PR event (opened/synchronize)
2. Webhook Handler → Redis: Queue analysis task
3. Redis → Code Review Engine: Dequeue task
4. Code Review Engine → GitHub API: Fetch PR diff
5. Code Review Engine → AST Parser: Parse source code
6. AST Parser → Code Review Engine: Return AST
7. Code Review Engine → Architecture Analyzer: Get dependency context
8. Architecture Analyzer → Neo4j: Query graph
9. Neo4j → Architecture Analyzer: Return graph data
10. Architecture Analyzer → Code Review Engine: Return context
11. Code Review Engine → Agentic AI: Send code + context
12. Agentic AI → LLM API: Analysis request
13. LLM API → Agentic AI: Analysis response
14. Agentic AI → Code Review Engine: Structured results
15. Code Review Engine → PostgreSQL: Store analysis results
16. Code Review Engine → Neo4j: Update dependency graph
17. Code Review Engine → GitHub API: Post review comments
18. Code Review Engine → Notification Service: Send notification
```

See detailed diagram: `docs/diagram/data-flow-diagram.puml`

## 2.5 Component Interaction Diagram

See: `docs/diagram/component-interaction.puml`

---

# 3. Database Design

## 3.1 Entity Relationship Diagram (ERD)

### PostgreSQL Database Schema

The PostgreSQL database is organized into logical modules:

#### User Management Module
See: `docs/diagram/erd-postgresql-user-management.puml`
- **Entities**: User, Session, AuditLog
- **Purpose**: Authentication, authorization, and audit trail

#### Project Management Module
See: `docs/diagram/erd-postgresql-project-management.puml`
- **Entities**: Project, ProjectMember, AnalysisConfig
- **Purpose**: Repository management and team collaboration

#### Code Analysis Module
See: `docs/diagram/erd-postgresql-code-analysis.puml`
- **Entities**: PullRequest, Analysis, Issue, Comment, ComplianceCheck
- **Purpose**: PR review and issue tracking

#### Quality Metrics Module
See: `docs/diagram/erd-postgresql-quality-metrics.puml`
- **Entities**: QualityMetric, TaskQueue
- **Purpose**: Quality tracking and task management

### Neo4j Graph Database Schema

The Neo4j graph database stores code structure and relationships:

#### Code Entity Nodes
See: `docs/diagram/erd-neo4j-code-entities.puml`
- **Nodes**: Module, Class, Function
- **Purpose**: Code structure representation

#### Dependency Relationships
See: `docs/diagram/erd-neo4j-dependencies.puml`
- **Relationship**: DEPENDS_ON
- **Purpose**: Module, class, and function dependencies

#### Call Relationships
See: `docs/diagram/erd-neo4j-calls.puml`
- **Relationship**: CALLS
- **Purpose**: Function and method call tracking

#### Inheritance Relationships
See: `docs/diagram/erd-neo4j-inheritance.puml`
- **Relationships**: INHERITS, IMPLEMENTS, EXTENDS
- **Purpose**: Class hierarchy and interface implementation

#### Complete Graph Model
See: `docs/diagram/erd-neo4j-complete-graph.puml`
- **Overview**: Complete architecture with all nodes and relationships
- **Purpose**: Comprehensive view of code architecture

### Complete ERD (All Entities)
See: `docs/diagram/entity-relationship-diagram.puml` (Original comprehensive diagram)

## 3.2 PostgreSQL Schema

### 3.2.1 Users Table

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('guest', 'user', 'programmer', 'reviewer', 'manager', 'admin')),
    is_active BOOLEAN DEFAULT TRUE,
    email_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    failed_login_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMP,
    CONSTRAINT username_format CHECK (username ~ '^[a-zA-Z][a-zA-Z0-9_]{2,29}$'),
    CONSTRAINT email_format CHECK (email ~ '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(LOWER(username));
CREATE INDEX idx_users_role ON users(role);
```

### 3.2.2 Sessions Table

```sql
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    access_token VARCHAR(500) NOT NULL,
    refresh_token VARCHAR(500),
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45),
    user_agent TEXT,
    is_revoked BOOLEAN DEFAULT FALSE,
    CONSTRAINT valid_expiry CHECK (expires_at > created_at)
);

CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_sessions_access_token ON sessions(access_token);
CREATE INDEX idx_sessions_expires_at ON sessions(expires_at);
```

### 3.2.3 Projects Table

```sql
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    github_url VARCHAR(500) UNIQUE NOT NULL,
    repository_id VARCHAR(100) NOT NULL,
    default_branch VARCHAR(100) DEFAULT 'main',
    webhook_secret VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_analyzed TIMESTAMP,
    CONSTRAINT github_url_format CHECK (github_url ~ '^https://github\.com/[a-zA-Z0-9-]+/[a-zA-Z0-9._-]+$')
);

CREATE INDEX idx_projects_owner_id ON projects(owner_id);
CREATE INDEX idx_projects_github_url ON projects(github_url);
CREATE INDEX idx_projects_is_active ON projects(is_active);
```

### 3.2.4 Project Members Table

```sql
CREATE TABLE project_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('owner', 'maintainer', 'contributor', 'viewer')),
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(project_id, user_id)
);

CREATE INDEX idx_project_members_project_id ON project_members(project_id);
CREATE INDEX idx_project_members_user_id ON project_members(user_id);
```

### 3.2.5 Pull Requests Table

```sql
CREATE TABLE pull_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    pr_number INTEGER NOT NULL,
    github_pr_id VARCHAR(100) NOT NULL,
    title VARCHAR(500) NOT NULL,
    author VARCHAR(100) NOT NULL,
    source_branch VARCHAR(100) NOT NULL,
    target_branch VARCHAR(100) NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('open', 'closed', 'merged')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    closed_at TIMESTAMP,
    UNIQUE(project_id, pr_number)
);

CREATE INDEX idx_pull_requests_project_id ON pull_requests(project_id);
CREATE INDEX idx_pull_requests_status ON pull_requests(status);
CREATE INDEX idx_pull_requests_author ON pull_requests(author);
```

### 3.2.6 Analyses Table

```sql
CREATE TABLE analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pr_id UUID NOT NULL REFERENCES pull_requests(id) ON DELETE CASCADE,
    status VARCHAR(20) NOT NULL CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    processing_time INTEGER, -- seconds
    total_issues INTEGER DEFAULT 0,
    critical_issues INTEGER DEFAULT 0,
    high_issues INTEGER DEFAULT 0,
    medium_issues INTEGER DEFAULT 0,
    low_issues INTEGER DEFAULT 0,
    quality_score DECIMAL(5,2),
    error_message TEXT,
    CONSTRAINT valid_completion CHECK (
        (status = 'completed' AND completed_at IS NOT NULL) OR
        (status != 'completed' AND completed_at IS NULL)
    )
);

CREATE INDEX idx_analyses_pr_id ON analyses(pr_id);
CREATE INDEX idx_analyses_status ON analyses(status);
CREATE INDEX idx_analyses_completed_at ON analyses(completed_at);
```

### 3.2.7 Issues Table

```sql
CREATE TABLE issues (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID NOT NULL REFERENCES analyses(id) ON DELETE CASCADE,
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('critical', 'high', 'medium', 'low')),
    category VARCHAR(100) NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    suggestion TEXT,
    file_path VARCHAR(500) NOT NULL,
    line_number INTEGER NOT NULL,
    code_snippet TEXT,
    rule_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_feedback VARCHAR(20) CHECK (user_feedback IN ('accept', 'dismiss', 'false_positive')),
    feedback_comment TEXT,
    feedback_at TIMESTAMP
);

CREATE INDEX idx_issues_analysis_id ON issues(analysis_id);
CREATE INDEX idx_issues_severity ON issues(severity);
CREATE INDEX idx_issues_category ON issues(category);
CREATE INDEX idx_issues_file_path ON issues(file_path);
```

### 3.2.8 Quality Metrics Table

```sql
CREATE TABLE quality_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    metric_date DATE NOT NULL,
    total_lines INTEGER,
    code_coverage DECIMAL(5,2),
    avg_complexity DECIMAL(5,2),
    technical_debt INTEGER, -- hours
    maintainability_index DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(project_id, metric_date)
);

CREATE INDEX idx_quality_metrics_project_id ON quality_metrics(project_id);
CREATE INDEX idx_quality_metrics_date ON quality_metrics(metric_date);
```

### 3.2.9 Audit Logs Table

```sql
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    resource_id UUID,
    details JSONB,
    ip_address VARCHAR(45),
    user_agent TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp);
CREATE INDEX idx_audit_logs_resource ON audit_logs(resource_type, resource_id);
```


## 3.3 Neo4j Graph Database Schema

### 3.3.1 Node Types

#### Module Node
```cypher
CREATE CONSTRAINT module_unique IF NOT EXISTS
FOR (m:Module) REQUIRE m.id IS UNIQUE;

CREATE INDEX module_project IF NOT EXISTS
FOR (m:Module) ON (m.project_id);

// Properties:
// - id: UUID
// - project_id: UUID
// - name: String
// - path: String
// - language: String
// - lines_of_code: Integer
// - complexity: Integer
// - created_at: DateTime
// - updated_at: DateTime
```

#### Class Node
```cypher
CREATE CONSTRAINT class_unique IF NOT EXISTS
FOR (c:Class) REQUIRE c.id IS UNIQUE;

// Properties:
// - id: UUID
// - module_id: UUID
// - name: String
// - file_path: String
// - line_start: Integer
// - line_end: Integer
// - complexity: Integer
// - methods_count: Integer
// - is_abstract: Boolean
```

#### Function Node
```cypher
CREATE CONSTRAINT function_unique IF NOT EXISTS
FOR (f:Function) REQUIRE f.id IS UNIQUE;

// Properties:
// - id: UUID
// - parent_id: UUID (module or class)
// - name: String
// - file_path: String
// - line_start: Integer
// - line_end: Integer
// - complexity: Integer
// - parameters_count: Integer
// - is_async: Boolean
```

### 3.3.2 Relationship Types

#### DEPENDS_ON
```cypher
// Module A depends on Module B
CREATE (a:Module)-[:DEPENDS_ON {
    type: 'import',
    strength: 5,
    created_at: datetime()
}]->(b:Module)

// Properties:
// - type: String (import, call, inheritance, composition)
// - strength: Integer (1-10, based on usage frequency)
// - created_at: DateTime
// - last_updated: DateTime
```

#### CALLS
```cypher
// Function A calls Function B
CREATE (a:Function)-[:CALLS {
    call_count: 3,
    is_recursive: false
}]->(b:Function)

// Properties:
// - call_count: Integer
// - is_recursive: Boolean
// - call_sites: List<Integer> (line numbers)
```

#### INHERITS
```cypher
// Class A inherits from Class B
CREATE (a:Class)-[:INHERITS {
    inheritance_type: 'single'
}]->(b:Class)

// Properties:
// - inheritance_type: String (single, multiple, interface)
```

#### CONTAINS
```cypher
// Module contains Class
CREATE (m:Module)-[:CONTAINS]->(c:Class)

// Class contains Function
CREATE (c:Class)-[:CONTAINS]->(f:Function)
```

### 3.3.3 Common Queries

#### Find Circular Dependencies
```cypher
MATCH path = (m:Module)-[:DEPENDS_ON*2..10]->(m)
WHERE m.project_id = $project_id
RETURN path, length(path) as cycle_length
ORDER BY cycle_length
```

#### Calculate Module Coupling
```cypher
MATCH (m:Module {project_id: $project_id})
OPTIONAL MATCH (m)-[r:DEPENDS_ON]->()
WITH m, count(r) as outgoing
OPTIONAL MATCH ()-[r:DEPENDS_ON]->(m)
WITH m, outgoing, count(r) as incoming
RETURN m.name, outgoing, incoming, (outgoing + incoming) as total_coupling
ORDER BY total_coupling DESC
```

#### Find Layer Violations
```cypher
// Assuming layers are defined by path patterns
MATCH (presentation:Module)-[:DEPENDS_ON]->(data:Module)
WHERE presentation.path STARTS WITH 'src/ui/'
  AND data.path STARTS WITH 'src/data/'
  AND NOT exists((presentation)-[:DEPENDS_ON]->(:Module {path: 'src/business/'}))
RETURN presentation.name, data.name
```

#### Get Dependency Graph for Visualization
```cypher
MATCH (m:Module {project_id: $project_id})
OPTIONAL MATCH (m)-[r:DEPENDS_ON]->(target:Module)
RETURN m, collect({target: target, relationship: r}) as dependencies
```

---

# 4. Component Design

## 4.1 Class Diagram

The system's class structure is organized into modular diagrams by functional domain for improved readability and maintainability.

### Modular Class Diagrams

#### User Management Domain
See: `docs/diagram/class-user-management.puml`
- **Components**: User, Session, AuthService, JWTManager, PasswordHasher, PermissionChecker
- **Repositories**: UserRepository, SessionRepository
- **DTOs**: RegisterDTO, LoginDTO, UserProfile, TokenPayload
- **Purpose**: Authentication, authorization, session management, audit logging

#### Project Management Domain
See: `docs/diagram/class-project-management.puml`
- **Components**: Project, ProjectMember, ProjectService, WebhookService, AnalysisConfig, ConfigService
- **Repositories**: ProjectRepository, ConfigRepository
- **DTOs**: CreateProjectDTO, UpdateProjectDTO, ProjectConfig, QualityMetrics
- **Purpose**: GitHub repository integration, team collaboration, project configuration

#### Code Analysis Domain
See: `docs/diagram/class-code-analysis.puml`
- **Components**: PullRequest, Analysis, Issue, Comment, CodeReviewEngine, ParserService, IssueDetector
- **Repositories**: AnalysisRepository, IssueRepository, CommentRepository
- **DTOs**: AnalysisReport, IssueContext, ValidationResult, ComparisonResult
- **Purpose**: PR analysis, issue detection, code review, GitHub comment integration

#### Architecture Analysis Domain
See: `docs/diagram/class-architecture-analysis.puml`
- **Components**: CodeEntity, Dependency, ArchitectureAnalyzer, ASTParser, GraphBuilder, CircularDependencyDetector, LayerAnalyzer
- **Repositories**: EntityRepository, DependencyRepository
- **DTOs**: EntityMetrics, CouplingMetrics, DriftReport, GraphVisualization, Violation
- **Purpose**: Code structure analysis, dependency graph, circular dependency detection, layer validation

#### AI Integration Domain
See: `docs/diagram/class-ai-integration.puml`
- **Components**: AgenticAI, LLMClient, ContextBuilder, PromptManager, ResponseParser, EmbeddingService, VectorStore
- **Support**: RateLimiter, CacheManager, TokenCounter
- **DTOs**: AIAnalysis, ReviewComment, CodeSuggestion, Pattern, Context, LLMResponse
- **Purpose**: LLM integration, AI-powered code review, semantic search, prompt management

#### Quality Metrics Domain
See: `docs/diagram/class-quality-metrics.puml`
- **Components**: QualityMetric, ComplianceCheck, MetricsService, MetricCalculator, ComplexityCalculator, CoverageCalculator, TechnicalDebtCalculator
- **Analysis**: MetricsAggregator, TrendAnalyzer, DashboardBuilder
- **Repositories**: MetricsRepository, ComplianceRepository
- **DTOs**: MetricDelta, MetricTrend, Dashboard, Report, ComparisonReport
- **Purpose**: Quality metrics calculation, compliance verification, trend analysis, dashboard generation

#### Infrastructure Domain
See: `docs/diagram/class-infrastructure.puml`
- **Components**: GitHubClient, Neo4jClient, RedisClient, PostgreSQLClient, TaskQueue
- **Services**: EmailService, LoggerService, MonitoringService, CacheService, FileStorageService
- **Support**: WebhookHandler, RateLimiter, ConfigurationManager
- **DTOs**: PRData, File, WebhookConfig, Node, Relationship, Task, HealthStatus
- **Purpose**: External integrations, database clients, task queue, monitoring, caching

### Complete Class Diagram
See: `docs/diagram/class-diagram.puml` (Original comprehensive diagram with all domains)

## 4.2 Core Components

### 4.2.1 Authentication Service

**Purpose**: Manages user authentication, authorization, and session management.

**Technologies**: FastAPI, PyJWT, bcrypt, Redis

**Class Structure**:
```python
class AuthService:
    """Main authentication service"""
    
    def __init__(self, db: Database, redis: RedisClient, jwt_manager: JWTManager):
        self.db = db
        self.redis = redis
        self.jwt_manager = jwt_manager
    
    async def register(self, user_data: RegisterDTO) -> User:
        """
        Register a new user
        
        Args:
            user_data: Registration data (username, email, password)
        
        Returns:
            Created user object
        
        Raises:
            ValidationError: Invalid input data
            DuplicateUserError: Username or email already exists
        """
        # Validate input
        self._validate_registration_data(user_data)
        
        # Check for duplicates
        if await self.db.user_exists(user_data.email, user_data.username):
            raise DuplicateUserError("Email or username already exists")
        
        # Hash password
        password_hash = bcrypt.hashpw(
            user_data.password.encode('utf-8'),
            bcrypt.gensalt(rounds=12)
        )
        
        # Create user
        user = await self.db.create_user({
            'username': user_data.username,
            'email': user_data.email,
            'password_hash': password_hash,
            'role': 'user'
        })
        
        # Send verification email
        await self._send_verification_email(user)
        
        return user
    
    async def login(self, credentials: LoginDTO) -> SessionDTO:
        """
        Authenticate user and create session
        
        Args:
            credentials: Login credentials (email/username, password)
        
        Returns:
            Session with access and refresh tokens
        
        Raises:
            AuthenticationError: Invalid credentials
            AccountLockedError: Account is locked
        """
        # Find user
        user = await self.db.find_user_by_email_or_username(credentials.identifier)
        if not user:
            raise AuthenticationError("Invalid credentials")
        
        # Check account status
        if user.locked_until and user.locked_until > datetime.now():
            raise AccountLockedError(f"Account locked until {user.locked_until}")
        
        # Verify password
        if not bcrypt.checkpw(credentials.password.encode('utf-8'), user.password_hash):
            await self._handle_failed_login(user)
            raise AuthenticationError("Invalid credentials")
        
        # Reset failed attempts
        await self.db.reset_failed_login_attempts(user.id)
        
        # Generate tokens
        access_token = self.jwt_manager.create_access_token(user)
        refresh_token = self.jwt_manager.create_refresh_token(user)
        
        # Create session
        session = await self.db.create_session({
            'user_id': user.id,
            'access_token': access_token,
            'refresh_token': refresh_token,
            'expires_at': datetime.now() + timedelta(hours=24)
        })
        
        # Update last login
        await self.db.update_last_login(user.id)
        
        return SessionDTO(
            access_token=access_token,
            refresh_token=refresh_token,
            user=UserDTO.from_orm(user)
        )
    
    async def validate_token(self, token: str) -> User:
        """Validate JWT token and return user"""
        try:
            payload = self.jwt_manager.decode_token(token)
            user_id = payload.get('sub')
            
            # Check if token is revoked
            if await self.redis.is_token_revoked(token):
                raise TokenRevokedError("Token has been revoked")
            
            # Get user
            user = await self.db.get_user(user_id)
            if not user or not user.is_active:
                raise AuthenticationError("User not found or inactive")
            
            return user
        except jwt.ExpiredSignatureError:
            raise TokenExpiredError("Token has expired")
        except jwt.InvalidTokenError:
            raise AuthenticationError("Invalid token")
```

**Key Methods**:
- `register(user_data: RegisterDTO) -> User`: Register new user
- `login(credentials: LoginDTO) -> SessionDTO`: Authenticate and create session
- `logout(token: str) -> None`: Revoke session
- `validate_token(token: str) -> User`: Validate JWT token
- `refresh_token(refresh_token: str) -> SessionDTO`: Refresh access token
- `change_password(user_id: UUID, old_password: str, new_password: str) -> None`: Change password


---

# 5. Security Design

For complete security design including authentication mechanisms, authorization model, encryption strategies, and audit logging, see: **[SDD-Security-Deployment.md](./SDD-Security-Deployment.md)**

Summary:
- **Authentication**: JWT tokens with bcrypt password hashing
- **Authorization**: Role-Based Access Control (RBAC) with 6 roles
- **Encryption**: TLS 1.3 in transit, AES-256 at rest
- **Input Validation**: SQL injection, XSS, CSRF protection
- **Secrets Management**: AWS Secrets Manager integration
- **Audit Logging**: Comprehensive logging with 7-year retention

---

# 6. Interface Design

## 6.1 API Endpoints Summary

For complete API specifications with request/response examples, see: **[ProjectName-SRS_v2.1.md](./ProjectName-SRS_v2.1.md) Section 7**

### Authentication APIs
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User authentication
- `POST /api/auth/refresh` - Token refresh
- `POST /api/auth/logout` - Session termination

### Repository Management APIs
- `POST /api/repositories` - Add repository
- `GET /api/repositories` - List repositories
- `GET /api/repositories/{id}` - Get repository details
- `DELETE /api/repositories/{id}` - Remove repository

### Analysis APIs
- `GET /api/analyses/{id}` - Get analysis results
- `POST /api/analyses/{id}/feedback` - Submit feedback
- `GET /api/analyses/{id}/issues` - List issues

### Architecture APIs
- `GET /api/architecture/{project_id}/graph` - Get dependency graph
- `GET /api/architecture/{project_id}/drift` - Get drift report
- `GET /api/architecture/{project_id}/metrics` - Get architecture metrics

### Webhook APIs
- `POST /api/webhooks/github` - GitHub webhook receiver

### Metrics APIs
- `GET /api/metrics/{project_id}` - Get quality metrics
- `GET /api/metrics/{project_id}/trends` - Get trend data
- `POST /api/metrics/{project_id}/export` - Export report

## 6.2 User Interface Screens

### 6.2.1 Dashboard
**Purpose**: Main interface showing project overview and quick actions

**Components**:
- Project list with quality scores
- Recent analyses summary
- Quick action buttons (Add Repository, View Reports)
- Quality trend charts
- Notification center

**Wireframe**: See `docs/wireframes/dashboard.png`

### 6.2.2 Repository Management
**Purpose**: List and manage connected repositories

**Components**:
- Repository cards with status indicators
- Add repository button
- Search and filter controls
- Sync and settings actions

### 6.2.3 Analysis Results Viewer
**Purpose**: Display detailed code review results

**Components**:
- Issue list grouped by severity
- File tree navigation
- Code snippet viewer with inline comments
- Accept/Dismiss actions
- Suggestion details

### 6.2.4 Architecture Visualization
**Purpose**: Interactive dependency graph display

**Components**:
- D3.js force-directed graph
- Zoom and pan controls
- Filter panel (entity type, complexity, severity)
- Node details sidebar
- Export options (PNG, SVG, JSON)
- Circular dependency highlights

### 6.2.5 Quality Metrics Dashboard
**Purpose**: Display quality metrics and trends

**Components**:
- Quality score gauge
- Issue breakdown pie chart
- Trend line charts (quality score, issues, complexity)
- Comparison table (current vs. previous)
- Export report button

### 6.2.6 Settings and Configuration
**Purpose**: System and project configuration

**Components**:
- Analysis rules configuration
- Compliance standards selection
- LLM model selection
- Notification preferences
- Integration settings (GitHub, Slack)
- User management (admin only)

## 6.3 WebSocket Events

For real-time updates:

```typescript
// Client subscribes to analysis updates
socket.on('analysis:started', (data) => {
  console.log(`Analysis ${data.analysis_id} started`);
});

socket.on('analysis:progress', (data) => {
  console.log(`Progress: ${data.percentage}%`);
});

socket.on('analysis:completed', (data) => {
  console.log(`Analysis completed with ${data.total_issues} issues`);
  // Refresh UI
});

socket.on('analysis:failed', (data) => {
  console.error(`Analysis failed: ${data.error}`);
});
```

---

# 7. Deployment Architecture

For complete deployment architecture including infrastructure details, container orchestration, and CI/CD pipeline, see: **[SDD-Security-Deployment.md](./SDD-Security-Deployment.md) Section 6**

### Architecture Diagrams

- **Deployment Architecture**: `docs/diagram/deployment-architecture.puml`
- **Security Architecture**: `docs/diagram/security-architecture.puml`
- **CI/CD Pipeline**: `docs/diagram/cicd-pipeline.puml`

## 7.1 Container Architecture

### Docker Images

| Service | Base Image | Size | Registry |
|---------|------------|------|----------|
| Frontend | node:18-alpine | ~150MB | ECR |
| API Services | python:3.11-slim | ~200MB | ECR |
| Workers | python:3.11-slim | ~250MB | ECR |
| Nginx | nginx:alpine | ~50MB | ECR |

### Kubernetes Deployment

```yaml
# Example: Analysis Service Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: analysis-service
  namespace: production
spec:
  replicas: 3
  selector:
    matchLabels:
      app: analysis-service
  template:
    metadata:
      labels:
        app: analysis-service
    spec:
      containers:
      - name: analysis-service
        image: <account>.dkr.ecr.us-east-1.amazonaws.com/analysis-service:latest
        ports:
        - containerPort: 8003
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: url
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8003
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8003
          initialDelaySeconds: 10
          periodSeconds: 5
```

## 7.2 Scaling Strategy

### Horizontal Pod Autoscaler (HPA)

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: analysis-service-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: analysis-service
  minReplicas: 3
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### Worker Autoscaling

```python
# Celery worker autoscaling based on queue depth
from celery import Celery

app = Celery('tasks', broker='redis://localhost:6379/0')

app.conf.update(
    worker_autoscaler='10,3',  # max 10, min 3 workers
    worker_prefetch_multiplier=1,
    task_acks_late=True,
)
```

---

# 8. Technology Stack

## 8.1 Frontend

| Technology | Version | Purpose |
|------------|---------|---------|
| React | 18.2+ | UI framework |
| Next.js | 14.0+ | Server-side rendering, routing |
| TypeScript | 5.0+ | Type safety |
| Tailwind CSS | 3.3+ | Styling |
| D3.js | 7.8+ | Graph visualization |
| Cytoscape.js | 3.26+ | Alternative graph library |
| Socket.IO Client | 4.6+ | Real-time updates |
| Axios | 1.6+ | HTTP client |
| React Query | 5.0+ | Data fetching and caching |
| Zustand | 4.4+ | State management |

## 8.2 Backend

| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.11+ | Primary language |
| FastAPI | 0.109+ | Web framework |
| Pydantic | 2.5+ | Data validation |
| SQLAlchemy | 2.0+ | ORM |
| Alembic | 1.13+ | Database migrations |
| Celery | 5.3+ | Async task queue |
| PyJWT | 2.8+ | JWT handling |
| bcrypt | 4.1+ | Password hashing |
| httpx | 0.26+ | Async HTTP client |
| pytest | 7.4+ | Testing framework |

## 8.3 Databases

| Technology | Version | Purpose |
|------------|---------|---------|
| PostgreSQL | 15+ | Relational data |
| Neo4j | 5.15+ | Graph database |
| Redis | 7.2+ | Cache and queue |

## 8.4 Infrastructure

| Technology | Version | Purpose |
|------------|---------|---------|
| Docker | 24.0+ | Containerization |
| Kubernetes | 1.28+ | Container orchestration |
| Terraform | 1.6+ | Infrastructure as Code |
| AWS EKS | - | Managed Kubernetes |
| AWS RDS | - | Managed PostgreSQL |
| AWS ElastiCache | - | Managed Redis |
| Kong | 3.5+ | API Gateway |
| Nginx | 1.25+ | Reverse proxy |

## 8.5 Monitoring & Logging

| Technology | Version | Purpose |
|------------|---------|---------|
| Prometheus | 2.48+ | Metrics collection |
| Grafana | 10.2+ | Metrics visualization |
| Elasticsearch | 8.11+ | Log storage |
| Logstash | 8.11+ | Log processing |
| Kibana | 8.11+ | Log visualization |
| Jaeger | 1.52+ | Distributed tracing |
| Sentry | - | Error tracking |

## 8.6 CI/CD

| Technology | Version | Purpose |
|------------|---------|---------|
| GitHub Actions | - | CI/CD pipeline |
| Docker Compose | 2.23+ | Local development |
| SonarQube | 10.3+ | Code quality |
| Snyk | - | Security scanning |
| Trivy | 0.48+ | Container scanning |

---

# 9. Architecture Decision Records (ADR)

## ADR-001: Use Neo4j for Dependency Graph Storage

**Status**: Accepted

**Context**: Need to store and query complex dependency relationships between code entities.

**Decision**: Use Neo4j graph database instead of relational database.

**Rationale**:
- Graph databases are optimized for relationship queries
- Cypher query language is intuitive for graph traversal
- Efficient circular dependency detection using graph algorithms
- Better performance for deep relationship queries
- Native support for graph visualization

**Consequences**:
- Additional database to manage
- Team needs to learn Cypher
- Increased infrastructure complexity
- Better query performance for architectural analysis

---

## ADR-002: Use FastAPI for Backend Services

**Status**: Accepted

**Context**: Need to choose a Python web framework for microservices.

**Decision**: Use FastAPI instead of Django or Flask.

**Rationale**:
- Async/await support for better performance
- Automatic OpenAPI documentation
- Built-in data validation with Pydantic
- Type hints for better code quality
- High performance (comparable to Node.js)
- Modern Python 3.11+ features

**Consequences**:
- Smaller ecosystem compared to Django
- Less built-in functionality (need to integrate libraries)
- Better performance and developer experience

---

## ADR-003: Multi-LLM Strategy with Fallback

**Status**: Accepted

**Context**: LLM APIs can be unreliable (rate limits, outages, quality variations).

**Decision**: Implement primary (GPT-4) and secondary (Claude 3.5) LLM with automatic fallback.

**Rationale**:
- Improved reliability and uptime
- Cost optimization (use cheaper model as fallback)
- Quality comparison between models
- Vendor lock-in mitigation

**Consequences**:
- Increased complexity in LLM integration
- Need to manage multiple API keys
- Prompt engineering for multiple models
- Better system reliability

---

## ADR-004: Microservices Architecture

**Status**: Accepted

**Context**: System has distinct functional areas with different scaling needs.

**Decision**: Implement microservices architecture instead of monolith.

**Rationale**:
- Independent scaling of services
- Technology flexibility per service
- Fault isolation
- Easier team organization
- Better deployment flexibility

**Consequences**:
- Increased operational complexity
- Need for service mesh/API gateway
- Distributed system challenges (consistency, debugging)
- Better scalability and maintainability

---

## ADR-005: Celery for Async Task Processing

**Status**: Accepted

**Context**: Code analysis is CPU-intensive and should not block API requests.

**Decision**: Use Celery with Redis as message broker for async tasks.

**Rationale**:
- Mature and battle-tested
- Good Python integration
- Supports task retries and scheduling
- Monitoring tools available
- Horizontal scaling of workers

**Consequences**:
- Additional infrastructure (Redis)
- Complexity in task management
- Need for task monitoring
- Better API responsiveness

---

**End of Software Design Document**

---

**Document Approval**

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Author | BaiXuan Zhang | | 2026-02-16 |
| Reviewer | Dr. Siraprapa | | |
| Approver | | | |

