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
| v2.0 | 2026-02-13 | BaiXuan Zhang | Dr. Siraprapa | Added system architecture, database schema, component design |
| v2.1 | 2026-02-16 | BaiXuan Zhang | Dr. Siraprapa | Added security design, deployment architecture, complete database design, API specs, architecture diagrams |
| v2.1 | 2026-02-19 | BaiXuan Zhang | Dr. Siraprapa | Completed RBAC component design, updated technology stack, added ADR-005, aligned with enterprise_rbac_auth implementation |

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

Stores user account information for authentication and authorization.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, auto-generated | Unique user identifier |
| username | VARCHAR(50) | UNIQUE, NOT NULL | Login username (3-30 chars, alphanumeric + underscore, starts with letter) |
| email | VARCHAR(100) | UNIQUE, NOT NULL | User email address |
| password_hash | VARCHAR(255) | NOT NULL | bcrypt-hashed password |
| role | VARCHAR(20) | NOT NULL, CHECK | One of: guest, user, programmer, reviewer, manager, admin |
| is_active | BOOLEAN | DEFAULT TRUE | Account active status |
| email_verified | BOOLEAN | DEFAULT FALSE | Email verification status |
| created_at | TIMESTAMP | DEFAULT NOW | Account creation time |
| updated_at | TIMESTAMP | DEFAULT NOW | Last update time |
| last_login | TIMESTAMP | NULLABLE | Last successful login time |
| failed_login_attempts | INTEGER | DEFAULT 0 | Consecutive failed login count |
| locked_until | TIMESTAMP | NULLABLE | Account lockout expiry time |

Indexes: email, username (case-insensitive), role

### 3.2.2 Sessions Table

Tracks active user sessions for token management and audit.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, auto-generated | Unique session identifier |
| user_id | UUID | FK → users, CASCADE | Owning user |
| access_token | VARCHAR(500) | NOT NULL | JWT access token |
| refresh_token | VARCHAR(500) | NULLABLE | JWT refresh token |
| expires_at | TIMESTAMP | NOT NULL | Session expiry time (must be after created_at) |
| created_at | TIMESTAMP | DEFAULT NOW | Session creation time |
| ip_address | VARCHAR(45) | NULLABLE | Client IP address |
| user_agent | TEXT | NULLABLE | Client user agent string |
| is_revoked | BOOLEAN | DEFAULT FALSE | Manual revocation flag |

Indexes: user_id, access_token, expires_at

### 3.2.3 Projects Table

