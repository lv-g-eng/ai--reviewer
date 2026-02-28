**\[AI-Based Reviewer on Project Code and Architecture\] - Software Design Document (SDD)**

**Version:** \[ v0.5\]

**Date:** \[20/02/2026\]

**Document History\
**

  ------------- ------------ --------------- --------------- ----------------------------------------------------------------------------------------------------------------------------
  **Version**   **Date**     **Author**      **Reviewer**    **Changes**

  V0.1          2026-02-07   BaiXuan Zhang   Dr. Siraprapa   Initial draft

  V0.2          2026-02-13   BaiXuan Zhang   Dr. Siraprapa   Added system architecture, database schema, component design

  V0.3          2026-02-16   BaiXuan Zhang   Dr. Siraprapa   Added security design, deployment architecture, complete database design, API specs, architecture diagrams

  V0.4          2026-02-19   BaiXuan Zhang   Dr. Siraprapa   Completed RBAC component design, updated technology stack, added ADR-005, aligned with enterprise_rbac_auth implementation

  V0.5          2026-02-20   BaiXuan Zhang   Dr. Siraprapa   Added comprehensive design sections: design constraints, module-level specifications, core algorithms, exception handling, detailed security design, deployment architecture, performance optimization, maintainability/observability, ADRs (001-007)
  ------------- ------------ --------------- --------------- ----------------------------------------------------------------------------------------------------------------------------

# 1. Introduction

## 1.1 Purpose

This Software Design Document (SDD) describes the architectural and detailed design of the AI-Based Reviewer platform for automated code review and architectural analysis. It serves as a comprehensive guide for the development team, defining system architecture, component interactions, data structures, interface designs, and implementation specifications aligned with the requirements outlined in the Software Requirements Specification (SRS).

## 1.2 System Overview

The AI-Based Reviewer is a web-based platform that provides intelligent, automated code review and architectural analysis for software projects. The system leverages cutting-edge technologies including Abstract Syntax Trees (AST), graph databases, and Large Language Models (LLMs) to deliver comprehensive code quality assessment, architectural drift detection, and compliance verification.

**Core Capabilities:**

Automated Pull Request Review - AI-powered code analysis with inline comments

Real-time Architectural Drift Detection - Graph-based analysis using Neo4j

Compliance Verification - ISO/IEC 25010, ISO/IEC 23396, and industry standards

Interactive Dependency Graph Visualization - D3.js-powered interactive graphs

Enterprise-grade Security - RBAC authentication, audit logging

## 1.3 Design Principles

\- **Modularity:** Microservices architecture with clear service boundaries

\- **Scalability:** Horizontal scaling capability for all stateless components

\- **Resilience:** Fault tolerance with graceful degradation

\- **Security:** Defense in depth with multiple security layers

\- **Maintainability:** Clean code, comprehensive documentation, automated testing

\- **Performance:** Optimized for sub-second response times

## 1.4 Scope

This document covers:

·System architecture and component design

·Database schema and data models

·API specifications and interfaces

·Security architecture and controls

·Deployment topology and infrastructure

·Technology stack and tool selection

# 2. System Architecture

## 2.1 Architectural Overview

The system implements a multi-tier microservices architecture designed for modularity, scalability, and resilience. The architecture follows industry best practices including separation of concerns, horizontal scaling capability, and high availability patterns.

## 2.2 Logical Architecture

The system follows a multi-tier architecture with clear separation of concerns:

**Presentation Layer**

\- **Technology:** React 18, Next.js 14, Tailwind CSS

\- **Responsibilities:**

  - Server-side rendering for SEO and performance

  - Interactive dashboards for code metrics and architecture visualization

  - Real-time updates via WebSocket connections

  - Responsive design for desktop and mobile

\- **Components:**

  - Dashboard UI

  - Repository Management UI

  - Analysis Results Viewer

  - Dependency Graph Visualizer

  - Settings and Configuration UI

**Application Layer**

\- **Technology:** FastAPI (Python 3.11+), Pydantic for validation

\- **Responsibilities:**

  - REST API endpoints for client requests

  - Business logic orchestration

  - Request validation and error handling

  - Authentication and authorization

\- **Services:**

  - Auth Service: User authentication, JWT management, RBAC

  - Project Manager: Repository management, webhook configuration

  - Analysis Service: Analysis orchestration, result aggregation

**Service Layer**

\- **Technology:** Python 3.11+, Celery for async tasks

\- **Responsibilities:**

  - Core business logic implementation

  - Integration with external services

  - Asynchronous task processing

\- **Components:**

  - AST Parser Service: Generates abstract syntax trees from source code

  - Graph Analysis Service: Manages dependency graph operations in Neo4j

  - LLM Integration Service: Coordinates with AI APIs for code review

  - GitHub Integration Service: Handles webhooks and repository operations

  - Metrics Service: Calculates and aggregates quality metrics

**Data Layer**

\- **PostgreSQL:** Transactional data (users, projects, analyses, audit logs)

\- **Neo4j:** Graph data (AST nodes, dependencies, architectural relationships)

\- **Redis:** Caching and message queue for asynchronous tasks

## 2.3 Microservices Architecture

**Service Catalog**

  --------------------------------------------------------------------------------------------------------------------------------------------------
  **Service Name**            **Technology**   **Port**       **Responsibilities**                             **Dependencies**
  --------------------------- ---------------- -------------- ------------------------------------------------ -------------------------------------
  **API Gateway**             Kong/Nginx       80/443         Routing, rate limiting, SSL termination          None

  **Auth Service**            FastAPI          8001           Authentication, authorization, user management   PostgreSQL, Redis

  **Project Manager**         FastAPI          8002           Repository management, project configuration     PostgreSQL, GitHub API

  **Analysis Service**        FastAPI          8003           Analysis orchestration, result aggregation       PostgreSQL, Redis, Analysis Workers

  **Code Review Engine**      Python/Celery    N/A            AST parsing, code analysis, issue detection      LLM API, PostgreSQL

  **Architecture Analyzer**   Python/Celery    N/A            Dependency graph analysis, drift detection       Neo4j, PostgreSQL

  **Agentic AI Service**      Python/Celery    N/A            LLM integration, prompt engineering              OpenAI API, Anthropic API

  **Webhook Handler**         FastAPI          8004           GitHub webhook processing                        Redis, GitHub API

  **Metrics Service**         FastAPI          8005           Quality metrics calculation, reporting           PostgreSQL, Neo4j
  --------------------------------------------------------------------------------------------------------------------------------------------------

**Service Communication**

-   **Synchronous**: REST APIs over HTTP/HTTPS

-   **Asynchronous**: Message queue (Redis/Celery) for long-running tasks

-   **Event-driven**: Webhooks for external integrations

## 2.4 Data Flow Diagram (DFD)

Pull Request Review Flow:

1\. GitHub webhook triggers on PR creation/update

2\. Webhook handler receives event and queues analysis task in Redis

3\. Analysis worker retrieves code diff from GitHub API

4\. AST Parser generates syntax trees for modified files

5\. Graph Analysis queries Neo4j for architectural context

6\. LLM service sends code + context to AI API for analysis

7\. Results are processed, categorized by severity, and stored in PostgreSQL

8\. Review comments are posted to GitHub PR

9\. Dependency graph is updated in Neo4j

10\. Frontend dashboard is updated with new analysis results

![IMG_256](media/image1.png){width="6.520138888888889in" height="4.5125in"}

## 2.5 Component Interaction Diagram

![IMG_256](media/image2.png){width="6.53125in" height="7.649305555555555in"}

**3. Database Design**

**3.1 Entity Relationship Diagram (ERD)**

The system uses two primary databases with the following main entities:

PostgreSQL Entities:

• Users (one-to-many with Projects)

![IMG_256](media/image3.png){width="6.540972222222222in" height="3.829861111111111in"}

-   **Entities**: User, Session, AuditLog

-   **Purpose**: Authentication, authorization, and audit trail

• Projects (one-to-many with Repositories)

![IMG_256](media/image4.png){width="6.499305555555556in" height="3.7583333333333333in"}

-   **Entities**: Project, ProjectMember, AnalysisConfig

-   **Purpose**: Repository management and team collaboration

• Repositories (one-to-many with PullRequests)

• PullRequests (one-to-many with AnalysisResults)

• AnalysisResults (one-to-many with Issues)

• Issues (detected code issues)

![IMG_256](media/image5.png){width="6.447916666666667in" height="6.367361111111111in"}

-   **Entities**: PullRequest, Analysis, Issue, Comment, ComplianceCheck

-   **Purpose**: PR review and issue tracking

• AuditLogs (system activity tracking)

![IMG_256](media/image6.png){width="6.541666666666667in" height="2.7395833333333335in"}

-   **Entities**: QualityMetric, TaskQueue

-   **Purpose**: Quality tracking and task management

Neo4j Graph Entities:

• Module nodes (represents code modules/packages)

• Class nodes (represents classes)

• Function nodes (represents functions/methods)

![IMG_256](media/image7.png){width="6.604166666666667in" height="8.94513888888889in"}

-   **Nodes**: Module, Class, Function

-   **Purpose**: Code structure representation

• DEPENDS_ON relationships (dependency edges)

![IMG_256](media/image8.png){width="6.438194444444444in" height="2.204861111111111in"}

-   **Nodes**: Module, Class, Function

-   **Purpose**: Code structure representation

• CALLS relationships (function call edges)

![IMG_256](media/image9.png){width="6.604166666666667in" height="6.138888888888889in"}

-   **Relationship**: CALLS

-   **Purpose**: Function and method call tracking

• INHERITS relationships (inheritance edges)

![IMG_256](media/image10.png){width="6.540972222222222in" height="5.060416666666667in"}

-   **Relationships**: INHERITS, IMPLEMENTS, EXTENDS

-   **Purpose**: Class hierarchy and interface implementation

• Complete Graph Model

![IMG_256](media/image11.png){width="5.221527777777778in" height="9.131944444444445in"}

-   **Overview**: Complete architecture with all nodes and relationships

-   **Purpose**: Comprehensive view of code architecture

![IMG_256](media/image12.png){width="6.545138888888889in" height="5.940277777777778in"}

## 3.2 PostgreSQL Schema

### 3.2.1 Users Table

Stores user account information for authentication and authorization.

  -------------------------------------------------------------------------------------------------------------------------------------------
  **Column**              **Type**          **Constraints**      **Description**
  ----------------------- ----------------- -------------------- ----------------------------------------------------------------------------
  id                      UUID              PK, auto-generated   Unique user identifier

  username                VARCHAR(50)       UNIQUE, NOT NULL     Login username (3-30 chars, alphanumeric + underscore, starts with letter)

  email                   VARCHAR(100)      UNIQUE, NOT NULL     User email address

  password_hash           VARCHAR(255)      NOT NULL             bcrypt-hashed password

  role                    VARCHAR(20)       NOT NULL, CHECK      One of: guest, user, programmer, reviewer, manager, admin

  is_active               BOOLEAN           DEFAULT TRUE         Account active status

  email_verified          BOOLEAN           DEFAULT FALSE        Email verification status

  created_at              TIMESTAMP         DEFAULT NOW          Account creation time

  updated_at              TIMESTAMP         DEFAULT NOW          Last update time

  last_login              TIMESTAMP         NULLABLE             Last successful login time

  failed_login_attempts   INTEGER           DEFAULT 0            Consecutive failed login count

  locked_until            TIMESTAMP         NULLABLE             Account lockout expiry time
  -------------------------------------------------------------------------------------------------------------------------------------------

Indexes: email, username (case-insensitive), role

### 3.2.2 Sessions Table

Tracks active user sessions for token management and audit.

  ----------------------------------------------------------------------------------------------------------
  **Column**        **Type**          **Constraints**       **Description**
  ----------------- ----------------- --------------------- ------------------------------------------------
  id                UUID              PK, auto-generated    Unique session identifier

  user_id           UUID              FK → users, CASCADE   Owning user

  access_token      VARCHAR(500)      NOT NULL              JWT access token

  refresh_token     VARCHAR(500)      NULLABLE              JWT refresh token

  expires_at        TIMESTAMP         NOT NULL              Session expiry time (must be after created_at)

  created_at        TIMESTAMP         DEFAULT NOW           Session creation time

  ip_address        VARCHAR(45)       NULLABLE              Client IP address

  user_agent        TEXT              NULLABLE              Client user agent string

  is_revoked        BOOLEAN           DEFAULT FALSE         Manual revocation flag
  ----------------------------------------------------------------------------------------------------------

