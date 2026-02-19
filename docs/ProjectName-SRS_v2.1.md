---
title: Software Requirements Specification
project: AI-Based Code Reviewer
version: 2.1
date: 2026-02-16
authors: [BaiXuan Zhang]
reviewers: [Dr. Siraprapa]
status: In Review
last_updated: 2026-02-16
---

# AI-Based Reviewer on Project Code and Architecture
## Software Requirement Specification (SRS)

**Version:** v2.1  
**Date:** 2026-02-16

## Document History

| Version | Date | Author | Reviewer | Changes |
|---------|------|--------|----------|---------|
| v1.0 | 2026-02-07 | BaiXuan Zhang | Dr. Siraprapa | Initial draft |
| v2.0 | 2026-02-13 | BaiXuan Zhang | Dr. Siraprapa | Complete revision with proposal alignment, added use cases |
| v2.1 | 2026-02-16 | BaiXuan Zhang | Dr. Siraprapa | Added NFR, completed all use cases, added RTM, API specs |

---

# Table of Contents

1. [Introduction](#1-introduction)
2. [Overall Description](#2-overall-description)
3. [User Requirements Specification (URS)](#3-user-requirements-specification)
4. [Functional Requirements (SRS)](#4-functional-requirements)
5. [Non-Functional Requirements (NFR)](#5-non-functional-requirements)
6. [Use Cases](#6-use-cases)
7. [API Specifications](#7-api-specifications)
8. [Data Validation Rules](#8-data-validation-rules)
9. [Requirements Traceability Matrix](#9-requirements-traceability-matrix)

---

# 1. Introduction

## 1.1 Purpose

This Software Requirement Specification (SRS) document defines the functional and non-functional requirements for the "AI-Based Project Code and Architecture Review Platform". It serves as the authoritative reference for the system's design, development, and validation, ensuring the platform meets the needs of automated code and architecture review workflows.

## 1.2 Scope

This SRS covers all core requirements of the platform, including:


**Core Functionality:** Automatic review of GitHub code repositories by integrating Abstract Syntax Trees (AST), Dependency Graphs, and Large Language Models (LLMs) to analyze code quality and architectural compliance.

**User Requirements:** Support for real-time feedback during code submission, automated detection of architectural deviations, and visual dashboards for project quality monitoring.

### Key Features Description

#### Feature #1: Code Review - Automated quality control for pull requests with LLM code analysis
**Description:** Automated code quality assessment via LLM integration. System analyzes pull request code using AST parsing and LLM deep learning models to identify syntax errors, static semantic errors (such as type mismatch), and compilation errors. Provides instant inline comments with severity ratings so developers can understand issues directly in their PR workflow.

**Priority:** Must Have

#### Feature #2: Graph-based Architecture Analysis - Real-time monitoring of architectural drift using Neo4j
**Description:** Real-time architectural monitoring through Neo4j graph database integration. System continuously tracks dependency relationships, detects architectural drift patterns, identifies circular dependencies, and validates structural compliance against defined architecture standards. Dashboard visualization shows architecture health metrics in real-time for team visibility.

**Priority:** Must Have

#### Feature #3: Authenticated System - Role-based access control (RBAC) for enterprise security
**Description:** Enterprise-grade security with JWT-based authentication and role-based access control. Ensures secure access control and audit compliance with comprehensive logging.

**Priority:** Must Have

#### Feature #4: Project Management - Lifecycle management of code analysis tasks
**Description:** Comprehensive repository and analysis task management. Provides dashboard for monitoring analysis queue, project health, and quality metrics over time.

**Priority:** Should Have

## 1.3 Acronyms and Definitions

### 1.3.1 Acronyms

| Acronym | Definition |
|---------|------------|
| **API** | Application Programming Interface |
| **AST** | Abstract Syntax Tree - A tree representation of the abstract syntactic structure of source code |
| **CFG** | Control Flow Graph - A representation of all paths that might be traversed through a program during execution |
| **CI/CD** | Continuous Integration/Continuous Deployment |
| **GDPR** | General Data Protection Regulation |
| **HIPAA** | Health Insurance Portability and Accountability Act |
| **JWT** | JSON Web Token - Compact, URL-safe means of representing claims between two parties |
| **LLM** | Large Language Model - AI system trained on vast text data for understanding and generating text |
| **LOC** | Lines of Code |
| **MTTR** | Mean Time To Resolution |
| **NFR** | Non-Functional Requirement |
| **OWASP** | Open Web Application Security Project |
| **PR** | Pull Request - Proposed code change submitted for review before merging |
| **RBAC** | Role-Based Access Control - Access control paradigm where permissions associate with roles |
| **REST** | Representational State Transfer |
| **RTM** | Requirements Traceability Matrix |
| **SDLC** | Software Development Life Cycle |
| **SOC 2** | Service Organization Control 2 - Auditing standard for service organizations' security |
| **SRS** | Software Requirements Specification |
| **TLS** | Transport Layer Security |
| **URS** | User Requirements Specification |


### 1.3.2 Definitions

| Term | Definition |
|------|------------|
| **Architectural Drift** | Progressive deviation of a software system's actual structure from its intended design, typically accumulating through small incremental changes that individually appear harmless but collectively compromise architectural integrity. |
| **Agentic AI** | Artificial intelligence system capable of autonomous reasoning, decision-making, and action execution within defined parameters, characterized by goal-directed behavior and contextual adaptation. |
| **Baseline Configuration** | Formally reviewed and agreed-upon specification serving as the basis for further development, changeable only through formal change control. In this system, architectural baselines define expected structural patterns against which drift is measured. |
| **Coupling Anomaly** | Unauthorized or unexpected dependency relationship between software modules that violates architectural constraints, potentially compromising modularity, testability, or maintainability. |
| **Cyclic Dependency** | Circular reference pattern where Module A depends on Module B, which depends on Module C, which depends back on Module A, creating a dependency cycle that compromises system modularity and testing isolation. |
| **Dependency Graph** | Directed graph structure representing relationships between software components, where nodes represent modules/classes and edges represent dependencies (imports, function calls, inheritance). |
| **Explainable AI (XAI)** | AI techniques producing decisions, recommendations, or predictions accompanied by human-interpretable reasoning, enabling users to understand why the AI reached a particular conclusion. |
| **Graph Database** | Database management system using graph structures with nodes, edges, and properties to represent and store data, optimized for querying relationships and traversing connected data patterns. |
| **Layer Violation** | Architectural anti-pattern where code in one tier bypasses the immediately adjacent tier to access functionality in a non-adjacent tier, compromising separation of concerns (e.g., presentation layer directly accessing data layer). |
| **Quality Gate** | Automated checkpoint in the development pipeline validating code against predefined quality criteria (test coverage, complexity metrics, security vulnerabilities) and blocking deployment if thresholds are not met. |
| **Static Analysis** | Automated examination of source code without executing the program, identifying potential defects, security vulnerabilities, code smells, and compliance violations through pattern matching and rule-based evaluation. |
| **Technical Debt** | Implied cost of future refactoring work caused by choosing quick/easy solutions now instead of better approaches that would take longer, accumulating maintenance burden over time. |
| **Webhook** | HTTP callback mechanism enabling real-time event notifications from one system to another, where the receiving system provides an endpoint URL that the sending system calls when specified events occur. |

---

# 2. Overall Description

## 2.1 Product Perspective

The AI-Based Reviewer platform is a web-based application accessible from any device supporting a modern web browser. The system integrates with GitHub repositories through webhooks and provides automated code review and architectural analysis capabilities.

### System Environment

#### Frontend Layer
React/Next.js-based progressive web application delivering responsive, server-side rendered user interfaces. Provides interactive dashboards with real-time updates via WebSocket connections, supporting both desktop and mobile browser access. Implements component-based architecture with Tailwind CSS for consistent visual design.

#### Backend API Layer
FastAPI-powered RESTful services providing asynchronous request processing with automatic OpenAPI documentation. Orchestrates business logic including user authentication (JWT-based), repository management, analysis task scheduling, and result aggregation. Implements horizontal scaling through stateless microservices architecture.

#### Data Persistence Layer
Hybrid database architecture combining Neo4j graph database for relationship-intensive architectural data (AST nodes, dependency edges, call graphs) with PostgreSQL for transactional relational data (user accounts, audit logs). Redis in-memory store provides caching and message queue functionality for asynchronous task processing via Celery workers.

#### AI Reasoning Layer
Integration with multiple Large Language Model APIs (GPT-4, Claude 3.5 Sonnet) providing contextual code analysis, architectural reasoning, and natural language suggestion generation. Implements fallback mechanisms and rate limiting. Enriches LLM prompts with structural context from graph database, enabling architectural impact analysis.

#### Integration Layer
GitHub webhook receivers for real-time PR event notifications with automated comment posting via GitHub REST API. OAuth 2.0 authentication flow for repository access authorization. Supports webhook signature verification for security.


## 2.2 User Characteristics

| Role | Access Level | Definition | Responsibilities |
|------|--------------|------------|------------------|
| **Administrator** | Full system access | System-level configuration and management | User account management, system configuration, compliance settings, platform health monitoring, integration setup, security policy enforcement |
| **Pull Request Reviewer** | Read/Write analysis access | Code review and quality assurance | Code review execution, AI suggestion acceptance/rejection, architectural compliance validation, feedback provision to developers |
| **Programmer** | Read-only analysis, Write own code | Software developer submitting code | Code submission, PR creation, AI feedback interpretation, suggested fix implementation, code quality improvement |
| **Manager** | Read-only comprehensive | Project oversight and reporting | Dashboard monitoring, report generation, quality metrics review, team performance analysis, compliance oversight, strategic planning |
| **Guest** | Limited public access | Unauthenticated visitor | Platform information viewing, documentation access (no code or analysis access) |

## 2.3 Constraints

### Technical Constraints
- Must integrate with GitHub API v3 and webhooks
- Must support Python, JavaScript, TypeScript, Java, and Go for code analysis
- Must operate within LLM API rate limits (GPT-4: 10,000 tokens/min, Claude: 100,000 tokens/min)
- Must support modern browsers (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+)

### Regulatory Constraints
- Must comply with GDPR for EU user data
- Must comply with SOC 2 Type II for enterprise customers
- Must implement OWASP Top 10 security controls
- Must maintain audit logs for 7 years for compliance

### Business Constraints
- Initial release must support up to 100 concurrent users
- Analysis must complete within 2 minutes for repositories < 50K LOC
- System must achieve 99.5% uptime SLA
- Must support English language interface (internationalization in future releases)

---

# 3. User Requirements Specification (URS)

| ID | Priority | User Story | Acceptance Criteria |
|----|----------|------------|---------------------|
| **URS-01** | Must Have | As a Guest, I want to register by providing username, email, and password, so that I can access the platform | - Registration form validates input in real-time<br>- System sends confirmation email<br>- Account is created with default "User" role<br>- User is redirected to login page |
| **URS-02** | Must Have | As a User, I want to login using valid credentials, so that I can access my projects | - System validates credentials<br>- JWT token is generated with 24-hour expiry<br>- User is redirected to dashboard<br>- Failed attempts are logged |
| **URS-03** | Must Have | As a User, I want to add GitHub repository by providing repository URL, so that it can be analyzed | - System validates GitHub URL format<br>- OAuth authorization flow is initiated<br>- Webhook is configured automatically<br>- Repository appears in project list |
| **URS-04** | Must Have | As a Programmer, I want to receive automated code review feedback when pull request is submitted, so that I can improve code quality | - Analysis starts within 30 seconds of PR creation<br>- Comments are posted to GitHub PR<br>- Issues are categorized by severity<br>- Suggestions are actionable |
| **URS-05** | Should Have | As a Reviewer, I want to view interactive dependency graphs and architecture evolution, so that I can understand system structure | - Graph renders within 5 seconds<br>- Supports zoom, pan, and filter<br>- Shows circular dependencies highlighted<br>- Displays historical changes |
| **URS-06** | Should Have | As a Manager, I want to view code quality metrics dashboard with exportable reports, so that I can track team performance | - Dashboard loads within 3 seconds<br>- Shows trends over time<br>- Supports PDF/CSV export<br>- Includes quality score, issue counts, technical debt |
| **URS-07** | Must Have | As an Administrator, I want to configure analysis settings and compliance standards, so that I can customize platform behavior | - Settings are saved immediately<br>- Changes apply to new analyses<br>- Supports ISO/IEC 25010, Google Style Guide<br>- Audit log records all changes |

---

# 4. Functional Requirements (SRS)


## 4.1 Authentication and Authorization

| ID | Priority | Requirement | Acceptance Criteria |
|----|----------|-------------|---------------------|
| **SRS-001** | Must Have | System shall authenticate users using JWT tokens with bcrypt password hashing | - JWT tokens expire after 24 hours<br>- Refresh tokens valid for 7 days<br>- Password hash uses bcrypt with cost factor 12<br>- Tokens include user ID, role, and expiry |
| **SRS-002** | Must Have | System shall implement role-based access control (RBAC) with 5 roles | - Permissions enforced at API level<br>- Role hierarchy: Guest < User < Programmer < Reviewer < Manager < Admin<br>- Unauthorized access returns HTTP 403<br>- All access attempts logged |
| **SRS-003** | Must Have | System shall support OAuth 2.0 for GitHub integration | - Authorization code flow implemented<br>- Tokens stored encrypted<br>- Supports token refresh<br>- Revocation supported |

## 4.2 Repository Management

| ID | Priority | Requirement | Acceptance Criteria |
|----|----------|-------------|---------------------|
| **SRS-004** | Must Have | System shall configure GitHub webhooks for pull request events | - Webhook URL: `/api/webhooks/github`<br>- Events: PR opened, synchronized, closed<br>- Signature verification using HMAC-SHA256<br>- Retry failed deliveries up to 3 times |
| **SRS-005** | Must Have | System shall validate GitHub repository URLs before adding | - Format: `https://github.com/{owner}/{repo}`<br>- Checks repository exists via API<br>- Verifies user has admin access<br>- Prevents duplicate additions |
| **SRS-006** | Should Have | System shall support repository synchronization | - Fetches latest commits<br>- Updates branch information<br>- Syncs PR list<br>- Runs on-demand or scheduled |

## 4.3 Code Analysis

| ID | Priority | Requirement | Acceptance Criteria |
|----|----------|-------------|---------------------|
| **SRS-007** | Must Have | System shall parse source code to generate AST and extract dependencies | - Supports Python, JavaScript, TypeScript, Java, Go<br>- Extracts imports, function calls, class inheritance<br>- Handles syntax errors gracefully<br>- Generates AST within 2 seconds per file |
| **SRS-008** | Must Have | System shall integrate with LLM API (GPT-4/Claude 3.5) for code analysis | - Sends code with architectural context<br>- Implements rate limiting (10 req/min)<br>- Fallback to secondary model on failure<br>- Timeout after 30 seconds |
| **SRS-009** | Must Have | System shall categorize issues by severity (Critical, High, Medium, Low) | - Critical: Security vulnerabilities, data loss risks<br>- High: Logic errors, performance issues<br>- Medium: Code smells, maintainability<br>- Low: Style violations, minor improvements |
| **SRS-010** | Must Have | System shall post review comments to GitHub PR via API | - Comments include file path, line number, description<br>- Grouped by severity<br>- Includes suggested fixes<br>- Posted within 1 minute of analysis completion |
| **SRS-011** | Should Have | System shall capture user feedback (Accept/Dismiss) on review comments | - Feedback stored in database<br>- Used for model refinement<br>- Aggregated in analytics dashboard<br>- Supports bulk actions |

## 4.4 Architecture Analysis

| ID | Priority | Requirement | Acceptance Criteria |
|----|----------|-------------|---------------------|
| **SRS-012** | Must Have | System shall store dependency graphs in Neo4j database | - Nodes: Modules, Classes, Functions<br>- Relationships: DEPENDS_ON, CALLS, INHERITS<br>- Properties: name, path, complexity, timestamp<br>- Indexed by project_id and entity_name |
| **SRS-013** | Must Have | System shall detect architectural drift by identifying cyclic dependencies, coupling anomalies, and layer violations | - Cyclic dependencies detected using graph algorithms<br>- Coupling measured by dependency count<br>- Layer violations checked against defined architecture<br>- Results stored with severity rating |
| **SRS-014** | Should Have | System shall render interactive dependency graphs using D3.js | - Supports zoom (0.1x to 10x)<br>- Pan with mouse drag<br>- Filter by entity type, severity<br>- Export as PNG/SVG<br>- Loads within 5 seconds for graphs < 1000 nodes |

## 4.5 Compliance Verification

| ID | Priority | Requirement | Acceptance Criteria |
|----|----------|-------------|---------------------|
| **SRS-015** | Must Have | System shall verify compliance with ISO/IEC 25010 quality model | - Checks: Functionality, Reliability, Usability, Efficiency, Maintainability, Portability<br>- Generates compliance report<br>- Highlights violations<br>- Provides remediation guidance |
| **SRS-016** | Should Have | System shall verify compliance with ISO/IEC 23396 architectural standards | - Validates layered architecture<br>- Checks separation of concerns<br>- Verifies interface contracts<br>- Reports architectural anti-patterns |
| **SRS-017** | Should Have | System shall verify compliance with Google Style Guides | - Language-specific rules (Python PEP 8, JavaScript Standard)<br>- Naming conventions<br>- Documentation requirements<br>- Configurable rule sets |

## 4.6 Performance and Scalability

| ID | Priority | Requirement | Acceptance Criteria |
|----|----------|-------------|---------------------|
| **SRS-018** | Must Have | System shall process small repositories (<10K LOC) in 8-12 seconds | - P50: 8 seconds<br>- P95: 12 seconds<br>- P99: 15 seconds<br>- Measured from webhook receipt to comment posting |
| **SRS-019** | Must Have | System shall use Redis for asynchronous task queuing | - Tasks queued immediately (< 100ms)<br>- FIFO processing order<br>- Failed tasks retry with exponential backoff<br>- Max 3 retry attempts |
| **SRS-020** | Should Have | System shall support horizontal scaling of analysis workers | - Stateless worker design<br>- Load balanced via Redis queue<br>- Auto-scaling based on queue depth<br>- Graceful shutdown on scale-down |

---

# 5. Non-Functional Requirements (NFR)


## 5.1 Performance Requirements

| ID | Category | Requirement | Target | Measurement Method |
|----|----------|-------------|--------|-------------------|
| **NFR-001** | Response Time | API endpoints shall respond within acceptable time limits | - GET requests: < 500ms (P95)<br>- POST requests: < 1s (P95)<br>- Analysis tasks: < 2min for <50K LOC | Application Performance Monitoring (APM) |
| **NFR-002** | Throughput | System shall handle concurrent analysis requests | - 10 concurrent analyses<br>- 100 concurrent API requests<br>- 1000 concurrent dashboard users | Load testing with JMeter |
| **NFR-003** | Scalability | System shall scale horizontally to handle increased load | - Add workers without downtime<br>- Linear performance scaling up to 50 workers<br>- Auto-scale based on queue depth > 20 | Kubernetes HPA metrics |
| **NFR-004** | Resource Usage | Analysis workers shall operate within resource limits | - CPU: < 2 cores per worker<br>- Memory: < 4GB per worker<br>- Disk I/O: < 100 MB/s | Container resource monitoring |

## 5.2 Security Requirements

| ID | Category | Requirement | Implementation | Verification |
|----|----------|-------------|----------------|--------------|
| **NFR-005** | Authentication | System shall enforce strong password policies | - Min 8 characters<br>- Uppercase, lowercase, number, special char<br>- Password history (last 5)<br>- Account lockout after 5 failed attempts | Automated security tests |
| **NFR-006** | Authorization | System shall implement least privilege access control | - Role-based permissions<br>- Resource-level access control<br>- API endpoint authorization<br>- Audit all access attempts | Penetration testing |
| **NFR-007** | Data Encryption | System shall encrypt sensitive data at rest and in transit | - TLS 1.3 for all connections<br>- AES-256 for database encryption<br>- Encrypted environment variables<br>- Secure key management (AWS KMS) | Security audit |
| **NFR-008** | Input Validation | System shall validate and sanitize all user inputs | - SQL injection prevention<br>- XSS protection<br>- CSRF tokens<br>- Rate limiting (100 req/min per user) | OWASP ZAP scanning |
| **NFR-009** | Audit Logging | System shall log all security-relevant events | - Authentication attempts<br>- Authorization failures<br>- Data modifications<br>- Configuration changes<br>- Retention: 7 years | Log analysis tools |
| **NFR-010** | Vulnerability Management | System shall be scanned for vulnerabilities regularly | - Weekly dependency scans<br>- Monthly penetration tests<br>- Automated CVE monitoring<br>- Patch within 30 days of disclosure | Snyk, OWASP Dependency-Check |

## 5.3 Availability and Reliability

| ID | Category | Requirement | Target | Measurement |
|----|----------|-------------|--------|-------------|
| **NFR-011** | Uptime | System shall maintain high availability | - 99.5% uptime (43.8 hours downtime/year)<br>- Planned maintenance windows: 4 hours/month<br>- Unplanned downtime: < 2 hours/month | Uptime monitoring (Pingdom) |
| **NFR-012** | Fault Tolerance | System shall handle component failures gracefully | - Database failover: < 30 seconds<br>- Service restart: < 10 seconds<br>- No data loss on failure<br>- Automatic retry for transient errors | Chaos engineering tests |
| **NFR-013** | Backup and Recovery | System shall backup data regularly | - Database backups: Daily full, hourly incremental<br>- Retention: 30 days<br>- Recovery Time Objective (RTO): 4 hours<br>- Recovery Point Objective (RPO): 1 hour | Disaster recovery drills |
| **NFR-014** | Error Handling | System shall handle errors gracefully | - User-friendly error messages<br>- Detailed logs for debugging<br>- Automatic error reporting<br>- Graceful degradation | Error tracking (Sentry) |

## 5.4 Usability Requirements

| ID | Category | Requirement | Criteria | Validation |
|----|----------|-------------|----------|------------|
| **NFR-015** | User Interface | System shall provide intuitive user interface | - Consistent design language<br>- Responsive layout (mobile, tablet, desktop)<br>- Accessibility (WCAG 2.1 Level AA)<br>- Loading indicators for async operations | Usability testing |
| **NFR-016** | Documentation | System shall provide comprehensive documentation | - User guide<br>- API documentation (OpenAPI)<br>- Administrator manual<br>- Inline help and tooltips | Documentation review |
| **NFR-017** | Learnability | New users shall be productive within 30 minutes | - Onboarding tutorial<br>- Sample projects<br>- Video tutorials<br>- Context-sensitive help | User testing |
| **NFR-018** | Error Messages | System shall provide clear, actionable error messages | - Plain language (no technical jargon)<br>- Specific problem description<br>- Suggested resolution steps<br>- Link to documentation | User feedback |

## 5.5 Maintainability Requirements

| ID | Category | Requirement | Implementation | Verification |
|----|----------|-------------|----------------|--------------|
| **NFR-019** | Code Quality | Codebase shall maintain high quality standards | - Test coverage: > 80%<br>- Code complexity: < 10 cyclomatic complexity<br>- Documentation: All public APIs<br>- Linting: Zero warnings | CI/CD quality gates |
| **NFR-020** | Modularity | System shall be modular and loosely coupled | - Microservices architecture<br>- Clear service boundaries<br>- API-based communication<br>- Independent deployment | Architecture review |
| **NFR-021** | Monitoring | System shall provide comprehensive monitoring | - Application metrics (Prometheus)<br>- Log aggregation (ELK)<br>- Distributed tracing (Jaeger)<br>- Alerting (PagerDuty) | Monitoring dashboard |
| **NFR-022** | Deployment | System shall support automated deployment | - CI/CD pipeline (GitHub Actions)<br>- Infrastructure as Code (Terraform)<br>- Blue-green deployment<br>- Rollback capability | Deployment tests |

## 5.6 Compatibility Requirements

| ID | Category | Requirement | Supported Versions | Testing |
|----|----------|-------------|-------------------|---------|
| **NFR-023** | Browser Compatibility | System shall support modern web browsers | - Chrome 90+<br>- Firefox 88+<br>- Safari 14+<br>- Edge 90+ | Cross-browser testing |
| **NFR-024** | Programming Languages | System shall analyze multiple programming languages | - Python 3.8+<br>- JavaScript ES6+<br>- TypeScript 4.0+<br>- Java 11+<br>- Go 1.16+ | Language-specific tests |
| **NFR-025** | Integration | System shall integrate with external services | - GitHub API v3<br>- OpenAI API v1<br>- Anthropic API v1<br>- Neo4j 4.4+<br>- PostgreSQL 13+ | Integration tests |

## 5.7 Compliance Requirements

| ID | Category | Requirement | Standard | Audit Frequency |
|----|----------|-------------|----------|-----------------|
| **NFR-026** | Data Privacy | System shall comply with data protection regulations | - GDPR (EU)<br>- CCPA (California)<br>- Data retention policies<br>- Right to deletion | Annual |
| **NFR-027** | Security Standards | System shall comply with security standards | - SOC 2 Type II<br>- OWASP Top 10<br>- CWE Top 25<br>- ISO 27001 | Bi-annual |
| **NFR-028** | Accessibility | System shall comply with accessibility standards | - WCAG 2.1 Level AA<br>- Section 508<br>- Keyboard navigation<br>- Screen reader support | Quarterly |

---

# 6. Use Cases

## 6.1 Use Case Diagram

See: `docs/diagram/use-case-diagram.puml`


## 6.2 Detailed Use Case Descriptions

For complete use case descriptions including normal flows, alternative flows, exception flows, and business rules, see: **[SRS-UseCases-Detailed.md](./SRS-UseCases-Detailed.md)**

Summary of use cases:
- **UC-01:** User Registration
- **UC-02:** User Login
- **UC-03:** Add GitHub Repository
- **UC-04:** Automated Pull Request Review
- **UC-05:** View Interactive Dependency Graph
- **UC-06:** View Quality Metrics Dashboard
- **UC-07:** Configure Analysis Settings

---

# 7. API Specifications

## 7.1 Authentication Endpoints

### POST /api/auth/register
**Description:** Register a new user account

**Request Body:**
```json
{
  "username": "string (3-30 chars, alphanumeric + underscore)",
  "email": "string (valid email format)",
  "password": "string (min 8 chars, complexity requirements)"
}
```

**Response 201 Created:**
```json
{
  "success": true,
  "message": "Registration successful. Please verify your email.",
  "data": {
    "user_id": "uuid",
    "username": "string",
    "email": "string",
    "role": "user",
    "created_at": "ISO 8601 timestamp"
  }
}
```

**Error Responses:**
- **400 Bad Request:** Invalid input format
```json
{
  "success": false,
  "error": "VALIDATION_ERROR",
  "message": "Password must contain uppercase, lowercase, number, and special character",
  "field": "password"
}
```
- **409 Conflict:** Username or email already exists
```json
{
  "success": false,
  "error": "DUPLICATE_USER",
  "message": "Email already registered"
}
```

---

### POST /api/auth/login
**Description:** Authenticate user and receive JWT tokens

**Request Body:**
```json
{
  "email": "string (email or username)",
  "password": "string"
}
```

**Response 200 OK:**
```json
{
  "success": true,
  "data": {
    "access_token": "string (JWT, 24h expiry)",
    "refresh_token": "string (JWT, 7d expiry)",
    "user": {
      "id": "uuid",
      "username": "string",
      "email": "string",
      "role": "string"
    }
  }
}
```

**Error Responses:**
- **401 Unauthorized:** Invalid credentials
- **403 Forbidden:** Account locked or unverified
- **429 Too Many Requests:** Rate limit exceeded

---

### POST /api/auth/refresh
**Description:** Refresh access token using refresh token

**Request Body:**
```json
{
  "refresh_token": "string"
}
```

**Response 200 OK:**
```json
{
  "success": true,
  "data": {
    "access_token": "string (new JWT, 24h expiry)"
  }
}
```

---

## 7.2 Repository Management Endpoints

### POST /api/repositories
**Description:** Add a new GitHub repository for analysis

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "github_url": "string (https://github.com/{owner}/{repo})",
  "default_branch": "string (optional, default: main)",
  "config": {
    "enabled_rules": ["security", "performance", "style"],
    "severity_threshold": "medium",
    "auto_merge_on_pass": false
  }
}
```

**Response 201 Created:**
```json
{
  "success": true,
  "data": {
    "project_id": "uuid",
    "name": "string",
    "github_url": "string",
    "default_branch": "string",
    "webhook_configured": true,
    "initial_scan_status": "queued",
    "created_at": "ISO 8601 timestamp"
  }
}
```

**Error Responses:**
- **400 Bad Request:** Invalid GitHub URL
- **403 Forbidden:** Insufficient GitHub permissions
- **409 Conflict:** Repository already added

---

### GET /api/repositories
**Description:** List all repositories for authenticated user

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `page` (integer, default: 1)
- `limit` (integer, default: 20, max: 100)
- `status` (enum: active, inactive, all)

**Response 200 OK:**
```json
{
  "success": true,
  "data": {
    "repositories": [
      {
        "project_id": "uuid",
        "name": "string",
        "github_url": "string",
        "is_active": true,
        "last_analyzed": "ISO 8601 timestamp",
        "quality_score": 85.5,
        "total_issues": 12
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 45,
      "total_pages": 3
    }
  }
}
```

---

### GET /api/repositories/{project_id}
**Description:** Get detailed information about a specific repository

**Response 200 OK:**
```json
{
  "success": true,
  "data": {
    "project_id": "uuid",
    "name": "string",
    "github_url": "string",
    "default_branch": "string",
    "languages": ["Python", "JavaScript"],
    "is_active": true,
    "webhook_configured": true,
    "created_at": "ISO 8601 timestamp",
    "last_analyzed": "ISO 8601 timestamp",
    "metrics": {
      "quality_score": 85.5,
      "total_lines": 15000,
      "code_coverage": 78.5,
      "avg_complexity": 4.2,
      "technical_debt": 120
    },
    "recent_analyses": [
      {
        "analysis_id": "uuid",
        "pr_number": 42,
        "status": "completed",
        "total_issues": 5,
        "completed_at": "ISO 8601 timestamp"
      }
    ]
  }
}
```

---

## 7.3 Analysis Endpoints

### GET /api/analyses/{analysis_id}
**Description:** Get detailed analysis results

**Response 200 OK:**
```json
{
  "success": true,
  "data": {
    "analysis_id": "uuid",
    "pr_id": "uuid",
    "pr_number": 42,
    "status": "completed",
    "started_at": "ISO 8601 timestamp",
    "completed_at": "ISO 8601 timestamp",
    "processing_time": 45,
    "summary": {
      "total_issues": 12,
      "critical": 1,
      "high": 3,
      "medium": 5,
      "low": 3
    },
    "issues": [
      {
        "issue_id": "uuid",
        "severity": "high",
        "category": "security",
        "title": "SQL Injection Vulnerability",
        "description": "User input is directly concatenated into SQL query",
        "file_path": "src/database.py",
        "line_number": 45,
        "suggestion": "Use parameterized queries or ORM",
        "code_snippet": "query = f\"SELECT * FROM users WHERE id = {user_id}\""
      }
    ],
    "compliance": [
      {
        "standard": "ISO/IEC 25010",
        "clause": "Security",
        "status": "fail",
        "details": "1 critical security vulnerability detected"
      }
    ]
  }
}
```

---

### POST /api/analyses/{analysis_id}/feedback
**Description:** Submit feedback on analysis results

**Request Body:**
```json
{
  "issue_id": "uuid",
  "action": "accept | dismiss | false_positive",
  "comment": "string (optional)"
}
```

**Response 200 OK:**
```json
{
  "success": true,
  "message": "Feedback recorded successfully"
}
```

---

## 7.4 Architecture Endpoints

### GET /api/architecture/{project_id}/graph
**Description:** Get dependency graph data for visualization

**Query Parameters:**
- `entity_type` (enum: file, class, function, all)
- `min_complexity` (integer, optional)
- `max_depth` (integer, default: 5)

**Response 200 OK:**
```json
{
  "success": true,
  "data": {
    "nodes": [
      {
        "id": "uuid",
        "type": "class",
        "name": "UserService",
        "file_path": "src/services/user.py",
        "complexity": 8,
        "lines": 150
      }
    ],
    "edges": [
      {
        "source": "uuid",
        "target": "uuid",
        "type": "depends_on",
        "weight": 5
      }
    ],
    "metrics": {
      "total_nodes": 45,
      "total_edges": 78,
      "circular_dependencies": 2,
      "avg_coupling": 3.5
    },
    "circular_dependencies": [
      {
        "cycle": ["ModuleA", "ModuleB", "ModuleC", "ModuleA"],
        "severity": "high"
      }
    ]
  }
}
```

---

## 7.5 Webhook Endpoints

### POST /api/webhooks/github
**Description:** Receive GitHub webhook events (internal use)

**Headers:**
```
X-GitHub-Event: pull_request
X-Hub-Signature-256: sha256=<signature>
```

**Request Body:** GitHub webhook payload (varies by event)

**Response 200 OK:**
```json
{
  "success": true,
  "message": "Webhook processed",
  "task_id": "uuid"
}
```

---

## 7.6 Metrics Endpoints

### GET /api/metrics/{project_id}
**Description:** Get quality metrics and trends

**Query Parameters:**
- `period` (enum: 7d, 30d, 90d, 1y)
- `metrics` (array: quality_score, issues, complexity, coverage)

**Response 200 OK:**
```json
{
  "success": true,
  "data": {
    "current": {
      "quality_score": 85.5,
      "total_issues": 12,
      "avg_complexity": 4.2,
      "code_coverage": 78.5
    },
    "trends": [
      {
        "date": "2026-02-01",
        "quality_score": 82.0,
        "total_issues": 18
      }
    ],
    "comparison": {
      "quality_score_change": "+3.5",
      "issues_change": "-6"
    }
  }
}
```

---

## 7.7 Error Response Format

All API errors follow this standard format:

```json
{
  "success": false,
  "error": "ERROR_CODE",
  "message": "Human-readable error message",
  "details": {
    "field": "specific_field",
    "constraint": "validation_rule"
  },
  "timestamp": "ISO 8601 timestamp",
  "request_id": "uuid"
}
```

### Common Error Codes
- `VALIDATION_ERROR`: Input validation failed
- `AUTHENTICATION_REQUIRED`: Missing or invalid authentication
- `AUTHORIZATION_FAILED`: Insufficient permissions
- `RESOURCE_NOT_FOUND`: Requested resource does not exist
- `DUPLICATE_RESOURCE`: Resource already exists
- `RATE_LIMIT_EXCEEDED`: Too many requests
- `EXTERNAL_SERVICE_ERROR`: Third-party service failure
- `INTERNAL_SERVER_ERROR`: Unexpected server error

---

# 8. Data Validation Rules


## 8.1 User Input Validation

| Field | Data Type | Validation Rules | Regex Pattern | Error Message |
|-------|-----------|------------------|---------------|---------------|
| Username | String | - Length: 3-30 characters<br>- Alphanumeric and underscore only<br>- Must start with letter<br>- Case-insensitive uniqueness | `^[a-zA-Z][a-zA-Z0-9_]{2,29}$` | "Username must be 3-30 characters, start with a letter, and contain only letters, numbers, and underscores" |
| Email | String | - Valid email format<br>- Max 100 characters<br>- Case-insensitive uniqueness<br>- No disposable email domains | `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$` | "Please enter a valid email address" |
| Password | String | - Min 8 characters<br>- Max 128 characters<br>- At least 1 uppercase<br>- At least 1 lowercase<br>- At least 1 number<br>- At least 1 special char (!@#$%^&*) | `^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,128}$` | "Password must be 8-128 characters with uppercase, lowercase, number, and special character" |
| GitHub URL | URL | - Format: https://github.com/{owner}/{repo}<br>- Owner: 1-39 chars, alphanumeric + hyphen<br>- Repo: 1-100 chars, alphanumeric + hyphen/underscore/dot | `^https://github\.com/[a-zA-Z0-9-]{1,39}/[a-zA-Z0-9._-]{1,100}$` | "Please enter a valid GitHub repository URL" |
| Project Name | String | - Length: 3-200 characters<br>- Alphanumeric, spaces, hyphens, underscores<br>- Trim whitespace | `^[a-zA-Z0-9 _-]{3,200}$` | "Project name must be 3-200 characters" |

## 8.2 Business Logic Validation

| Rule ID | Validation Rule | Implementation | Error Handling |
|---------|-----------------|----------------|----------------|
| **BV-01** | Email must be unique across all users | Database unique constraint + application-level check | Return 409 Conflict with message "Email already registered" |
| **BV-02** | Username must be unique (case-insensitive) | Database unique index (lowercase) + application check | Return 409 Conflict with message "Username already taken" |
| **BV-03** | Repository URL must be unique per platform instance | Database unique constraint on github_url | Return 409 Conflict with message "Repository already connected" |
| **BV-04** | User must have GitHub admin access to add repository | GitHub API permission check before webhook creation | Return 403 Forbidden with message "Admin access required" |
| **BV-05** | Analysis cannot be triggered for closed PRs | Check PR status before queuing analysis | Return 400 Bad Request with message "Cannot analyze closed PR" |
| **BV-06** | JWT token must not be expired | Check exp claim in token | Return 401 Unauthorized with message "Token expired" |
| **BV-07** | User role must have required permission for action | RBAC permission matrix check | Return 403 Forbidden with message "Insufficient permissions" |
| **BV-08** | File size must not exceed 10MB for analysis | Check file size before parsing | Skip file with warning "File too large for analysis" |
| **BV-09** | Analysis queue must not exceed 1000 pending tasks | Check queue depth before adding task | Return 429 Too Many Requests with message "Analysis queue full" |
| **BV-10** | Webhook signature must be valid | HMAC-SHA256 verification | Return 401 Unauthorized with message "Invalid webhook signature" |

## 8.3 Data Sanitization Rules

| Input Type | Sanitization Method | Purpose |
|------------|---------------------|---------|
| User-generated text (comments, descriptions) | HTML entity encoding, strip script tags | Prevent XSS attacks |
| SQL query parameters | Parameterized queries, ORM escaping | Prevent SQL injection |
| File paths | Path normalization, directory traversal prevention | Prevent path traversal attacks |
| GitHub URLs | URL parsing and validation, whitelist domain | Prevent SSRF attacks |
| JSON payloads | Schema validation, type checking | Prevent injection and type confusion |
| Code snippets | Syntax highlighting escaping, no execution | Safe display of code |

---

# 9. Requirements Traceability Matrix (RTM)

## 9.1 URS to SRS Mapping

| URS ID | URS Description | Related SRS | Related NFR | Use Case | Priority |
|--------|-----------------|-------------|-------------|----------|----------|
| URS-01 | Guest registration | SRS-001, SRS-002 | NFR-005, NFR-008 | UC-01 | Must Have |
| URS-02 | User login | SRS-001, SRS-002 | NFR-005, NFR-009 | UC-02 | Must Have |
| URS-03 | Add GitHub repository | SRS-004, SRS-005, SRS-006 | NFR-006, NFR-007 | UC-03 | Must Have |
| URS-04 | Automated PR review | SRS-007, SRS-008, SRS-009, SRS-010, SRS-018, SRS-019 | NFR-001, NFR-002, NFR-014 | UC-04 | Must Have |
| URS-05 | View dependency graph | SRS-012, SRS-013, SRS-014 | NFR-001, NFR-015 | UC-05 | Should Have |
| URS-06 | View quality dashboard | SRS-015, SRS-016, SRS-017 | NFR-001, NFR-015, NFR-016 | UC-06 | Should Have |
| URS-07 | Configure settings | SRS-003, SRS-015, SRS-016, SRS-017 | NFR-006, NFR-009, NFR-022 | UC-07 | Must Have |

## 9.2 SRS to Design Components Mapping

| SRS ID | Requirement | Design Component | Database Tables | API Endpoints | Test Cases |
|--------|-------------|------------------|-----------------|---------------|------------|
| SRS-001 | JWT authentication | AuthService, JWTManager | users, sessions | POST /api/auth/login, /api/auth/refresh | TC-AUTH-001 to TC-AUTH-005 |
| SRS-002 | RBAC | AuthorizationMiddleware, PermissionChecker | users, roles, permissions | All protected endpoints | TC-RBAC-001 to TC-RBAC-010 |
| SRS-003 | OAuth 2.0 | GitHubOAuthService | oauth_tokens | POST /api/auth/github | TC-OAUTH-001 to TC-OAUTH-003 |
| SRS-004 | GitHub webhooks | WebhookHandler, SignatureVerifier | projects, webhooks | POST /api/webhooks/github | TC-WEBHOOK-001 to TC-WEBHOOK-005 |
| SRS-007 | AST parsing | ASTParser, DependencyExtractor | code_entities, dependencies (Neo4j) | N/A (internal) | TC-PARSE-001 to TC-PARSE-010 |
| SRS-008 | LLM integration | LLMClient, PromptBuilder | analysis_results, issues | N/A (internal) | TC-LLM-001 to TC-LLM-008 |
| SRS-009 | Issue categorization | IssueCategorizer, SeverityClassifier | issues | GET /api/analyses/{id} | TC-ISSUE-001 to TC-ISSUE-005 |
| SRS-010 | GitHub comments | GitHubCommentPoster | comments | N/A (external API) | TC-COMMENT-001 to TC-COMMENT-003 |
| SRS-012 | Neo4j storage | Neo4jClient, GraphRepository | N/A (graph database) | GET /api/architecture/{id}/graph | TC-GRAPH-001 to TC-GRAPH-007 |
| SRS-013 | Drift detection | ArchitectureDriftDetector, CycleDetector | architectural_violations | GET /api/architecture/{id}/drift | TC-DRIFT-001 to TC-DRIFT-005 |
| SRS-014 | Graph visualization | D3GraphRenderer (frontend) | N/A | GET /api/architecture/{id}/graph | TC-VIZ-001 to TC-VIZ-004 |
| SRS-018 | Performance | TaskQueue, AnalysisWorker | task_queue (Redis) | N/A (internal) | TC-PERF-001 to TC-PERF-010 |
| SRS-019 | Redis queue | RedisClient, CeleryWorker | N/A (Redis) | N/A (internal) | TC-QUEUE-001 to TC-QUEUE-005 |

## 9.3 NFR to Verification Method Mapping

| NFR ID | Requirement | Verification Method | Success Criteria | Test Tool |
|--------|-------------|---------------------|------------------|-----------|
| NFR-001 | API response time | Performance testing | P95 < 500ms for GET, < 1s for POST | JMeter, Locust |
| NFR-002 | Concurrent requests | Load testing | 100 concurrent users without degradation | JMeter |
| NFR-003 | Horizontal scaling | Scalability testing | Linear scaling up to 50 workers | Kubernetes metrics |
| NFR-005 | Password policy | Security testing | All requirements enforced | Automated tests |
| NFR-006 | Authorization | Penetration testing | No unauthorized access | OWASP ZAP |
| NFR-007 | Data encryption | Security audit | TLS 1.3, AES-256 verified | SSL Labs, manual audit |
| NFR-008 | Input validation | Security testing | No injection vulnerabilities | OWASP ZAP, Burp Suite |
| NFR-011 | 99.5% uptime | Monitoring | < 43.8 hours downtime/year | Pingdom, Datadog |
| NFR-015 | User interface | Usability testing | 80% task completion rate | User testing sessions |
| NFR-019 | Code quality | Static analysis | > 80% coverage, < 10 complexity | SonarQube, pytest-cov |
| NFR-023 | Browser compatibility | Cross-browser testing | All features work on supported browsers | BrowserStack |
| NFR-026 | GDPR compliance | Compliance audit | All requirements met | Legal review |

## 9.4 Feature to Requirements Mapping

| Feature | Related URS | Related SRS | Related NFR | Priority | Status |
|---------|-------------|-------------|-------------|----------|--------|
| Code Review | URS-04 | SRS-007, SRS-008, SRS-009, SRS-010, SRS-011 | NFR-001, NFR-002, NFR-014 | Must Have | In Development |
| Architecture Analysis | URS-05 | SRS-012, SRS-013, SRS-014 | NFR-001, NFR-003, NFR-015 | Must Have | In Development |
| Authentication System | URS-01, URS-02, URS-07 | SRS-001, SRS-002, SRS-003 | NFR-005, NFR-006, NFR-007, NFR-009 | Must Have | In Development |
| Project Management | URS-03, URS-06 | SRS-004, SRS-005, SRS-006, SRS-015, SRS-016, SRS-017 | NFR-001, NFR-015, NFR-016 | Should Have | Planned |

---

# 10. Acceptance Criteria

## 10.1 Feature Acceptance Criteria

### Feature 1: Code Review
- [ ] System analyzes PR within 30 seconds of creation
- [ ] Analysis completes within 2 minutes for repositories < 50K LOC
- [ ] Issues are categorized into 4 severity levels
- [ ] Comments are posted to GitHub PR with file path and line number
- [ ] LLM provides actionable suggestions for each issue
- [ ] User can accept/dismiss feedback
- [ ] System handles syntax errors gracefully
- [ ] Fallback to secondary LLM on primary failure

### Feature 2: Architecture Analysis
- [ ] Dependency graph is stored in Neo4j
- [ ] Circular dependencies are detected and highlighted
- [ ] Graph renders within 5 seconds for < 1000 nodes
- [ ] User can zoom, pan, and filter graph
- [ ] Layer violations are identified
- [ ] Coupling metrics are calculated
- [ ] Graph can be exported as PNG/SVG

### Feature 3: Authentication System
- [ ] User can register with email and password
- [ ] Password meets complexity requirements
- [ ] JWT tokens are generated on login
- [ ] Tokens expire after 24 hours
- [ ] Refresh tokens work for 7 days
- [ ] RBAC enforces permissions
- [ ] Account locks after 5 failed attempts
- [ ] OAuth 2.0 works with GitHub

### Feature 4: Project Management
- [ ] User can add GitHub repository
- [ ] Webhook is configured automatically
- [ ] Repository list displays quality metrics
- [ ] Dashboard shows trends over time
- [ ] Reports can be exported as PDF
- [ ] Settings can be configured per project
- [ ] Audit log records all changes

---

# 11. Glossary

See Section 1.3 for acronyms and definitions.

---

# 12. Appendices

## Appendix A: References

1. ISO/IEC 25010:2011 - Systems and software Quality Requirements and Evaluation (SQuaRE)
2. ISO/IEC 23396:2020 - Software and systems engineering — Architectural design
3. OWASP Top 10 - 2021
4. GitHub REST API Documentation - https://docs.github.com/en/rest
5. OpenAI API Documentation - https://platform.openai.com/docs
6. Neo4j Graph Database Documentation - https://neo4j.com/docs/
7. JWT RFC 7519 - https://tools.ietf.org/html/rfc7519

## Appendix B: Document Conventions

- **Must Have**: Critical requirement for MVP release
- **Should Have**: Important but not critical for MVP
- **Could Have**: Desirable but can be deferred
- **Won't Have**: Out of scope for current release

## Appendix C: Change Log

| Version | Date | Section | Change Description | Author |
|---------|------|---------|-------------------|--------|
| v2.1 | 2026-02-16 | All | Added NFR chapter, completed all use cases, added API specs, added RTM | BaiXuan Zhang |
| v2.0 | 2026-02-13 | 5, 6 | Added use case diagrams and UC-01 description | BaiXuan Zhang |
| v1.0 | 2026-02-07 | All | Initial draft | BaiXuan Zhang |

---

**End of Software Requirements Specification**

---

**Document Approval**

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Author | BaiXuan Zhang | | 2026-02-16 |
| Reviewer | Dr. Siraprapa | | |
| Approver | | | |