Stores connected GitHub repository configurations.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, auto-generated | Unique project identifier |
| owner_id | UUID | FK → users, CASCADE | Project owner |
| name | VARCHAR(200) | NOT NULL | Display name |
| github_url | VARCHAR(500) | UNIQUE, NOT NULL | GitHub repository URL (format: https://github.com/{owner}/{repo}) |
| repository_id | VARCHAR(100) | NOT NULL | GitHub repository ID |
| default_branch | VARCHAR(100) | DEFAULT 'main' | Default analysis branch |
| webhook_secret | VARCHAR(255) | NULLABLE | HMAC webhook verification secret |
| is_active | BOOLEAN | DEFAULT TRUE | Project active status |
| created_at | TIMESTAMP | DEFAULT NOW | Creation time |
| updated_at | TIMESTAMP | DEFAULT NOW | Last update time |
| last_analyzed | TIMESTAMP | NULLABLE | Last analysis completion time |

Indexes: owner_id, github_url, is_active

### 3.2.4 Project Members Table

Manages team membership and per-project role assignments.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, auto-generated | Unique membership identifier |
| project_id | UUID | FK → projects, CASCADE | Associated project |
| user_id | UUID | FK → users, CASCADE | Associated user |
| role | VARCHAR(20) | NOT NULL, CHECK | One of: owner, maintainer, contributor, viewer |
| joined_at | TIMESTAMP | DEFAULT NOW | Membership creation time |

Constraints: UNIQUE(project_id, user_id). Indexes: project_id, user_id

### 3.2.5 Pull Requests Table

Records GitHub pull requests submitted for analysis.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, auto-generated | Unique PR record identifier |
| project_id | UUID | FK → projects, CASCADE | Associated project |
| pr_number | INTEGER | NOT NULL | GitHub PR number |
| github_pr_id | VARCHAR(100) | NOT NULL | GitHub internal PR ID |
| title | VARCHAR(500) | NOT NULL | PR title |
| author | VARCHAR(100) | NOT NULL | GitHub username of PR author |
| source_branch | VARCHAR(100) | NOT NULL | Feature branch name |
| target_branch | VARCHAR(100) | NOT NULL | Target merge branch |
| status | VARCHAR(20) | NOT NULL, CHECK | One of: open, closed, merged |
| created_at | TIMESTAMP | DEFAULT NOW | PR creation time |
| updated_at | TIMESTAMP | DEFAULT NOW | Last update time |
| closed_at | TIMESTAMP | NULLABLE | PR close/merge time |

Constraints: UNIQUE(project_id, pr_number). Indexes: project_id, status, author

### 3.2.6 Analyses Table

Stores analysis job status and aggregate results per pull request.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, auto-generated | Unique analysis identifier |
| pr_id | UUID | FK → pull_requests, CASCADE | Associated pull request |
| status | VARCHAR(20) | NOT NULL, CHECK | One of: pending, processing, completed, failed |
| started_at | TIMESTAMP | DEFAULT NOW | Analysis start time |
| completed_at | TIMESTAMP | NULLABLE | Analysis completion time (required when status=completed) |
| processing_time | INTEGER | NULLABLE | Duration in seconds |
| total_issues | INTEGER | DEFAULT 0 | Total issue count |
| critical_issues | INTEGER | DEFAULT 0 | Critical severity count |
| high_issues | INTEGER | DEFAULT 0 | High severity count |
| medium_issues | INTEGER | DEFAULT 0 | Medium severity count |
| low_issues | INTEGER | DEFAULT 0 | Low severity count |
| quality_score | DECIMAL(5,2) | NULLABLE | Computed quality score (0-100) |
| error_message | TEXT | NULLABLE | Failure reason if status=failed |

Indexes: pr_id, status, completed_at

### 3.2.7 Issues Table

Stores individual code issues detected during analysis.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, auto-generated | Unique issue identifier |
| analysis_id | UUID | FK → analyses, CASCADE | Parent analysis |
| severity | VARCHAR(20) | NOT NULL, CHECK | One of: critical, high, medium, low |
| category | VARCHAR(100) | NOT NULL | Issue category (security, performance, style, etc.) |
| title | VARCHAR(200) | NOT NULL | Short issue title |
| description | TEXT | NOT NULL | Detailed issue description |
| suggestion | TEXT | NULLABLE | AI-generated fix suggestion |
| file_path | VARCHAR(500) | NOT NULL | Relative file path |
| line_number | INTEGER | NOT NULL | Line number in file |
| code_snippet | TEXT | NULLABLE | Relevant code excerpt |
| rule_id | VARCHAR(100) | NULLABLE | Triggered rule identifier |
| created_at | TIMESTAMP | DEFAULT NOW | Issue creation time |
| user_feedback | VARCHAR(20) | CHECK, NULLABLE | One of: accept, dismiss, false_positive |
| feedback_comment | TEXT | NULLABLE | User feedback comment |
| feedback_at | TIMESTAMP | NULLABLE | Feedback submission time |

Indexes: analysis_id, severity, category, file_path

### 3.2.8 Quality Metrics Table

Stores daily aggregated quality metrics per project for trend analysis.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, auto-generated | Unique metric record identifier |
| project_id | UUID | FK → projects, CASCADE | Associated project |
| metric_date | DATE | NOT NULL | Metric snapshot date |
| total_lines | INTEGER | NULLABLE | Total lines of code |
| code_coverage | DECIMAL(5,2) | NULLABLE | Test coverage percentage |
| avg_complexity | DECIMAL(5,2) | NULLABLE | Average cyclomatic complexity |
| technical_debt | INTEGER | NULLABLE | Estimated technical debt in hours |
| maintainability_index | DECIMAL(5,2) | NULLABLE | Maintainability index score |
| created_at | TIMESTAMP | DEFAULT NOW | Record creation time |

Constraints: UNIQUE(project_id, metric_date). Indexes: project_id, metric_date

### 3.2.9 Audit Logs Table

Immutable record of all security-relevant system actions. No UPDATE or DELETE operations are permitted.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, auto-generated | Unique log entry identifier |
| user_id | UUID | FK → users, SET NULL | Acting user (nullable for system actions) |
| action | VARCHAR(100) | NOT NULL | Action type (e.g., LOGIN, CREATE_USER, UPDATE_USER_ROLE) |
| resource_type | VARCHAR(50) | NOT NULL | Affected resource type |
| resource_id | UUID | NULLABLE | Affected resource identifier |
| details | JSONB | NULLABLE | Additional action context |
| ip_address | VARCHAR(45) | NULLABLE | Client IP address |
| user_agent | TEXT | NULLABLE | Client user agent string |
| timestamp | TIMESTAMP | DEFAULT NOW | Action timestamp |

Indexes: user_id, action, timestamp, (resource_type, resource_id)


## 3.3 Neo4j Graph Database Schema

### 3.3.1 Node Types

#### Module Node

Represents a source code module (file or package). Unique constraint on `id`, indexed by `project_id`.

| Property | Type | Description |
|----------|------|-------------|
| id | UUID | Unique module identifier |
| project_id | UUID | Owning project |
| name | String | Module name |
| path | String | File system path |
| language | String | Programming language |
| lines_of_code | Integer | Total lines of code |
| complexity | Integer | Cyclomatic complexity |
| created_at | DateTime | Creation timestamp |
| updated_at | DateTime | Last update timestamp |

#### Class Node

Represents a class definition within a module. Unique constraint on `id`.

| Property | Type | Description |
|----------|------|-------------|
| id | UUID | Unique class identifier |
| module_id | UUID | Containing module |
| name | String | Class name |
| file_path | String | Source file path |
| line_start | Integer | Start line number |
| line_end | Integer | End line number |
| complexity | Integer | Cyclomatic complexity |
| methods_count | Integer | Number of methods |
| is_abstract | Boolean | Abstract class flag |

#### Function Node

Represents a function or method definition. Unique constraint on `id`.

| Property | Type | Description |
|----------|------|-------------|
| id | UUID | Unique function identifier |
| parent_id | UUID | Containing module or class |
| name | String | Function name |
| file_path | String | Source file path |
| line_start | Integer | Start line number |
| line_end | Integer | End line number |
| complexity | Integer | Cyclomatic complexity |
| parameters_count | Integer | Number of parameters |
| is_async | Boolean | Async function flag |

### 3.3.2 Relationship Types

#### DEPENDS_ON

Directed dependency from one module to another (import, call, inheritance, or composition).

| Property | Type | Description |
|----------|------|-------------|
| type | String | Dependency type: import, call, inheritance, composition |
| strength | Integer | Usage frequency score (1-10) |
| created_at | DateTime | Relationship creation time |
| last_updated | DateTime | Last update time |

#### CALLS

Directed call relationship from one function to another.

| Property | Type | Description |
|----------|------|-------------|
| call_count | Integer | Number of call sites |
| is_recursive | Boolean | Whether the call is recursive |
| call_sites | List\<Integer\> | Line numbers of call sites |

#### INHERITS

Directed inheritance relationship from subclass to superclass.

| Property | Type | Description |
|----------|------|-------------|
| inheritance_type | String | One of: single, multiple, interface |

#### CONTAINS

Structural containment: Module → Class, Class → Function.

### 3.3.3 Common Query Patterns

The following query patterns are used for architectural analysis:

- **Circular Dependency Detection**: Traverse DEPENDS_ON relationships to find cycles of length 2-10 within a project
- **Module Coupling Calculation**: Count incoming and outgoing DEPENDS_ON edges per module; rank by total coupling
- **Layer Violation Detection**: Match DEPENDS_ON edges that skip architectural layers (e.g., presentation → data without passing through service)
- **Dependency Graph Export**: Collect all modules and their DEPENDS_ON targets for visualization rendering

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

**Purpose**: Manages user authentication, JWT token lifecycle, and session management.

**Technologies**: FastAPI, PyJWT, bcrypt, SQLAlchemy

**Implementation**: `enterprise_rbac_auth/services/auth_service.py`

**Class Structure**:

| Method | Signature | Description |
|--------|-----------|-------------|
| `hash_password` | `(password: str) → str` | Hash password using bcrypt with configurable rounds |
| `verify_password` | `(password: str, password_hash: str) → bool` | Verify plain-text password against stored bcrypt hash |
| `generate_token` | `(user_id, username, role) → str` | Generate signed JWT with user_id, username, role, iat, exp, jti claims |
| `validate_token` | `(token: str) → Optional[TokenPayload]` | Decode and validate JWT; returns None on expiry or tampering |
| `refresh_token` | `(token: str) → Optional[str]` | Issue new token if current token is within 10-min refresh window |
| `login` | `(db, username, password, ip_address, device_info) → AuthResult` | Authenticate user, create Session record, update last_login |
| `logout` | `(db, user_id, token) → bool` | Invalidate specific session by setting is_valid=False |
| `invalidate_all_user_sessions` | `(db, user_id) → bool` | Invalidate all active sessions (used on password change / deactivation) |

**Key Design Decisions**:
- Stateless design: no instance state, all methods are `@staticmethod`
- Generic error messages on login failure to prevent username enumeration
- JWT payload includes `jti` (JWT ID) for uniqueness and future revocation support
- Session records stored in PostgreSQL for audit trail; token validity checked via `is_valid` flag

**Design Notes**:
- Stateless design: no instance state, all methods are static
- Generic error messages on login failure to prevent username enumeration
- JWT payload includes `jti` (JWT ID) for uniqueness and future revocation support
- Session records stored in PostgreSQL for audit trail; token validity checked via `is_valid` flag
- The original async design (register, login, validate_token as instance methods) was superseded by the current stateless `@staticmethod` implementation for simplicity and testability

---

### 4.2.2 RBAC Service

**Purpose**: Manages role-based permissions and project-level access control.

**Technologies**: SQLAlchemy, Python Enum

**Implementation**: `enterprise_rbac_auth/services/rbac_service.py`

**Role Hierarchy**:
```
ADMIN > MANAGER > REVIEWER > PROGRAMMER > VISITOR
```

**Permission Matrix**:

| Permission | ADMIN | MANAGER | REVIEWER | PROGRAMMER | VISITOR |
|------------|-------|---------|----------|------------|---------|
| CREATE_USER | ✓ | | | | |
| READ_USER | ✓ | ✓ | | | |
| UPDATE_USER | ✓ | | | | |
| DELETE_USER | ✓ | | | | |
| CREATE_PROJECT | ✓ | ✓ | | ✓ | |
| VIEW_PROJECT | ✓ | ✓ | ✓ | ✓ | ✓ |
| UPDATE_PROJECT | ✓ | ✓ | | ✓ | |
| DELETE_PROJECT | ✓ | ✓ | | ✓ | |
| TRIGGER_ANALYSIS | ✓ | ✓ | ✓ | ✓ | |
| VIEW_ANALYSIS | ✓ | ✓ | ✓ | ✓ | ✓ |
| MANAGE_USERS | ✓ | | | | |
| VIEW_AUDIT_LOGS | ✓ | ✓ | | | |

**Class Structure**:

| Method | Signature | Description |
|--------|-----------|-------------|
| `has_permission` | `(db, user_id, permission) → bool` | Check if user's role includes the requested permission |
| `get_role_permissions` | `(role) → list[Permission]` | Return permission list for a given role from ROLE_PERMISSIONS map |
| `can_access_project` | `(db, user_id, project_id, permission) → bool` | Project access: ADMIN always True; owner always True; others need ProjectAccess grant for VIEW; write permissions denied for non-owners |
| `grant_project_access` | `(db, project_id, user_id, granted_by) → bool` | Create ProjectAccess record; only admin or project owner may grant |
| `revoke_project_access` | `(db, project_id, user_id, revoked_by) → bool` | Delete ProjectAccess record; only admin or project owner may revoke |
| `assign_role` | `(db, user_id, new_role, assigned_by) → bool` | Update user.role; only admin may assign roles; effect is immediate |
| `validate_role` | `(role: str) → bool` | Validate role string against Role enum |

---

### 4.2.3 Audit Service

**Purpose**: Records all security-relevant actions with immutable audit trail.

**Technologies**: SQLAlchemy, PostgreSQL JSONB

**Implementation**: `enterprise_rbac_auth/services/audit_service.py`

**Logged Actions**:
- `LOGIN`, `LOGOUT`, `LOGIN_FAILED`
- `CREATE_USER`, `UPDATE_USER`, `DELETE_USER`, `UPDATE_USER_ROLE`
- `CREATE_PROJECT`, `UPDATE_PROJECT`, `DELETE_PROJECT`
- `GRANT_ACCESS`, `REVOKE_ACCESS`
- `TRIGGER_ANALYSIS`, `VIEW_ANALYSIS`
- `UPDATE_CONFIG`

**Immutability Enforcement**: No `UPDATE` or `DELETE` endpoints exposed. API layer returns `403 Forbidden` for any modification attempt.

---

### 4.2.4 Authorization Middleware

**Purpose**: Intercepts requests to validate JWT tokens and enforce RBAC before reaching route handlers.

**Technologies**: FastAPI dependency injection, PyJWT

**Implementation**: `enterprise_rbac_auth/middleware/auth_middleware.py`

**Middleware Flow**:
```
Request → Extract Bearer token → validate_token()
    → Token invalid/missing → 401 Unauthorized
    → Token valid → Load user from DB
    → User inactive → 401 Unauthorized
    → Check required role/permission via RBACService
    → Permission denied → 403 Forbidden
    → Permission granted → Inject user into request context → Route handler
```

**Key Functions**:

| Function | Description |
|----------|-------------|
| `get_current_user(token, db)` | Dependency: validates token and returns active user |
| `require_role(required_role)` | Dependency factory: enforces minimum role level |
| `require_permission(permission)` | Dependency factory: enforces specific permission |
| `require_project_access(permission)` | Dependency factory: enforces project-level access via RBACService |

---

### 4.2.5 Architecture Evaluation Tools

**Purpose**: Static analysis of codebase architecture layers and dependency relationships.

**Technologies**: Python AST, NetworkX, pytest

**Implementation**: `tools/architecture_evaluation/`

| Module | Responsibility |
|--------|---------------|
| `layer_analyzer.py` | Detects layer violations using import path patterns |
| `integration_analyzer.py` | Builds dependency graph and detects circular dependencies |
| `system_inspector.py` | Inspects running system for architectural compliance |
| `models.py` | Data models: `LayerViolation`, `CircularDependency`, `ArchitectureReport` |

**Layer Definition**:

Layers are identified by import path patterns. The allowed dependency flow is: `presentation → service → data`. A violation occurs when a presentation-layer module directly imports from the data layer, bypassing the service layer.

| Layer | Path Patterns |
|-------|---------------|
| presentation | `api/`, `routes/` |
| service | `services/` |
| data | `models/`, `database/` |
| middleware | `middleware/` |


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

For real-time updates, the frontend subscribes to the following server-emitted events:

| Event | Payload Fields | Description |
|-------|---------------|-------------|
| `analysis:started` | `analysis_id` | Fired when an analysis job begins processing |
| `analysis:progress` | `analysis_id`, `percentage` | Periodic progress updates during analysis |
| `analysis:completed` | `analysis_id`, `total_issues`, `quality_score` | Fired when analysis finishes successfully |
| `analysis:failed` | `analysis_id`, `error` | Fired when analysis encounters an unrecoverable error |

The client uses these events to update the UI in real time without polling, refreshing issue counts and quality scores as soon as results are available.

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

Each service is deployed as a Kubernetes `Deployment` with the following configuration pattern:

- **Replicas**: 3 (minimum for high availability)
- **Image**: pulled from AWS ECR with environment-specific tags
- **Environment variables**: injected from Kubernetes Secrets (e.g., database credentials)
- **Resource limits**: CPU 1000m / Memory 1Gi per container; requests at 500m / 512Mi
- **Health checks**: liveness probe on `/health` (initial delay 30s, period 10s); readiness probe on `/ready` (initial delay 10s, period 5s)

See: `docs/diagram/deployment-architecture.puml` for the complete deployment topology.

## 7.2 Scaling Strategy

### Horizontal Pod Autoscaler (HPA)

The HPA is configured for each stateless service with the following policy:

- **Min replicas**: 3
- **Max replicas**: 20
- **Scale-up trigger**: CPU utilization > 70% or Memory utilization > 80%
- **Scale-down**: gradual, with stabilization window to prevent thrashing

### Worker Autoscaling

Celery workers scale based on Redis queue depth:

- **Min workers**: 3
- **Max workers**: 10
- **Prefetch multiplier**: 1 (one task per worker at a time for fair distribution)
- **Late acknowledgement**: enabled (tasks re-queued on worker crash)
- **Scale-up trigger**: queue depth > 20 pending tasks

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