Indexes: user_id, access_token, expires_at

### 3.2.3 Projects Table

Stores connected GitHub repository configurations.

  --------------------------------------------------------------------------------------------------------------------------
  **Column**       **Type**        **Constraints**       **Description**
  ---------------- --------------- --------------------- -------------------------------------------------------------------
  id               UUID            PK, auto-generated    Unique project identifier

  owner_id         UUID            FK → users, CASCADE   Project owner

  name             VARCHAR(200)    NOT NULL              Display name

  github_url       VARCHAR(500)    UNIQUE, NOT NULL      GitHub repository URL (format: https://github.com/{owner}/{repo})

  repository_id    VARCHAR(100)    NOT NULL              GitHub repository ID

  default_branch   VARCHAR(100)    DEFAULT \'main\'      Default analysis branch

  webhook_secret   VARCHAR(255)    NULLABLE              HMAC webhook verification secret

  is_active        BOOLEAN         DEFAULT TRUE          Project active status

  created_at       TIMESTAMP       DEFAULT NOW           Creation time

  updated_at       TIMESTAMP       DEFAULT NOW           Last update time

  last_analyzed    TIMESTAMP       NULLABLE              Last analysis completion time
  --------------------------------------------------------------------------------------------------------------------------

Indexes: owner_id, github_url, is_active

### 3.2.4 Project Members Table

Manages team membership and per-project role assignments.

  -------------------------------------------------------------------------------------------------------------
  **Column**        **Type**          **Constraints**          **Description**
  ----------------- ----------------- ------------------------ ------------------------------------------------
  id                UUID              PK, auto-generated       Unique membership identifier

  project_id        UUID              FK → projects, CASCADE   Associated project

  user_id           UUID              FK → users, CASCADE      Associated user

  role              VARCHAR(20)       NOT NULL, CHECK          One of: owner, maintainer, contributor, viewer

  joined_at         TIMESTAMP         DEFAULT NOW              Membership creation time
  -------------------------------------------------------------------------------------------------------------

Constraints: UNIQUE(project_id, user_id). Indexes: project_id, user_id

### 3.2.5 Pull Requests Table

Records GitHub pull requests submitted for analysis.

  -------------------------------------------------------------------------------------------
  **Column**        **Type**          **Constraints**          **Description**
  ----------------- ----------------- ------------------------ ------------------------------
  id                UUID              PK, auto-generated       Unique PR record identifier

  project_id        UUID              FK → projects, CASCADE   Associated project

  pr_number         INTEGER           NOT NULL                 GitHub PR number

  github_pr_id      VARCHAR(100)      NOT NULL                 GitHub internal PR ID

  title             VARCHAR(500)      NOT NULL                 PR title

  author            VARCHAR(100)      NOT NULL                 GitHub username of PR author

  source_branch     VARCHAR(100)      NOT NULL                 Feature branch name

  target_branch     VARCHAR(100)      NOT NULL                 Target merge branch

  status            VARCHAR(20)       NOT NULL, CHECK          One of: open, closed, merged

  created_at        TIMESTAMP         DEFAULT NOW              PR creation time

  updated_at        TIMESTAMP         DEFAULT NOW              Last update time

  closed_at         TIMESTAMP         NULLABLE                 PR close/merge time
  -------------------------------------------------------------------------------------------

Constraints: UNIQUE(project_id, pr_number). Indexes: project_id, status, author

### 3.2.6 Analyses Table

Stores analysis job status and aggregate results per pull request.

  -----------------------------------------------------------------------------------------------------------------------------
  **Column**        **Type**          **Constraints**               **Description**
  ----------------- ----------------- ----------------------------- -----------------------------------------------------------
  id                UUID              PK, auto-generated            Unique analysis identifier

  pr_id             UUID              FK → pull_requests, CASCADE   Associated pull request

  status            VARCHAR(20)       NOT NULL, CHECK               One of: pending, processing, completed, failed

  started_at        TIMESTAMP         DEFAULT NOW                   Analysis start time

  completed_at      TIMESTAMP         NULLABLE                      Analysis completion time (required when status=completed)

  processing_time   INTEGER           NULLABLE                      Duration in seconds

  total_issues      INTEGER           DEFAULT 0                     Total issue count

  critical_issues   INTEGER           DEFAULT 0                     Critical severity count

  high_issues       INTEGER           DEFAULT 0                     High severity count

  medium_issues     INTEGER           DEFAULT 0                     Medium severity count

  low_issues        INTEGER           DEFAULT 0                     Low severity count

  quality_score     DECIMAL(5,2)      NULLABLE                      Computed quality score (0-100)

  error_message     TEXT              NULLABLE                      Failure reason if status=failed
  -----------------------------------------------------------------------------------------------------------------------------

Indexes: pr_id, status, completed_at

### 3.2.7 Issues Table

Stores individual code issues detected during analysis.

  -------------------------------------------------------------------------------------------------------------------
  **Column**         **Type**          **Constraints**          **Description**
  ------------------ ----------------- ------------------------ -----------------------------------------------------
  id                 UUID              PK, auto-generated       Unique issue identifier

  analysis_id        UUID              FK → analyses, CASCADE   Parent analysis

  severity           VARCHAR(20)       NOT NULL, CHECK          One of: critical, high, medium, low

  category           VARCHAR(100)      NOT NULL                 Issue category (security, performance, style, etc.)

  title              VARCHAR(200)      NOT NULL                 Short issue title

  description        TEXT              NOT NULL                 Detailed issue description

  suggestion         TEXT              NULLABLE                 AI-generated fix suggestion

  file_path          VARCHAR(500)      NOT NULL                 Relative file path

  line_number        INTEGER           NOT NULL                 Line number in file

  code_snippet       TEXT              NULLABLE                 Relevant code excerpt

  rule_id            VARCHAR(100)      NULLABLE                 Triggered rule identifier

  created_at         TIMESTAMP         DEFAULT NOW              Issue creation time

  user_feedback      VARCHAR(20)       CHECK, NULLABLE          One of: accept, dismiss, false_positive

  feedback_comment   TEXT              NULLABLE                 User feedback comment

  feedback_at        TIMESTAMP         NULLABLE                 Feedback submission time
  -------------------------------------------------------------------------------------------------------------------

Indexes: analysis_id, severity, category, file_path

### 3.2.8 Quality Metrics Table

Stores daily aggregated quality metrics per project for trend analysis.

  ------------------------------------------------------------------------------------------------------
  **Column**              **Type**          **Constraints**          **Description**
  ----------------------- ----------------- ------------------------ -----------------------------------
  id                      UUID              PK, auto-generated       Unique metric record identifier

  project_id              UUID              FK → projects, CASCADE   Associated project

  metric_date             DATE              NOT NULL                 Metric snapshot date

  total_lines             INTEGER           NULLABLE                 Total lines of code

  code_coverage           DECIMAL(5,2)      NULLABLE                 Test coverage percentage

  avg_complexity          DECIMAL(5,2)      NULLABLE                 Average cyclomatic complexity

  technical_debt          INTEGER           NULLABLE                 Estimated technical debt in hours

  maintainability_index   DECIMAL(5,2)      NULLABLE                 Maintainability index score

  created_at              TIMESTAMP         DEFAULT NOW              Record creation time
  ------------------------------------------------------------------------------------------------------

Constraints: UNIQUE(project_id, metric_date). Indexes: project_id, metric_date

### 3.2.9 Audit Logs Table

Immutable record of all security-relevant system actions. No UPDATE or DELETE operations are permitted.

  -------------------------------------------------------------------------------------------------------------------
  **Column**       **Type**         **Constraints**        **Description**
  ---------------- ---------------- ---------------------- ----------------------------------------------------------
  id               UUID             PK, auto-generated     Unique log entry identifier

  user_id          UUID             FK → users, SET NULL   Acting user (nullable for system actions)

  action           VARCHAR(100)     NOT NULL               Action type (e.g., LOGIN, CREATE_USER, UPDATE_USER_ROLE)

  resource_type    VARCHAR(50)      NOT NULL               Affected resource type

  resource_id      UUID             NULLABLE               Affected resource identifier

  details          JSONB            NULLABLE               Additional action context

  ip_address       VARCHAR(45)      NULLABLE               Client IP address

  user_agent       TEXT             NULLABLE               Client user agent string

  timestamp        TIMESTAMP        DEFAULT NOW            Action timestamp
  -------------------------------------------------------------------------------------------------------------------

Indexes: user_id, action, timestamp, (resource_type, resource_id)

## 3.3 Neo4j Graph Database Schema

### 3.3.1 Node Types

**Module Node**

Represents a source code module (file or package). Unique constraint on id, indexed by project_id.

  --------------------------------------------------------------------------
  **Property**            **Type**                **Description**
  ----------------------- ----------------------- --------------------------
  id                      UUID                    Unique module identifier

  project_id              UUID                    Owning project

  name                    String                  Module name

  path                    String                  File system path

  language                String                  Programming language

  lines_of_code           Integer                 Total lines of code

  complexity              Integer                 Cyclomatic complexity

  created_at              DateTime                Creation timestamp

  updated_at              DateTime                Last update timestamp
  --------------------------------------------------------------------------

**Class Node**

Represents a class definition within a module. Unique constraint on id.

  -------------------------------------------------------------------------
  **Property**            **Type**                **Description**
  ----------------------- ----------------------- -------------------------
  id                      UUID                    Unique class identifier

  module_id               UUID                    Containing module

  name                    String                  Class name

  file_path               String                  Source file path

  line_start              Integer                 Start line number

  line_end                Integer                 End line number

  complexity              Integer                 Cyclomatic complexity

  methods_count           Integer                 Number of methods

  is_abstract             Boolean                 Abstract class flag
  -------------------------------------------------------------------------

**Function Node**

Represents a function or method definition. Unique constraint on id.

  ----------------------------------------------------------------------------
  **Property**            **Type**                **Description**
  ----------------------- ----------------------- ----------------------------
  id                      UUID                    Unique function identifier

  parent_id               UUID                    Containing module or class

  name                    String                  Function name

  file_path               String                  Source file path

  line_start              Integer                 Start line number

  line_end                Integer                 End line number

  complexity              Integer                 Cyclomatic complexity

  parameters_count        Integer                 Number of parameters

  is_async                Boolean                 Async function flag
  ----------------------------------------------------------------------------

### 3.3.2 Relationship Types

**DEPENDS_ON**

Directed dependency from one module to another (import, call, inheritance, or composition).

  ---------------------------------------------------------------------------------------------------------
  **Property**            **Type**                **Description**
  ----------------------- ----------------------- ---------------------------------------------------------
  type                    String                  Dependency type: import, call, inheritance, composition

  strength                Integer                 Usage frequency score (1-10)

  created_at              DateTime                Relationship creation time

  last_updated            DateTime                Last update time
  ---------------------------------------------------------------------------------------------------------

**CALLS**

Directed call relationship from one function to another.

  -------------------------------------------------------------------------------
  **Property**            **Type**                **Description**
  ----------------------- ----------------------- -------------------------------
  call_count              Integer                 Number of call sites

  is_recursive            Boolean                 Whether the call is recursive

  call_sites              List\\\<Integer\\\>     Line numbers of call sites
  -------------------------------------------------------------------------------

**INHERITS**

Directed inheritance relationship from subclass to superclass.

  -------------------------------------------------------------------------------------
  **Property**            **Type**                **Description**
  ----------------------- ----------------------- -------------------------------------
  inheritance_type        String                  One of: single, multiple, interface

  -------------------------------------------------------------------------------------

**CONTAINS**

Structural containment: Module → Class, Class → Function.

### 3.3.3 Common Query Patterns

The following query patterns are used for architectural analysis:

-   **Circular Dependency Detection**: Traverse DEPENDS_ON relationships to find cycles of length 2-10 within a project

-   **Module Coupling Calculation**: Count incoming and outgoing DEPENDS_ON edges per module; rank by total coupling

-   **Layer Violation Detection**: Match DEPENDS_ON edges that skip architectural layers (e.g., presentation → data without passing through service)

-   **Dependency Graph Export**: Collect all modules and their DEPENDS_ON targets for visualization rendering

# 4. Detailed Design

## 4.1 Class Diagram (if Object-Oriented)

The system\'s class structure is organized into modular diagrams by functional domain for improved readability and maintainability.

**User Management Domain**

![IMG_256](media/image13.png){width="6.458333333333333in" height="2.245138888888889in"}

-   **Components**: User, Session, AuthService, JWTManager, PasswordHasher, PermissionChecker

-   **Repositories**: UserRepository, SessionRepository

-   **DTOs**: RegisterDTO, LoginDTO, UserProfile, TokenPayload

-   **Purpose**: Authentication, authorization, session management, audit logging

**Project Management Domain**

![IMG_256](media/image14.png){width="6.55in" height="3.261111111111111in"}

-   **Components**: Project, ProjectMember, ProjectService, WebhookService, AnalysisConfig, ConfigService

-   **Repositories**: ProjectRepository, ConfigRepository

-   **DTOs**: CreateProjectDTO, UpdateProjectDTO, ProjectConfig, QualityMetrics

-   **Purpose**: GitHub repository integration, team collaboration, project configuration

**Code Analysis Domain**

![IMG_256](media/image15.png){width="6.533333333333333in" height="4.334027777777778in"}

-   **Components**: PullRequest, Analysis, Issue, Comment, CodeReviewEngine, ParserService, IssueDetector

-   **Repositories**: AnalysisRepository, IssueRepository, CommentRepository

-   **DTOs**: AnalysisReport, IssueContext, ValidationResult, ComparisonResult

-   **Purpose**: PR analysis, issue detection, code review, GitHub comment integration

**Architecture Analysis Domain**

![IMG_256](media/image16.png){width="6.469444444444444in" height="1.25in"}

-   **Components**: CodeEntity, Dependency, ArchitectureAnalyzer, ASTParser, GraphBuilder, CircularDependencyDetector, LayerAnalyzer

-   **Repositories**: EntityRepository, DependencyRepository

-   **DTOs**: EntityMetrics, CouplingMetrics, DriftReport, GraphVisualization, Violation

-   **Purpose**: Code structure analysis, dependency graph, circular dependency detection, layer validation

**AI Integration Domain**

![IMG_256](media/image17.png){width="6.561111111111111in" height="1.3118055555555554in"}

-   **Components**: AgenticAI, LLMClient, ContextBuilder, PromptManager, ResponseParser, EmbeddingService, VectorStore

-   **Support**: RateLimiter, CacheManager, TokenCounter

-   **DTOs**: AIAnalysis, ReviewComment, CodeSuggestion, Pattern, Context, LLMResponse

-   **Purpose**: LLM integration, AI-powered code review, semantic search, prompt management

**Quality Metrics Domain**

![IMG_256](media/image18.png){width="6.501388888888889in" height="1.7618055555555556in"}

-   **Components**: QualityMetric, ComplianceCheck, MetricsService, MetricCalculator, ComplexityCalculator, CoverageCalculator, TechnicalDebtCalculator

-   **Analysis**: MetricsAggregator, TrendAnalyzer, DashboardBuilder

-   **Repositories**: MetricsRepository, ComplianceRepository

-   **DTOs**: MetricDelta, MetricTrend, Dashboard, Report, ComparisonReport

-   **Purpose**: Quality metrics calculation, compliance verification, trend analysis, dashboard generation

**Infrastructure Domain**

![IMG_256](media/image19.png){width="6.522916666666666in" height="0.6916666666666667in"}

-   **Components**: GitHubClient, Neo4jClient, RedisClient, PostgreSQLClient, TaskQueue

-   **Services**: EmailService, LoggerService, MonitoringService, CacheService, FileStorageService

-   **Support**: WebhookHandler, RateLimiter, ConfigurationManager

-   **DTOs**: PRData, File, WebhookConfig, Node, Relationship, Task, HealthStatus

-   **Purpose**: External integrations, database clients, task queue, monitoring, caching

**Complete Class Diagram**

![IMG_256](media/image20.png){width="6.553472222222222in" height="3.4791666666666665in"}

## 4.2 Core Components

### 4.2.1 Authentication Service

**Purpose**: Manages user authentication, JWT token lifecycle, and session management.

**Technologies**: FastAPI, PyJWT, bcrypt, SQLAlchemy

**Implementation**: enterprise_rbac_auth/services/auth_service.py

**Class Structure**:

  -------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  **Method**                     **Signature**                                                    **Description**
  ------------------------------ ---------------------------------------------------------------- -------------------------------------------------------------------------
  hash_password                  (password: str) → str                                            Hash password using bcrypt with configurable rounds

  verify_password                (password: str, password_hash: str) → bool                       Verify plain-text password against stored bcrypt hash

  generate_token                 (user_id, username, role) → str                                  Generate signed JWT with user_id, username, role, iat, exp, jti claims

  validate_token                 (token: str) → Optional\[TokenPayload\]                          Decode and validate JWT; returns None on expiry or tampering

  refresh_token                  (token: str) → Optional\[str\]                                   Issue new token if current token is within 10-min refresh window

  login                          (db, username, password, ip_address, device_info) → AuthResult   Authenticate user, create Session record, update last_login

  logout                         (db, user_id, token) → bool                                      Invalidate specific session by setting is_valid=False

  invalidate_all_user_sessions   (db, user_id) → bool                                             Invalidate all active sessions (used on password change / deactivation)
  -------------------------------------------------------------------------------------------------------------------------------------------------------------------------

**Key Design Decisions**:

-   Stateless design: no instance state, all methods are \@staticmethod

-   Generic error messages on login failure to prevent username enumeration

-   JWT payload includes jti (JWT ID) for uniqueness and future revocation support

-   Session records stored in PostgreSQL for audit trail; token validity checked via is_valid flag

**Design Notes**:

-   Stateless design: no instance state, all methods are static

-   Generic error messages on login failure to prevent username enumeration

-   JWT payload includes jti (JWT ID) for uniqueness and future revocation support

-   Session records stored in PostgreSQL for audit trail; token validity checked via is_valid flag

-   The original async design (register, login, validate_token as instance methods) was superseded by the current stateless \@staticmethod implementation for simplicity and testability

### 4.2.2 RBAC Service

**Purpose**: Manages role-based permissions and project-level access control.

**Technologies**: SQLAlchemy, Python Enum

**Implementation**: enterprise_rbac_auth/services/rbac_service.py

**Role Hierarchy**:

> ADMIN \> MANAGER \> REVIEWER \> PROGRAMMER \> VISITOR

**Permission Matrix**:

  --------------------------------------------------------------------------------------------
  **Permission**       **ADMIN**   **MANAGER**   **REVIEWER**   **PROGRAMMER**   **VISITOR**
  -------------------- ----------- ------------- -------------- ---------------- -------------
  CREATE_USER          ✓                                                         

  READ_USER            ✓           ✓                                             

  UPDATE_USER          ✓                                                         

  DELETE_USER          ✓                                                         

  CREATE_PROJECT       ✓           ✓                            ✓                

  VIEW_PROJECT         ✓           ✓             ✓              ✓                ✓

  UPDATE_PROJECT       ✓           ✓                            ✓                

  DELETE_PROJECT       ✓           ✓                            ✓                

  TRIGGER_ANALYSIS     ✓           ✓             ✓              ✓                

  VIEW_ANALYSIS        ✓           ✓             ✓              ✓                ✓

  MANAGE_USERS         ✓                                                         

  VIEW_AUDIT_LOGS      ✓           ✓                                             
  --------------------------------------------------------------------------------------------

**Class Structure**:

  ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  **Method**              **Signature**                                  **Description**
  ----------------------- ---------------------------------------------- -----------------------------------------------------------------------------------------------------------------------------------------
  has_permission          (db, user_id, permission) → bool               Check if user\'s role includes the requested permission

  get_role_permissions    (role) → list\[Permission\]                    Return permission list for a given role from ROLE_PERMISSIONS map

  can_access_project      (db, user_id, project_id, permission) → bool   Project access: ADMIN always True; owner always True; others need ProjectAccess grant for VIEW; write permissions denied for non-owners

  grant_project_access    (db, project_id, user_id, granted_by) → bool   Create ProjectAccess record; only admin or project owner may grant

  revoke_project_access   (db, project_id, user_id, revoked_by) → bool   Delete ProjectAccess record; only admin or project owner may revoke

  assign_role             (db, user_id, new_role, assigned_by) → bool    Update user.role; only admin may assign roles; effect is immediate

  validate_role           (role: str) → bool                             Validate role string against Role enum
  ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

### 4.2.3 Audit Service

**Purpose**: Records all security-relevant actions with immutable audit trail.

**Technologies**: SQLAlchemy, PostgreSQL JSONB

**Implementation**: enterprise_rbac_auth/services/audit_service.py

**Logged Actions**:

-   LOGIN, LOGOUT, LOGIN_FAILED

-   CREATE_USER, UPDATE_USER, DELETE_USER, UPDATE_USER_ROLE

-   CREATE_PROJECT, UPDATE_PROJECT, DELETE_PROJECT

-   GRANT_ACCESS, REVOKE_ACCESS

-   TRIGGER_ANALYSIS, VIEW_ANALYSIS

-   UPDATE_CONFIG

**Immutability Enforcement**: No UPDATE or DELETE endpoints exposed. API layer returns 403 Forbidden for any modification attempt.

### 4.2.4 Authorization Middleware

**Purpose**: Intercepts requests to validate JWT tokens and enforce RBAC before reaching route handlers.

**Technologies**: FastAPI dependency injection, PyJWT

**Implementation**: enterprise_rbac_auth/middleware/auth_middleware.py

**Middleware Flow**:

> Request → Extract Bearer token → validate_token()
>
> → Token invalid/missing → 401 Unauthorized
>
> → Token valid → Load user from DB
>
> → User inactive → 401 Unauthorized
>
> → Check required role/permission via RBACService
>
> → Permission denied → 403 Forbidden
>
> → Permission granted → Inject user into request context → Route handler

**Key Functions**:

  --------------------------------------------------------------------------------------------------------
  **Function**                         **Description**
  ------------------------------------ -------------------------------------------------------------------
  get_current_user(token, db)          Dependency: validates token and returns active user

  require_role(required_role)          Dependency factory: enforces minimum role level

  require_permission(permission)       Dependency factory: enforces specific permission

  require_project_access(permission)   Dependency factory: enforces project-level access via RBACService
  --------------------------------------------------------------------------------------------------------

### 4.2.5 Architecture Evaluation Tools

**Purpose**: Static analysis of codebase architecture layers and dependency relationships.

**Technologies**: Python AST, NetworkX, pytest

**Implementation**: tools/architecture_evaluation/

  ---------------------------------------------------------------------------------------------------------
  **Module**                          **Responsibility**
  ----------------------------------- ---------------------------------------------------------------------
  layer_analyzer.py                   Detects layer violations using import path patterns

  integration_analyzer.py             Builds dependency graph and detects circular dependencies

  system_inspector.py                 Inspects running system for architectural compliance

  models.py                           Data models: LayerViolation, CircularDependency, ArchitectureReport
  ---------------------------------------------------------------------------------------------------------

**Layer Definition**:

Layers are identified by import path patterns. The allowed dependency flow is: presentation → service → data. A violation occurs when a presentation-layer module directly imports from the data layer, bypassing the service layer.

  -----------------------------------------------------------------------
  **Layer**                           **Path Patterns**
  ----------------------------------- -----------------------------------
  presentation                        api/, routes/

  service                             services/

  data                                models/, database/

  middleware                          middleware/
  -----------------------------------------------------------------------

**5. Interface Design**

**5.1 Wireframes / Mockups**

\[Insert descriptions or screenshots of the main interfaces, such as the Login Screen, Dashboard, and Map View.\]

## 5.2 API Endpoints

  ----------------- ------------------------- ----------------------------------------
  Method            Endpoint                  Description

  POST              /api/auth/register        User registration

  POST              /api/auth/login           User authentication, returns JWT token

  POST              /api/repositories         Add new GitHub repository

  GET               /api/analysis/{repo_id}   Get analysis results for repository

  GET               /api/graph/{repo_id}      Get dependency graph data

  POST              /api/webhooks/github      GitHub webhook endpoint for PR events
  ----------------- ------------------------- ----------------------------------------

5.3 User Interface Screens

Dashboard: Main interface showing project overview, recent analyses, and quick actions.

Repository Management: List of connected repositories with status indicators.

Architecture View: Interactive dependency graph visualization with zoom and filter controls.

Metrics Dashboard: Charts and tables showing code quality trends over time.

Settings: Configuration interface for analysis rules and LLM model selection.


# 6. Design Constraints

## 6.1 Technical Constraints

| Constraint Category | Constraint | Rationale | Impact on Design |
|---------------------|------------|-----------|------------------|
| **Programming Language** | Python 3.11+ for backend services | Team expertise, rich ecosystem for AI/ML, async support | All backend services use Python; requires consistent dependency management |
| **Frontend Framework** | React 18 with Next.js 14 | SSR for performance, large community, TypeScript support | Component-based architecture, requires Node.js build pipeline |
| **Database Technology** | PostgreSQL 13+ for relational data | ACID compliance, JSON support, mature ecosystem | Requires connection pooling, migration strategy |
| **Graph Database** | Neo4j 4.4+ for dependency graphs | Native graph algorithms, Cypher query language | Separate database instance, requires graph-specific query optimization |
| **LLM API** | OpenAI GPT-4 / Anthropic Claude 3.5 | State-of-the-art code understanding, API availability | Rate limiting, fallback strategy, cost management |
| **Container Runtime** | Docker 20.10+, Kubernetes 1.21+ | Industry standard, cloud-agnostic | All services must be containerized, requires orchestration |
| **Message Queue** | Redis 6.2+ with Celery | In-memory performance, pub/sub support | Requires Redis cluster for HA, task serialization constraints |

## 6.2 Performance Constraints

| Constraint | Target | Design Implication |
|------------|--------|-------------------|
| **API Response Time** | P95 < 500ms for GET, < 1s for POST | Requires caching strategy, database query optimization, connection pooling |
| **Analysis Processing Time** | < 2 minutes for repositories < 50K LOC | Parallel processing, incremental analysis, efficient AST parsing |
| **Concurrent Users** | Support 100 concurrent dashboard users | Stateless services, horizontal scaling, WebSocket connection management |
| **Concurrent Analyses** | Support 10 concurrent analysis jobs | Worker pool sizing, resource limits per worker, queue management |
| **Database Query Performance** | < 100ms for 95% of queries | Proper indexing, query optimization, read replicas for reporting |
| **Graph Traversal Performance** | < 5 seconds for graphs with < 1000 nodes | Graph algorithm optimization, result caching, pagination |

## 6.3 Security Constraints

| Constraint | Requirement | Design Implication |
|------------|-------------|-------------------|
| **Authentication** | JWT-based with 24-hour expiry | Stateless authentication, token refresh mechanism, secure token storage |
| **Authorization** | RBAC with 5 roles | Permission checking middleware, role hierarchy enforcement, audit logging |
| **Data Encryption** | TLS 1.3 in transit, AES-256 at rest | SSL certificate management, database encryption configuration, key rotation |
| **Password Policy** | Min 8 chars, complexity requirements, bcrypt hashing | Password validation, secure hashing with cost factor 12, account lockout |
| **API Rate Limiting** | 100 requests/minute per user | Rate limiter middleware, Redis-based counter, 429 responses |
| **Input Validation** | All user inputs validated and sanitized | Pydantic models, SQL injection prevention, XSS protection |
| **Audit Logging** | All security events logged immutably | Append-only audit table, 7-year retention, no UPDATE/DELETE operations |

## 6.4 Scalability Constraints

| Constraint | Requirement | Design Implication |
|------------|-------------|-------------------|
| **Horizontal Scaling** | Linear scaling up to 50 workers | Stateless service design, shared-nothing architecture, distributed caching |
| **Database Scaling** | Support up to 10M analysis records | Partitioning strategy, archival process, query optimization |
| **Graph Database Scaling** | Support up to 1M nodes per project | Graph partitioning by project, index optimization, query result caching |
| **Storage Scaling** | Support up to 1TB of analysis data | Object storage (S3) for large artifacts, database for metadata only |
| **Network Bandwidth** | Support 100 Mbps sustained traffic | CDN for static assets, response compression, efficient serialization |

## 6.5 Compliance Constraints

| Constraint | Standard | Design Implication |
|------------|----------|-------------------|
| **Data Privacy** | GDPR, CCPA | User consent management, data export API, right to deletion, data minimization |
| **Security Standards** | SOC 2 Type II, OWASP Top 10 | Security controls, penetration testing, vulnerability scanning, audit trail |
| **Accessibility** | WCAG 2.1 Level AA | Keyboard navigation, screen reader support, color contrast, ARIA labels |
| **Code Quality** | ISO/IEC 25010 | Quality metrics calculation, compliance reporting, automated checks |
| **Architecture Standards** | ISO/IEC 23396 | Layer validation, dependency analysis, architectural drift detection |

## 6.6 Operational Constraints

| Constraint | Requirement | Design Implication |
|------------|-------------|-------------------|
| **Availability** | 99.5% uptime (43.8 hours downtime/year) | Multi-AZ deployment, health checks, automatic failover, graceful degradation |
| **Backup** | Daily full, hourly incremental | Automated backup scripts, 30-day retention, tested restore procedures |
| **Monitoring** | Real-time metrics and alerting | Prometheus metrics, Grafana dashboards, PagerDuty integration |
| **Deployment** | Zero-downtime deployments | Blue-green deployment, rolling updates, database migration strategy |
| **Disaster Recovery** | RTO 4 hours, RPO 1 hour | Multi-region backup, documented recovery procedures, quarterly DR drills |

# 7. Module-Level Detailed Specifications

## 7.1 AST Parser Module

**Module Path**: `services/code-review-engine/src/parsers/ast_parser.py`

**Purpose**: Parse source code into Abstract Syntax Trees for structural analysis

**Dependencies**: 
- Python: `ast`, `tree-sitter` (for multi-language support)
- Internal: `models.code_entity`, `utils.language_detector`

**Public Interface**:

```python
class ASTParser:
    def parse(self, code: str, language: str) -> AST:
        """Parse source code into AST
        
        Args:
            code: Source code string
            language: Programming language (python, javascript, typescript, java, go)
            
        Returns:
            AST object with root node
            
        Raises:
            SyntaxError: If code has syntax errors
            UnsupportedLanguageError: If language not supported
        """
        
    def extract_entities(self, ast: AST) -> List[CodeEntity]:
        """Extract code entities (classes, functions, variables) from AST
        
        Args:
            ast: Parsed AST object
            
        Returns:
            List of CodeEntity objects with metadata
        """
        
    def extract_dependencies(self, ast: AST) -> List[Dependency]:
        """Extract import and call dependencies from AST
        
        Args:
            ast: Parsed AST object
            
        Returns:
            List of Dependency objects (imports, function calls, inheritance)
        """
```

**Algorithm**:
1. Detect language if not specified (by file extension or content analysis)
2. Select appropriate parser (Python `ast` module or tree-sitter grammar)
3. Parse code into AST, catching and wrapping syntax errors
4. Traverse AST to extract entities (classes, functions, methods, variables)
5. Traverse AST to extract dependencies (imports, calls, inheritance)
6. Calculate complexity metrics (cyclomatic complexity, nesting depth)
7. Return structured AST with metadata

**Error Handling**:
- Syntax errors: Return partial AST with error annotations
- Unsupported language: Raise UnsupportedLanguageError with supported languages list
- Timeout: Abort parsing after 30 seconds, return timeout error

**Performance Considerations**:
- Cache parsed ASTs by file hash to avoid re-parsing unchanged files
- Use incremental parsing for large files (parse only changed sections)
- Limit AST depth to prevent stack overflow on deeply nested code

## 7.2 Dependency Graph Builder Module

**Module Path**: `services/architecture-analyzer/src/graph/graph_builder.py`

**Purpose**: Build and update dependency graphs in Neo4j from AST data

**Dependencies**:
- Neo4j Python driver
- Internal: `models.code_entity`, `models.dependency`, `database.neo4j_client`

**Public Interface**:

```python
class GraphBuilder:
    def build_graph(self, project_id: UUID, entities: List[CodeEntity], 
                   dependencies: List[Dependency]) -> GraphMetrics:
        """Build complete dependency graph for a project
        
        Args:
            project_id: Project identifier
            entities: List of code entities (modules, classes, functions)
            dependencies: List of dependencies between entities
            
        Returns:
            GraphMetrics with node/edge counts and build time
        """
        
    def update_graph(self, project_id: UUID, changed_files: List[str],
                    entities: List[CodeEntity], dependencies: List[Dependency]) -> GraphMetrics:
        """Incrementally update graph for changed files
        
        Args:
            project_id: Project identifier
            changed_files: List of file paths that changed
            entities: New/updated entities
            dependencies: New/updated dependencies
            
        Returns:
            GraphMetrics with updated counts
        """
        
    def delete_entities(self, project_id: UUID, file_paths: List[str]) -> int:
        """Delete entities and dependencies for removed files
        
        Args:
            project_id: Project identifier
            file_paths: List of deleted file paths
            
        Returns:
            Number of deleted nodes
        """
```

**Algorithm**:
1. Begin Neo4j transaction
2. For each entity: CREATE or MERGE node with properties
3. For each dependency: CREATE or MERGE relationship with properties
4. Create indexes on project_id, entity_name, file_path
5. Calculate graph metrics (node count, edge count, density)
6. Commit transaction
7. Return metrics

**Transaction Management**:
- Use explicit transactions for atomicity
- Batch operations in groups of 1000 for performance
- Rollback on any error to maintain consistency
- Retry transient failures up to 3 times with exponential backoff

**Performance Optimization**:
- Use MERGE instead of CREATE to handle duplicates
- Batch multiple operations in single transaction
- Use parameters to enable query plan caching
- Create indexes on frequently queried properties

## 7.3 Circular Dependency Detector Module

**Module Path**: `services/architecture-analyzer/src/analysis/circular_dependency_detector.py`

**Purpose**: Detect circular dependencies in dependency graphs using graph algorithms

**Dependencies**:
- NetworkX (for graph algorithms)
- Internal: `database.neo4j_client`, `models.circular_dependency`

**Public Interface**:

```python
class CircularDependencyDetector:
    def detect_cycles(self, project_id: UUID, max_cycle_length: int = 10) -> List[CircularDependency]:
        """Detect circular dependencies in project graph
        
        Args:
            project_id: Project identifier
            max_cycle_length: Maximum cycle length to detect (default 10)
            
        Returns:
            List of CircularDependency objects with cycle paths
        """
        
    def analyze_cycle_impact(self, cycle: CircularDependency) -> CycleImpact:
        """Analyze impact and severity of a circular dependency
        
        Args:
            cycle: CircularDependency object
            
        Returns:
            CycleImpact with severity, affected modules, suggested fixes
        """
```

**Algorithm** (Johnson's Algorithm for finding all cycles):
1. Query Neo4j for all DEPENDS_ON relationships in project
2. Build directed graph using NetworkX
3. Apply Johnson's algorithm to find all elementary cycles
4. Filter cycles by length (2 to max_cycle_length)
5. For each cycle:
   - Calculate severity based on cycle length and module coupling
   - Identify weakest link (lowest dependency strength)
   - Generate suggested fix (break weakest dependency)
6. Sort cycles by severity (descending)
7. Return list of CircularDependency objects

**Complexity Analysis**:
- Time: O((n + e)(c + 1)) where n=nodes, e=edges, c=cycles
- Space: O(n + e) for graph representation
- Practical limit: Graphs with < 10,000 nodes, < 100,000 edges

**Optimization Strategies**:
- Cache graph structure between analyses (invalidate on changes)
- Limit cycle detection to changed modules and their neighbors
- Use parallel processing for independent subgraphs
- Terminate early if cycle count exceeds threshold (100 cycles)

## 7.4 LLM Integration Module

**Module Path**: `services/agentic-ai/src/clients/llm_client.py`

**Purpose**: Integrate with multiple LLM providers for code analysis

**Dependencies**:
- OpenAI Python SDK
- Anthropic Python SDK
- Internal: `models.llm_request`, `models.llm_response`, `utils.rate_limiter`

**Public Interface**:

```python
class LLMClient:
    def analyze_code(self, code: str, context: ArchitecturalContext, 
                    analysis_type: AnalysisType) -> LLMAnalysis:
        """Analyze code using LLM with architectural context
        
        Args:
            code: Source code to analyze
            context: Architectural context (dependencies, patterns, violations)
            analysis_type: Type of analysis (security, performance, style, architecture)
            
        Returns:
            LLMAnalysis with issues, suggestions, and confidence scores
        """
        
    def generate_fix_suggestion(self, issue: Issue, code_context: str) -> FixSuggestion:
        """Generate code fix suggestion for an issue
        
        Args:
            issue: Detected issue
            code_context: Surrounding code context
            
        Returns:
            FixSuggestion with proposed code change and explanation
        """
```

**Prompt Engineering Strategy**:
1. **System Prompt**: Define role as expert code reviewer with architectural awareness
2. **Context Injection**: Include architectural patterns, dependency graph summary, compliance rules
3. **Code Snippet**: Provide code with line numbers and file path
4. **Analysis Instructions**: Specify analysis type, severity thresholds, output format
5. **Few-Shot Examples**: Include 2-3 examples of good analysis for consistency

**Provider Fallback Strategy**:
1. Primary: OpenAI GPT-4 (higher quality, slower)
2. Secondary: Anthropic Claude 3.5 Sonnet (faster, good quality)
3. Tertiary: Azure OpenAI (enterprise compliance)
4. Fallback: Rule-based analysis (no LLM, basic checks only)

**Rate Limiting**:
- OpenAI: 10 requests/minute, 10,000 tokens/minute
- Anthropic: 50 requests/minute, 100,000 tokens/minute
- Implement token bucket algorithm with Redis
- Queue requests when rate limit exceeded
- Return 429 error if queue full (> 100 requests)

**Error Handling**:
- Timeout (30s): Retry once, then fallback to next provider
- Rate limit: Queue request, retry after backoff period
- Invalid response: Log error, return empty analysis with error flag
- API key invalid: Alert admin, disable provider, use fallback

## 7.5 Drift Detection Module

**Module Path**: `services/architecture-analyzer/src/analysis/drift_detector.py`

**Purpose**: Detect architectural drift by comparing current architecture against baseline

**Dependencies**:
- Internal: `database.neo4j_client`, `models.architecture_baseline`, `models.drift_report`

**Public Interface**:

```python
class DriftDetector:
    def detect_drift(self, project_id: UUID, baseline_id: UUID) -> DriftReport:
        """Detect architectural drift from baseline
        
        Args:
            project_id: Project identifier
            baseline_id: Baseline architecture identifier
            
        Returns:
            DriftReport with violations, new dependencies, removed dependencies
        """
        
    def create_baseline(self, project_id: UUID, description: str) -> ArchitectureBaseline:
        """Create new architecture baseline from current state
        
        Args:
            project_id: Project identifier
            description: Baseline description
            
        Returns:
            ArchitectureBaseline object
        """
```

**Drift Detection Algorithm**:
1. Load baseline architecture (graph snapshot)
2. Load current architecture from Neo4j
3. Compare module structures:
   - New modules (in current, not in baseline)
   - Removed modules (in baseline, not in current)
   - Modified modules (different properties)
4. Compare dependencies:
   - New dependencies (potential coupling increase)
   - Removed dependencies (potential breaking changes)
   - Strengthened dependencies (increased coupling)
5. Detect layer violations:
   - Dependencies that skip architectural layers
   - Reverse dependencies (lower layer depends on higher layer)
6. Calculate drift score (0-100, higher = more drift)
7. Generate recommendations for remediation
8. Return DriftReport

**Drift Scoring Formula**:
```
drift_score = (
    new_dependencies_weight * new_deps_count +
    removed_dependencies_weight * removed_deps_count +
    layer_violations_weight * violations_count +
    circular_dependencies_weight * cycles_count
) / total_modules * 100

Weights: new_deps=1, removed_deps=2, violations=5, cycles=10
```

**Baseline Storage**:
- Store baseline as JSON snapshot in PostgreSQL
- Include: module list, dependency list, layer definitions, timestamp
- Compress large baselines (> 1MB) using gzip
- Retain last 10 baselines per project



# 8. Core Algorithm Designs

## 8.1 Circular Dependency Detection Algorithm

**Algorithm**: Johnson's Algorithm (modified for weighted directed graphs)

**Input**: Directed graph G = (V, E) where V = modules, E = dependencies

**Output**: List of all elementary cycles with severity scores

**Pseudocode**:
```
function find_all_cycles(graph G, max_length):
    cycles = []
    
    for each strongly connected component SCC in G:
        if |SCC| == 1 and no self-loop:
            continue  // Skip trivial components
            
        subgraph = induced_subgraph(G, SCC)
        
        for each vertex v in subgraph:
            blocked = set()
            blocked_map = {}
            stack = [v]
            path = []
            
            circuit(v, v, blocked, blocked_map, stack, path, cycles, max_length)
    
    return rank_cycles_by_severity(cycles)

function circuit(start, current, blocked, blocked_map, stack, path, cycles, max_length):
    if len(path) >= max_length:
        return false
        
    path.append(current)
    blocked.add(current)
    cycle_found = false
    
    for each neighbor in adjacency_list[current]:
        if neighbor == start:
            cycles.append(copy(path))
            cycle_found = true
        else if neighbor not in blocked:
            if circuit(start, neighbor, blocked, blocked_map, stack, path, cycles, max_length):
                cycle_found = true
    
    if cycle_found:
        unblock(current, blocked, blocked_map)
    else:
        for each neighbor in adjacency_list[current]:
            if current not in blocked_map[neighbor]:
                blocked_map[neighbor].add(current)
    
    path.pop()
    return cycle_found
```

**Complexity**:
- Time: O((n + e)(c + 1)) where c = number of cycles
- Space: O(n + e) for graph + O(n) for recursion stack
- Practical limit: n < 10,000 nodes

**Optimization**:
- Early termination if cycle count > 100
- Skip nodes with no outgoing edges
- Cache strongly connected components
- Parallel processing for independent SCCs

## 8.2 Complexity Calculation Algorithm

**Algorithm**: McCabe Cyclomatic Complexity

**Formula**: `M = E - N + 2P`
- E = number of edges in control flow graph
- N = number of nodes in control flow graph
- P = number of connected components (usually 1)

**Implementation**:
```python
def calculate_complexity(ast_node):
    """Calculate cyclomatic complexity from AST node"""
    complexity = 1  # Base complexity
    
    # Decision points that increase complexity
    decision_keywords = {
        'if', 'elif', 'else', 'for', 'while', 'and', 'or',
        'case', 'catch', 'except', 'finally', '?', '&&', '||'
    }
    
    for node in ast.walk(ast_node):
        if isinstance(node, (ast.If, ast.While, ast.For)):
            complexity += 1
        elif isinstance(node, ast.BoolOp):
            complexity += len(node.values) - 1
        elif isinstance(node, (ast.ExceptHandler, ast.Try)):
            complexity += 1
        elif isinstance(node, ast.Match):  # Python 3.10+
            complexity += len(node.cases)
    
    return complexity
```

**Interpretation**:
- 1-10: Simple, low risk
- 11-20: Moderate complexity, medium risk
- 21-50: High complexity, high risk
- 50+: Very high complexity, very high risk

## 8.3 Layer Violation Detection Algorithm

**Algorithm**: Path-based layer validation

**Layer Hierarchy** (top to bottom):
1. Presentation (UI, API routes)
2. Application (Business logic, orchestration)
3. Domain (Core business entities, rules)
4. Infrastructure (Database, external services)

**Rules**:
- Each layer can only depend on layers below it
- No layer can depend on layers above it
- No layer can skip intermediate layers

**Implementation**:
```python
def detect_layer_violations(dependencies, layer_map):
    """Detect dependencies that violate layer architecture
    
    Args:
        dependencies: List of (source_module, target_module) tuples
        layer_map: Dict mapping module paths to layer names
        
    Returns:
        List of LayerViolation objects
    """
    violations = []
    layer_order = ['presentation', 'application', 'domain', 'infrastructure']
    
    for source, target in dependencies:
        source_layer = get_layer(source, layer_map)
        target_layer = get_layer(target, layer_map)
        
        if source_layer is None or target_layer is None:
            continue  // Skip unclassified modules
        
        source_level = layer_order.index(source_layer)
        target_level = layer_order.index(target_layer)
        
        # Violation: depending on higher layer
        if target_level < source_level:
            violations.append(LayerViolation(
                source=source,
                target=target,
                source_layer=source_layer,
                target_layer=target_layer,
                violation_type='UPWARD_DEPENDENCY',
                severity='HIGH'
            ))
        
        # Violation: skipping intermediate layer
        elif target_level - source_level > 1:
            skipped_layers = layer_order[source_level+1:target_level]
            violations.append(LayerViolation(
                source=source,
                target=target,
                source_layer=source_layer,
                target_layer=target_layer,
                violation_type='LAYER_SKIP',
                severity='MEDIUM',
                skipped_layers=skipped_layers
            ))
    
    return violations
```

## 8.4 Code Quality Score Calculation Algorithm

**Formula**: Weighted average of multiple quality metrics

```
quality_score = (
    test_coverage_weight * normalize(test_coverage, 0, 100) +
    complexity_weight * normalize(100 - avg_complexity, 0, 100) +
    duplication_weight * normalize(100 - duplication_pct, 0, 100) +
    issues_weight * normalize(100 - issue_density, 0, 100) +
    documentation_weight * normalize(doc_coverage, 0, 100)
) / total_weight

Weights:
- test_coverage: 30%
- complexity: 25%
- duplication: 20%
- issues: 15%
- documentation: 10%
```

**Normalization**:
```python
def normalize(value, min_val, max_val):
    """Normalize value to 0-100 scale"""
    if value < min_val:
        return 0
    if value > max_val:
        return 100
    return ((value - min_val) / (max_val - min_val)) * 100
```

**Issue Density Calculation**:
```
issue_density = (critical_issues * 10 + high_issues * 5 + 
                 medium_issues * 2 + low_issues * 1) / (lines_of_code / 1000)
```

## 8.5 LLM Prompt Engineering Algorithm

**Strategy**: Few-shot learning with architectural context injection

**Prompt Template**:
```
System: You are an expert code reviewer with deep knowledge of software architecture, 
design patterns, and best practices. Analyze code for quality, security, performance, 
and architectural compliance.

Context:
- Project: {project_name}
- Language: {language}
- Architecture Pattern: {architecture_pattern}
- Compliance Standards: {standards}

Architectural Context:
- Module Layer: {layer}
- Dependencies: {dependency_summary}
- Circular Dependencies: {circular_deps}
- Complexity: {avg_complexity}

Code to Review:
File: {file_path}
Lines: {line_start}-{line_end}

```{language}
{code_snippet}
```

Instructions:
1. Identify code quality issues (bugs, code smells, anti-patterns)
2. Check for security vulnerabilities (OWASP Top 10)
3. Evaluate performance implications
4. Verify architectural compliance (layer violations, coupling)
5. Assess maintainability and readability

For each issue found, provide:
- Severity: CRITICAL | HIGH | MEDIUM | LOW
- Category: SECURITY | PERFORMANCE | MAINTAINABILITY | ARCHITECTURE | STYLE
- Description: Clear explanation of the issue
- Location: Specific line numbers
- Suggestion: Concrete fix recommendation with code example

Output Format: JSON array of issues

Examples:
{few_shot_examples}

Begin analysis:
```

**Few-Shot Examples** (2-3 examples per analysis type):
```json
[
  {
    "severity": "HIGH",
    "category": "SECURITY",
    "description": "SQL injection vulnerability: user input directly concatenated into query",
    "line_number": 42,
    "suggestion": "Use parameterized queries: cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))"
  },
  {
    "severity": "MEDIUM",
    "category": "ARCHITECTURE",
    "description": "Layer violation: presentation layer directly accessing data layer",
    "line_number": 15,
    "suggestion": "Introduce service layer method to encapsulate data access logic"
  }
]
```

**Response Parsing**:
1. Extract JSON from LLM response (handle markdown code blocks)
2. Validate JSON schema
3. Filter issues by confidence score (> 0.7)
4. Deduplicate similar issues (cosine similarity > 0.9)
5. Rank by severity and confidence
6. Return top N issues (default: 20)

# 9. Global Exception Handling Architecture

## 9.1 Exception Hierarchy

```
BaseApplicationException
├── AuthenticationException
│   ├── InvalidCredentialsException
│   ├── TokenExpiredException
│   ├── TokenInvalidException
│   └── AccountLockedException
├── AuthorizationException
│   ├── InsufficientPermissionsException
│   └── ResourceAccessDeniedException
├── ValidationException
│   ├── InvalidInputException
│   ├── SchemaValidationException
│   └── BusinessRuleViolationException
├── ResourceException
│   ├── ResourceNotFoundException
│   ├── ResourceAlreadyExistsException
│   └── ResourceConflictException
├── ExternalServiceException
│   ├── GitHubAPIException
│   ├── LLMAPIException
│   ├── DatabaseException
│   └── CacheException
├── AnalysisException
│   ├── ParsingException
│   ├── AnalysisTimeoutException
│   └── UnsupportedLanguageException
└── SystemException
    ├── ConfigurationException
    ├── InternalServerException
    └── ServiceUnavailableException
```

## 9.2 Exception Handling Strategy

**Principle**: Fail fast, log comprehensively, recover gracefully

**Layers**:

1. **Application Layer** (FastAPI routes):
   - Catch all exceptions
   - Map to HTTP status codes
   - Return standardized error responses
   - Log with request context

2. **Service Layer** (Business logic):
   - Catch and wrap external exceptions
   - Add business context
   - Propagate to application layer
   - Log with operation context

3. **Data Layer** (Database, external APIs):
   - Catch low-level exceptions
   - Wrap in domain exceptions
   - Retry transient failures
   - Log with technical details

## 9.3 Global Exception Handler (FastAPI)

```python
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging

app = FastAPI()
logger = logging.getLogger(__name__)

@app.exception_handler(BaseApplicationException)
async def application_exception_handler(request: Request, exc: BaseApplicationException):
    """Handle all application-specific exceptions"""
    logger.error(
        f"Application exception: {exc.__class__.__name__}",
        extra={
            "exception_type": exc.__class__.__name__,
            "message": str(exc),
            "path": request.url.path,
            "method": request.method,
            "user_id": getattr(request.state, "user_id", None),
            "request_id": getattr(request.state, "request_id", None)
        },
        exc_info=True
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "type": exc.error_type,
                "message": exc.message,
                "details": exc.details,
                "request_id": getattr(request.state, "request_id", None),
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors"""
    logger.warning(
        "Validation error",
        extra={
            "path": request.url.path,
            "errors": exc.errors()
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "type": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "details": exc.errors(),
                "request_id": getattr(request.state, "request_id", None)
            }
        }
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Catch-all handler for unexpected exceptions"""
    logger.critical(
        f"Unhandled exception: {exc.__class__.__name__}",
        extra={
            "exception_type": exc.__class__.__name__,
            "message": str(exc),
            "path": request.url.path,
            "method": request.method,
            "user_id": getattr(request.state, "user_id", None),
            "request_id": getattr(request.state, "request_id", None)
        },
        exc_info=True
    )
    
    # Don't expose internal error details to client
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "type": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred. Please try again later.",
                "request_id": getattr(request.state, "request_id", None),
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    )
```

## 9.4 Retry Strategy for Transient Failures

```python
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type((ConnectionError, TimeoutError, ServiceUnavailableException)),
    reraise=True
)
async def call_external_service(url: str, payload: dict):
    """Call external service with automatic retry on transient failures"""
    try:
        response = await http_client.post(url, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()
    except httpx.TimeoutException as e:
        logger.warning(f"Request timeout: {url}", exc_info=True)
        raise TimeoutError(f"Request to {url} timed out") from e
    except httpx.HTTPStatusError as e:
        if e.response.status_code >= 500:
            logger.error(f"Server error from {url}: {e.response.status_code}")
            raise ServiceUnavailableException(f"Service {url} unavailable") from e
        else:
            logger.error(f"Client error from {url}: {e.response.status_code}")
            raise ExternalServiceException(f"Request to {url} failed: {e.response.text}") from e
```

## 9.5 Circuit Breaker Pattern

```python
from circuitbreaker import circuit

@circuit(failure_threshold=5, recovery_timeout=60, expected_exception=ExternalServiceException)
async def call_llm_api(prompt: str, model: str):
    """Call LLM API with circuit breaker to prevent cascading failures"""
    try:
        response = await llm_client.complete(prompt=prompt, model=model)
        return response
    except Exception as e:
        logger.error(f"LLM API call failed: {str(e)}")
        raise ExternalServiceException("LLM API unavailable") from e
```

**Circuit States**:
- **Closed**: Normal operation, requests pass through
- **Open**: Failure threshold exceeded, requests fail immediately
- **Half-Open**: After recovery timeout, allow one test request

## 9.6 Error Response Format

**Standard Error Response**:
```json
{
  "error": {
    "type": "RESOURCE_NOT_FOUND",
    "message": "Project with ID 'abc-123' not found",
    "details": {
      "resource_type": "project",
      "resource_id": "abc-123"
    },
    "request_id": "req_7f8a9b2c",
    "timestamp": "2026-02-20T10:30:00Z",
    "documentation_url": "https://docs.example.com/errors/resource-not-found"
  }
}
```

**HTTP Status Code Mapping**:
- 400: ValidationException, InvalidInputException
- 401: AuthenticationException, TokenExpiredException
- 403: AuthorizationException, InsufficientPermissionsException
- 404: ResourceNotFoundException
- 409: ResourceConflictException, ResourceAlreadyExistsException
- 422: SchemaValidationException, BusinessRuleViolationException
- 429: RateLimitExceededException
- 500: InternalServerException, SystemException
- 502: ExternalServiceException (upstream failure)
- 503: ServiceUnavailableException
- 504: AnalysisTimeoutException, GatewayTimeoutException



# 10. Detailed Security Design

## 10.1 Security Architecture Overview

**Defense in Depth Strategy**: Multiple layers of security controls

```
┌─────────────────────────────────────────────────────────────┐
│ Layer 1: Network Security                                   │
│ - WAF (Web Application Firewall)                            │
│ - DDoS Protection                                            │
│ - TLS 1.3 Encryption                                         │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Layer 2: API Gateway Security                               │
│ - Rate Limiting (100 req/min per user)                      │
│ - IP Whitelisting (optional)                                │
│ - Request Size Limits (10MB max)                            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Layer 3: Authentication & Authorization                     │
│ - JWT Token Validation                                      │
│ - RBAC Permission Checking                                  │
│ - Session Management                                         │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Layer 4: Application Security                               │
│ - Input Validation (Pydantic)                               │
│ - SQL Injection Prevention (Parameterized Queries)          │
│ - XSS Protection (Output Encoding)                          │
│ - CSRF Protection (Token Validation)                        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Layer 5: Data Security                                      │
│ - Encryption at Rest (AES-256)                              │
│ - Encryption in Transit (TLS 1.3)                           │
│ - Secure Key Management (AWS KMS)                           │
│ - Data Masking (PII in logs)                                │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Layer 6: Monitoring & Audit                                 │
│ - Security Event Logging                                    │
│ - Intrusion Detection                                       │
│ - Audit Trail (7-year retention)                            │
└─────────────────────────────────────────────────────────────┘
```

## 10.2 Authentication Security

### 10.2.1 Password Security

**Hashing Algorithm**: bcrypt with cost factor 12

```python
import bcrypt

def hash_password(password: str) -> str:
    """Hash password using bcrypt with salt"""
    salt = bcrypt.gensalt(rounds=12)  # 2^12 iterations
    password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
    return password_hash.decode('utf-8')

def verify_password(password: str, password_hash: str) -> bool:
    """Verify password against stored hash"""
    return bcrypt.checkpw(
        password.encode('utf-8'),
        password_hash.encode('utf-8')
    )
```

**Password Policy**:
- Minimum length: 8 characters
- Must contain: uppercase, lowercase, digit, special character
- Password history: Last 5 passwords cannot be reused
- Account lockout: 5 failed attempts → 15-minute lockout
- Password expiry: 90 days (optional, configurable)

**Password Validation**:
```python
import re

def validate_password(password: str) -> tuple[bool, str]:
    """Validate password against policy"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain digit"
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain special character"
    
    # Check against common passwords list
    if password.lower() in COMMON_PASSWORDS:
        return False, "Password is too common"
    
    return True, "Password is valid"
```

### 10.2.2 JWT Token Security

**Token Structure**:
```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "user_id": "uuid",
    "username": "string",
    "role": "string",
    "iat": 1234567890,
    "exp": 1234654290,
    "jti": "unique-token-id"
  },
  "signature": "HMACSHA256(base64UrlEncode(header) + '.' + base64UrlEncode(payload), secret)"
}
```

**Token Generation**:
```python
import jwt
from datetime import datetime, timedelta
import secrets

def generate_jwt_token(user_id: str, username: str, role: str) -> str:
    """Generate JWT access token"""
    now = datetime.utcnow()
    payload = {
        "user_id": user_id,
        "username": username,
        "role": role,
        "iat": now,
        "exp": now + timedelta(hours=24),
        "jti": secrets.token_urlsafe(32)  # Unique token ID
    }
    
    token = jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm="HS256"
    )
    
    return token

def validate_jwt_token(token: str) -> Optional[dict]:
    """Validate and decode JWT token"""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=["HS256"],
            options={"verify_exp": True}
        )
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Token expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.error(f"Invalid token: {str(e)}")
        return None
```

**Token Storage**:
- Client: Store in httpOnly cookie (not localStorage to prevent XSS)
- Server: Store token JTI in Redis for revocation capability
- Expiry: 24 hours for access token, 7 days for refresh token

**Token Revocation**:
```python
async def revoke_token(token_jti: str):
    """Revoke token by adding JTI to blacklist"""
    await redis_client.setex(
        f"revoked_token:{token_jti}",
        timedelta(days=7),  # Keep in blacklist until expiry
        "1"
    )

async def is_token_revoked(token_jti: str) -> bool:
    """Check if token is revoked"""
    return await redis_client.exists(f"revoked_token:{token_jti}")
```

## 10.3 Authorization Security (RBAC)

**Permission Enforcement**:
```python
from functools import wraps
from fastapi import Depends, HTTPException, status

def require_permission(permission: Permission):
    """Decorator to enforce permission requirement"""
    async def permission_checker(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        if not RBACService.has_permission(db, current_user.id, permission):
            logger.warning(
                f"Permission denied: {current_user.username} attempted {permission}",
                extra={"user_id": current_user.id, "permission": permission}
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions: {permission} required"
            )
        return current_user
    
    return permission_checker

# Usage in route
@router.delete("/users/{user_id}")
async def delete_user(
    user_id: UUID,
    current_user: User = Depends(require_permission(Permission.DELETE_USER)),
    db: Session = Depends(get_db)
):
    # Only users with DELETE_USER permission can access this endpoint
    ...
```

**Project-Level Access Control**:
```python
def require_project_access(permission: Permission):
    """Decorator to enforce project-level access"""
    async def access_checker(
        project_id: UUID,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        if not RBACService.can_access_project(db, current_user.id, project_id, permission):
            logger.warning(
                f"Project access denied: {current_user.username} attempted {permission} on project {project_id}",
                extra={"user_id": current_user.id, "project_id": project_id, "permission": permission}
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied to project {project_id}"
            )
        return current_user
    
    return access_checker
```

## 10.4 Input Validation and Sanitization

**Pydantic Models for Validation**:
```python
from pydantic import BaseModel, Field, validator, constr
import re

class RegisterRequest(BaseModel):
    username: constr(min_length=3, max_length=30, regex=r'^[a-zA-Z][a-zA-Z0-9_]*$')
    email: constr(regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    password: constr(min_length=8, max_length=128)
    
    @validator('username')
    def username_no_reserved_words(cls, v):
        reserved = ['admin', 'root', 'system', 'api', 'null']
        if v.lower() in reserved:
            raise ValueError('Username is reserved')
        return v
    
    @validator('email')
    def email_domain_allowed(cls, v):
        # Optional: whitelist/blacklist email domains
        domain = v.split('@')[1]
        if domain in BLOCKED_DOMAINS:
            raise ValueError('Email domain not allowed')
        return v.lower()

class CreateProjectRequest(BaseModel):
    name: constr(min_length=1, max_length=200)
    github_url: constr(regex=r'^https://github\.com/[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+$')
    
    @validator('github_url')
    def validate_github_url(cls, v):
        # Additional validation: check repository exists and is accessible
        return v
```

**SQL Injection Prevention**:
```python
# GOOD: Parameterized query
def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()

# GOOD: SQLAlchemy ORM (automatically parameterized)
def get_projects_by_owner(db: Session, owner_id: UUID) -> List[Project]:
    return db.query(Project).filter(Project.owner_id == owner_id).all()

# BAD: String concatenation (NEVER DO THIS)
# query = f"SELECT * FROM users WHERE username = '{username}'"
```

**XSS Prevention**:
```python
import html
import bleach

def sanitize_html(content: str) -> str:
    """Sanitize HTML content to prevent XSS"""
    # Allow only safe tags and attributes
    allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'a', 'code', 'pre']
    allowed_attributes = {'a': ['href', 'title']}
    
    cleaned = bleach.clean(
        content,
        tags=allowed_tags,
        attributes=allowed_attributes,
        strip=True
    )
    
    return cleaned

def escape_output(text: str) -> str:
    """Escape HTML entities in output"""
    return html.escape(text)
```

## 10.5 Encryption and Key Management

### 10.5.1 Encryption at Rest

**Database Encryption** (PostgreSQL):
```sql
-- Enable transparent data encryption
ALTER SYSTEM SET ssl = on;
ALTER SYSTEM SET ssl_cert_file = '/path/to/server.crt';
ALTER SYSTEM SET ssl_key_file = '/path/to/server.key';

-- Encrypt specific columns (for PII)
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Encrypt sensitive data
INSERT INTO users (email, encrypted_ssn)
VALUES ('user@example.com', pgp_sym_encrypt('123-45-6789', 'encryption_key'));

-- Decrypt when querying
SELECT email, pgp_sym_decrypt(encrypted_ssn, 'encryption_key') AS ssn
FROM users;
```

**File Encryption** (for stored artifacts):
```python
from cryptography.fernet import Fernet
import base64

class EncryptionService:
    def __init__(self, key: bytes):
        self.cipher = Fernet(key)
    
    def encrypt_file(self, file_path: str) -> str:
        """Encrypt file and return encrypted file path"""
        with open(file_path, 'rb') as f:
            plaintext = f.read()
        
        ciphertext = self.cipher.encrypt(plaintext)
        
        encrypted_path = f"{file_path}.encrypted"
        with open(encrypted_path, 'wb') as f:
            f.write(ciphertext)
        
        return encrypted_path
    
    def decrypt_file(self, encrypted_path: str) -> bytes:
        """Decrypt file and return plaintext"""
        with open(encrypted_path, 'rb') as f:
            ciphertext = f.read()
        
        plaintext = self.cipher.decrypt(ciphertext)
        return plaintext
```

### 10.5.2 Key Management (AWS KMS)

```python
import boto3
from botocore.exceptions import ClientError

class KeyManagementService:
    def __init__(self):
        self.kms_client = boto3.client('kms', region_name='us-east-1')
        self.key_id = 'arn:aws:kms:us-east-1:123456789012:key/12345678-1234-1234-1234-123456789012'
    
    def encrypt_data(self, plaintext: str) -> str:
        """Encrypt data using KMS"""
        try:
            response = self.kms_client.encrypt(
                KeyId=self.key_id,
                Plaintext=plaintext.encode('utf-8')
            )
            ciphertext = base64.b64encode(response['CiphertextBlob']).decode('utf-8')
            return ciphertext
        except ClientError as e:
            logger.error(f"KMS encryption failed: {str(e)}")
            raise
    
    def decrypt_data(self, ciphertext: str) -> str:
        """Decrypt data using KMS"""
        try:
            ciphertext_blob = base64.b64decode(ciphertext)
            response = self.kms_client.decrypt(
                CiphertextBlob=ciphertext_blob
            )
            plaintext = response['Plaintext'].decode('utf-8')
            return plaintext
        except ClientError as e:
            logger.error(f"KMS decryption failed: {str(e)}")
            raise
    
    def rotate_key(self):
        """Enable automatic key rotation"""
        try:
            self.kms_client.enable_key_rotation(KeyId=self.key_id)
            logger.info(f"Key rotation enabled for {self.key_id}")
        except ClientError as e:
            logger.error(f"Key rotation failed: {str(e)}")
            raise
```

**Key Rotation Policy**:
- Automatic rotation: Every 365 days
- Manual rotation: On security incident or key compromise
- Old keys retained for decryption of existing data
- New keys used for all new encryption operations

## 10.6 OWASP Top 10 Protection

| OWASP Risk | Protection Mechanism | Implementation |
|------------|---------------------|----------------|
| **A01: Broken Access Control** | RBAC, permission checks, project-level access control | Middleware enforces permissions on every request |
| **A02: Cryptographic Failures** | TLS 1.3, AES-256, bcrypt, secure key management | All data encrypted in transit and at rest |
| **A03: Injection** | Parameterized queries, input validation, output encoding | SQLAlchemy ORM, Pydantic validation |
| **A04: Insecure Design** | Threat modeling, security requirements, secure SDLC | Architecture review, security testing |
| **A05: Security Misconfiguration** | Secure defaults, configuration management, hardening | Infrastructure as Code, security baselines |
| **A06: Vulnerable Components** | Dependency scanning, automated updates, SCA | Snyk, OWASP Dependency-Check, Renovate |
| **A07: Authentication Failures** | Strong password policy, MFA (future), account lockout | bcrypt, JWT, session management |
| **A08: Software and Data Integrity** | Code signing, integrity checks, secure CI/CD | Git commit signing, artifact checksums |
| **A09: Logging and Monitoring** | Comprehensive logging, SIEM integration, alerting | Structured logging, audit trail, monitoring |
| **A10: Server-Side Request Forgery** | URL validation, whitelist, network segmentation | Input validation, firewall rules |

## 10.7 Security Monitoring and Incident Response

**Security Event Logging**:
```python
import logging
from pythonjsonlogger import jsonlogger

# Configure structured logging
logger = logging.getLogger()
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter(
    '%(timestamp)s %(level)s %(name)s %(message)s %(user_id)s %(ip_address)s %(action)s'
)
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)

# Log security events
def log_security_event(event_type: str, user_id: str, ip_address: str, details: dict):
    logger.info(
        f"Security event: {event_type}",
        extra={
            "event_type": event_type,
            "user_id": user_id,
            "ip_address": ip_address,
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

# Examples
log_security_event("LOGIN_SUCCESS", user_id, ip_address, {"username": username})
log_security_event("LOGIN_FAILED", None, ip_address, {"username": username, "reason": "invalid_password"})
log_security_event("PERMISSION_DENIED", user_id, ip_address, {"resource": "project_123", "action": "delete"})
log_security_event("SUSPICIOUS_ACTIVITY", user_id, ip_address, {"pattern": "rapid_requests", "count": 100})
```

**Intrusion Detection**:
- Monitor for brute force attacks (> 10 failed logins in 5 minutes)
- Detect unusual access patterns (access from new location/device)
- Alert on privilege escalation attempts
- Track API abuse (rate limit violations, unusual endpoints)

**Incident Response Plan**:
1. **Detection**: Automated alerts trigger incident
2. **Containment**: Revoke compromised tokens, block IP addresses
3. **Investigation**: Review audit logs, identify scope
4. **Eradication**: Patch vulnerabilities, rotate keys
5. **Recovery**: Restore services, verify integrity
6. **Lessons Learned**: Post-mortem, update security controls



# 11. Deployment and Network Architecture

## 11.1 Deployment Topology

**Production Environment** (AWS Multi-AZ):

```
┌─────────────────────────────────────────────────────────────────┐
│ Route 53 (DNS)                                                   │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│ CloudFront CDN (Static Assets)                                   │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│ Application Load Balancer (ALB)                                  │
│ - SSL Termination (TLS 1.3)                                      │
│ - Health Checks                                                  │
│ - Sticky Sessions                                                │
└──────────┬──────────────────────────────────┬───────────────────┘
           │                                  │
    ┌──────▼──────┐                    ┌──────▼──────┐
    │   AZ-1a     │                    │   AZ-1b     │
    │             │                    │             │
    │ ┌─────────┐ │                    │ ┌─────────┐ │
    │ │Frontend │ │                    │ │Frontend │ │
    │ │ (ECS)   │ │                    │ │ (ECS)   │ │
    │ └────┬────┘ │                    │ └────┬────┘ │
    │      │      │                    │      │      │
    │ ┌────▼────┐ │                    │ ┌────▼────┐ │
    │ │API      │ │                    │ │API      │ │
    │ │Gateway  │ │                    │ │Gateway  │ │
    │ └────┬────┘ │                    │ └────┬────┘ │
    │      │      │                    │      │      │
    │ ┌────▼────┐ │                    │ ┌────▼────┐ │
    │ │Services │ │                    │ │Services │ │
    │ │(ECS)    │ │                    │ │(ECS)    │ │
    │ └────┬────┘ │                    │ └────┬────┘ │
    │      │      │                    │      │      │
    │ ┌────▼────┐ │                    │ ┌────▼────┐ │
    │ │Workers  │ │                    │ │Workers  │ │
    │ │(ECS)    │ │                    │ │(ECS)    │ │
    │ └─────────┘ │                    │ └─────────┘ │
    └──────┬──────┘                    └──────┬──────┘
           │                                  │
           └──────────────┬───────────────────┘
                          │
        ┌─────────────────▼─────────────────┐
        │ Data Layer (Multi-AZ)              │
        │ - RDS PostgreSQL (Primary + Read)  │
        │ - ElastiCache Redis (Cluster)      │
        │ - Neo4j (EC2 Cluster)              │
        │ - S3 (Artifacts, Backups)          │
        └────────────────────────────────────┘
```



## 11.2 Container Specifications

**Frontend Container** (Next.js):
```dockerfile
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

FROM node:18-alpine
WORKDIR /app
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json
EXPOSE 3000
CMD ["npm", "start"]
```

**Backend Service Container** (FastAPI):
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

**Resource Limits** (Kubernetes):
```yaml
resources:
  requests:
    memory: "512Mi"
    cpu: "500m"
  limits:
    memory: "2Gi"
    cpu: "2000m"
```



## 11.3 Network Security

**VPC Configuration**:
- Public Subnets: ALB, NAT Gateway
- Private Subnets: ECS tasks, RDS, ElastiCache
- Isolated Subnets: Neo4j cluster

**Security Groups**:
```
ALB Security Group:
- Inbound: 443 (HTTPS) from 0.0.0.0/0
- Outbound: 3000 (Frontend), 8000-8005 (Services)

Service Security Group:
- Inbound: 8000-8005 from ALB SG
- Outbound: 5432 (PostgreSQL), 6379 (Redis), 7687 (Neo4j)

Database Security Group:
- Inbound: 5432 from Service SG
- Outbound: None

Redis Security Group:
- Inbound: 6379 from Service SG
- Outbound: None

Neo4j Security Group:
- Inbound: 7687 from Service SG
- Outbound: None
```

**Network ACLs**:
- Block known malicious IPs
- Rate limiting at network level
- DDoS protection via AWS Shield



# 12. Performance Optimization Design

## 12.1 Caching Strategy

**Multi-Level Caching**:
1. **CDN Cache** (CloudFront): Static assets, 24-hour TTL
2. **Application Cache** (Redis): API responses, 5-minute TTL
3. **Database Query Cache**: Frequently accessed data, 1-minute TTL
4. **LLM Response Cache**: Analysis results by code hash, 7-day TTL

**Cache Invalidation**:
- Time-based: TTL expiration
- Event-based: On data modification (write-through)
- Manual: Admin API endpoint for cache clearing

## 12.2 Database Optimization

**Indexing Strategy**:
```sql
-- Users table
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_role ON users(role);

-- Projects table
CREATE INDEX idx_projects_owner_id ON projects(owner_id);
CREATE INDEX idx_projects_github_url ON projects(github_url);

-- Analyses table
CREATE INDEX idx_analyses_pr_id ON analyses(pr_id);
CREATE INDEX idx_analyses_status ON analyses(status);
CREATE INDEX idx_analyses_completed_at ON analyses(completed_at);

-- Issues table
CREATE INDEX idx_issues_analysis_id ON issues(analysis_id);
CREATE INDEX idx_issues_severity ON issues(severity);
CREATE INDEX idx_issues_file_path ON issues(file_path);

-- Composite indexes
CREATE INDEX idx_analyses_status_completed ON analyses(status, completed_at);
CREATE INDEX idx_issues_analysis_severity ON issues(analysis_id, severity);
```

**Query Optimization**:
- Use EXPLAIN ANALYZE for slow queries
- Avoid N+1 queries (use eager loading)
- Limit result sets with pagination
- Use database views for complex joins

**Connection Pooling**:
```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,          # Max connections
    max_overflow=10,       # Additional connections
    pool_timeout=30,       # Wait timeout
    pool_recycle=3600,     # Recycle after 1 hour
    pool_pre_ping=True     # Verify connection before use
)
```

## 12.3 Asynchronous Processing

**Task Queue Design**:
```python
from celery import Celery, Task
from celery.result import AsyncResult

app = Celery('tasks', broker='redis://localhost:6379/0')

@app.task(bind=True, max_retries=3)
def analyze_pull_request(self, pr_id: str):
    try:
        # Long-running analysis
        result = perform_analysis(pr_id)
        return result
    except Exception as exc:
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)

# Queue task
task = analyze_pull_request.delay(pr_id)

# Check status
result = AsyncResult(task.id)
if result.ready():
    output = result.get()
```

**Worker Configuration**:
- Concurrency: 4 workers per instance
- Prefetch: 1 task per worker (to prevent blocking)
- Task timeout: 10 minutes
- Result backend: Redis (for status tracking)



# 13. Maintainability and Observability Design

## 13.1 Logging Strategy

**Structured Logging** (JSON format):
```python
import logging
import json
from datetime import datetime

class StructuredLogger:
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
    
    def log(self, level: str, message: str, **kwargs):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "service": "code-review-engine",
            "message": message,
            **kwargs
        }
        self.logger.log(getattr(logging, level), json.dumps(log_entry))

# Usage
logger = StructuredLogger(__name__)
logger.log("INFO", "Analysis started", pr_id="123", user_id="abc")
```

**Log Levels**:
- DEBUG: Detailed diagnostic information
- INFO: General informational messages
- WARNING: Warning messages (degraded performance, deprecated features)
- ERROR: Error messages (handled exceptions)
- CRITICAL: Critical errors (system failures)

**Log Aggregation**:
- Centralized logging: ELK Stack (Elasticsearch, Logstash, Kibana)
- Log retention: 90 days for application logs, 7 years for audit logs
- Log analysis: Automated anomaly detection, alerting

## 13.2 Monitoring and Metrics

**Prometheus Metrics**:
```python
from prometheus_client import Counter, Histogram, Gauge

# Request metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)

# Business metrics
analyses_total = Counter(
    'analyses_total',
    'Total analyses performed',
    ['status', 'language']
)

active_analyses = Gauge(
    'active_analyses',
    'Number of active analyses'
)

# Database metrics
db_connections = Gauge(
    'db_connections',
    'Number of database connections',
    ['pool', 'state']
)
```

**Health Checks**:
```python
from fastapi import APIRouter, status

router = APIRouter()

@router.get("/health")
async def health_check():
    """Basic health check"""
    return {"status": "healthy"}

@router.get("/health/ready")
async def readiness_check(db: Session = Depends(get_db)):
    """Readiness check (can serve traffic)"""
    checks = {
        "database": check_database(db),
        "redis": check_redis(),
        "neo4j": check_neo4j()
    }
    
    if all(checks.values()):
        return {"status": "ready", "checks": checks}
    else:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "not_ready", "checks": checks}
        )

@router.get("/health/live")
async def liveness_check():
    """Liveness check (process is alive)"""
    return {"status": "alive"}
```

**Alerting Rules**:
- Error rate > 5% for 5 minutes → Page on-call engineer
- Response time P95 > 2s for 10 minutes → Alert team
- Database connection pool > 90% for 5 minutes → Alert DBA
- Disk usage > 85% → Alert ops team
- Failed analyses > 20% for 15 minutes → Alert development team



# 14. Architecture Decision Records (ADR)

## ADR-001: Microservices Architecture

**Status**: Accepted

**Context**: Need to design system architecture that supports independent scaling, deployment, and development of different components.

**Decision**: Adopt microservices architecture with separate services for authentication, project management, code analysis, and architecture analysis.

**Rationale**:
- Independent scaling: Analysis workers can scale independently from API services
- Technology flexibility: Can use different tech stacks for different services
- Fault isolation: Failure in one service doesn't bring down entire system
- Team autonomy: Different teams can work on different services independently

**Consequences**:
- Positive: Better scalability, fault isolation, development velocity
- Negative: Increased operational complexity, need for service mesh, distributed tracing
- Mitigation: Use Kubernetes for orchestration, implement comprehensive monitoring

**Alternatives Considered**:
- Monolithic architecture: Simpler but doesn't scale well
- Modular monolith: Better than pure monolith but still single deployment unit



## ADR-002: Neo4j for Dependency Graphs

**Status**: Accepted

**Context**: Need to store and query complex dependency relationships between code entities for architectural analysis.

**Decision**: Use Neo4j graph database for storing code dependency graphs alongside PostgreSQL for transactional data.

**Rationale**:
- Native graph algorithms: Efficient circular dependency detection, shortest path
- Cypher query language: Expressive queries for graph traversal
- Performance: O(1) relationship traversal vs O(n) in relational databases
- Visualization: Built-in graph visualization tools

**Consequences**:
- Positive: Fast graph queries, natural data model for dependencies
- Negative: Additional database to manage, learning curve for Cypher
- Mitigation: Use managed Neo4j service, provide Cypher query templates

**Alternatives Considered**:
- PostgreSQL with recursive CTEs: Slower for deep traversals
- Graph library (NetworkX): In-memory only, doesn't persist
- Amazon Neptune: Vendor lock-in, less mature than Neo4j



## ADR-003: Multiple LLM Provider Support

**Status**: Accepted

**Context**: Need reliable AI-powered code analysis with fallback options for availability and cost optimization.

**Decision**: Support multiple LLM providers (OpenAI GPT-4, Anthropic Claude 3.5, Azure OpenAI) with automatic fallback.

**Rationale**:
- Availability: If one provider is down, fallback to another
- Cost optimization: Use cheaper models for simpler analyses
- Quality: Different models excel at different tasks
- Compliance: Azure OpenAI for enterprise customers requiring data residency

**Consequences**:
- Positive: Higher availability, cost flexibility, better quality
- Negative: More complex integration, need to normalize responses
- Mitigation: Abstract LLM client interface, standardize prompt templates

**Alternatives Considered**:
- Single provider (OpenAI only): Simpler but single point of failure
- Self-hosted models: Lower cost but requires ML infrastructure



## ADR-004: JWT for Authentication

**Status**: Accepted

**Context**: Need stateless authentication mechanism that scales horizontally across multiple service instances.

**Decision**: Use JWT (JSON Web Tokens) for authentication with 24-hour expiry and refresh token mechanism.

**Rationale**:
- Stateless: No server-side session storage required
- Scalable: Works across multiple service instances without shared state
- Standard: Industry-standard protocol with wide library support
- Portable: Can be used across different services and platforms

**Consequences**:
- Positive: Horizontal scalability, no session database required
- Negative: Cannot revoke tokens before expiry (without blacklist)
- Mitigation: Short expiry time (24h), token blacklist in Redis for revocation

**Alternatives Considered**:
- Session-based auth: Requires shared session store, doesn't scale well
- OAuth 2.0 only: More complex, overkill for internal authentication



## ADR-005: Five-Role RBAC System

**Status**: Accepted

**Context**: Need flexible access control that supports different user types from read-only visitors to full administrators.

**Decision**: Implement 5-role RBAC system: Admin, Manager, Reviewer, Programmer, Visitor.

**Rationale**:
- Granular control: Different permission levels for different user types
- Enterprise-ready: Supports organizational hierarchies
- Principle of least privilege: Users get only necessary permissions
- Audit compliance: Clear role assignments for compliance reporting

**Consequences**:
- Positive: Flexible access control, audit trail, compliance-ready
- Negative: More complex than simple admin/user model
- Mitigation: Clear documentation, role assignment UI, permission matrix

**Alternatives Considered**:
- Two-role system (admin/user): Too simple for enterprise needs
- Attribute-based access control (ABAC): Too complex for current requirements



## ADR-006: Celery for Asynchronous Task Processing

**Status**: Accepted

**Context**: Need to process long-running code analysis tasks asynchronously without blocking API requests.

**Decision**: Use Celery with Redis as message broker for asynchronous task queue.

**Rationale**:
- Mature ecosystem: Battle-tested in production environments
- Python native: Integrates seamlessly with FastAPI backend
- Flexible: Supports task priorities, retries, scheduling
- Scalable: Can add workers dynamically based on queue depth

**Consequences**:
- Positive: Non-blocking API, horizontal scaling, task monitoring
- Negative: Additional infrastructure (Redis), complexity in debugging
- Mitigation: Comprehensive logging, task monitoring dashboard, retry logic

**Alternatives Considered**:
- AWS SQS + Lambda: Vendor lock-in, cold start latency
- RabbitMQ: More complex setup than Redis
- Background threads: Doesn't scale across multiple instances



## ADR-007: PostgreSQL for Transactional Data

**Status**: Accepted

**Context**: Need reliable, ACID-compliant database for user accounts, projects, and analysis results.

**Decision**: Use PostgreSQL 13+ as primary relational database for all transactional data.

**Rationale**:
- ACID compliance: Strong consistency guarantees for critical data
- JSON support: JSONB for flexible schema (analysis details, audit logs)
- Mature ecosystem: Extensive tooling, monitoring, backup solutions
- Performance: Excellent query performance with proper indexing
- Open source: No vendor lock-in, community support

**Consequences**:
- Positive: Data integrity, rich feature set, proven reliability
- Negative: Vertical scaling limits (mitigated by read replicas)
- Mitigation: Connection pooling, read replicas, query optimization

**Alternatives Considered**:
- MySQL: Less feature-rich, weaker JSON support
- MongoDB: No ACID guarantees, eventual consistency issues
- Amazon Aurora: Vendor lock-in, higher cost

