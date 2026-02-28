**\[AI-Based Reviewer on Project Code and Architecture\] - Software Requirement Specification (SRS)**

**Version:** \[ v0.5\]

**Date:** \[20/02/2026\]

**Document History\
**

  ------------- ------------ ------------- -------------- -------------------
  **Version**   **Date**     **Author**    **Reviewer**   **Changes**

  ------------- ------------ ------------- -------------- -------------------

  ------------ ------------ --------------- --------------- ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  V0.1         2026-02-07   BaiXuan Zhang   Dr. Siraprapa   Initial draft

  V0.2         2026-02-13   BaiXuan Zhang   Dr. Siraprapa   Complete revision with proposal alignment, added use cases

  V0.3         2026-02-16   BaiXuan Zhang   Dr. Siraprapa   Added NFR, completed all use cases, added RTM, API specs

  V0.4         2026-02-19   BaiXuan Zhang   Dr. Siraprapa   Added Section 10 Acceptance Criteria, Section 11 Appendices; aligned roles with enterprise_rbac_auth implementation (5 roles: Admin, Manager, Reviewer, Programmer, Visitor)

  V0.5         2026-02-20   BaiXuan Zhang   Dr. Siraprapa   Added Section 5.8 Portability Requirements, Section 5.9 Testability Specifications, per-requirement priority levels (P0-P3), enhanced RTM with full lifecycle traceability (Sections 9.5-9.10), comprehensive terminology glossary (Appendix C)
  ------------ ------------ --------------- --------------- ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# 1. Introduction

## 1.1 Purpose

This Software Requirement Specification (SRS) document defines the functional and non-functional requirements for the \"AI-Based Project Code and Architecture Review Platform\". It serves as the authoritative reference for the system\'s design, development, and validation, ensuring the platform meets the needs of automated code and architecture review workflows.

## 1.2 Scope

This SRS covers all core requirements of the platform, including:

**Core Functionality:** Automatic review of GitHub code repositories by integrating Abstract Syntax Trees (AST), Dependency Graphs, and Large Language Models (LLMs) to analyze code quality and architectural compliance.

**User Requirements:** Support for real-time feedback during code submission, automated detection of architectural deviations, and visual dashboards for project quality monitoring.

-   **Key Features Description:**

    -   **Feature #1:** Code Review - Automated quality control for pull requests with LLM code analysis\
        **Description:** Automated code quality assessment via LLM integration. System analyzes pull request code using AST parsing and LLM deep learning models to identify syntax errors, static semantic errors (such as type mismatch), and compilation errors. Provides instant inline comments with severity ratings so developers can understand issues directly in their PR workflow.

    -   **Priority:** Must Have

    -   **Feature #2:**Graph-based Architecture Analysis - Real-time monitoring of architectural drift using Neo4j\
        **Description:** Real-time architectural monitoring through Neo4j graph database integration. System continuously tracks dependency relationships, detects architectural drift patterns, identifies circular dependencies, and validates structural compliance against defined architecture standards. Dashboard visualization shows architecture health metrics in real-time for team visibility.

    -   **Priority:** Must Have

    -   **Feature #3:** Authenticated System - Role-based access control (RBAC) for enterprise security\
        **Description:** Enterprise-grade security with role-based access control. Ensures secure access control and audit compliance with comprehensive logging.

    -   **Priority:** Must Have

    -   **Feature #4:** Project Management - Lifecycle management of code analysis tasks\
        **Description:** Comprehensive repository and analysis task management. Provides dashboard for monitoring analysis queue, project health, and quality metrics over time.

    -   **Priority:** Should Have

## 1.3 Acronyms and Definitions

### 1.3.1 Acronyms

  -----------------------------------------------------------------------------------------------------------------------------
  **Acronym**   **Definition**
  ------------- ---------------------------------------------------------------------------------------------------------------
  **API**       Application Programming Interface

  **AST**       Abstract Syntax Tree - A tree representation of the abstract syntactic structure of source code

  **CFG**       Control Flow Graph - A representation of all paths that might be traversed through a program during execution

  **CI/CD**     Continuous Integration/Continuous Deployment

  **DXA**       Twentieth of a Point - Unit of measurement in Office Open XML (1440 DXA = 1 inch)

  **GDPR**      General Data Protection Regulation

  **HIPAA**     Health Insurance Portability and Accountability Act

  **JWT**       JSON Web Token - Compact, URL-safe means of representing claims between two parties

  **LLM**       Large Language Model - AI system trained on vast text data for understanding and generating text

  **LOC**       Lines of Code

  **MTTR**      Mean Time To Resolution

  **NFR**       Non-Functional Requirement

  **OWASP**     Open Web Application Security Project

  **PR**        Pull Request - Proposed code change submitted for review before merging

  **RBAC**      Role-Based Access Control - Access control paradigm where permissions associate with roles

  **REST**      Representational State Transfer

  **SDLC**      Software Development Life Cycle

  **SOC 2**     Service Organization Control 2 - Auditing standard for service organizations\' security

  **SRS**       Software Requirements Specification

  **TLS**       Transport Layer Security

  **URS**       User Requirements Specification
  -----------------------------------------------------------------------------------------------------------------------------

### 1.3.2 Definitions

  ---------------------------- -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  **Term**                     **Definition**

  **Architectural Drift**      Progressive deviation of a software system\'s actual structure from its intended design, typically accumulating through small incremental changes that individually appear harmless but collectively compromise architectural integrity.

  **Agentic AI**               Artificial intelligence system capable of autonomous reasoning, decision-making, and action execution within defined parameters, characterized by goal-directed behavior and contextual adaptation.

  **Baseline Configuration**   Formally reviewed and agreed-upon specification serving as the basis for further development, changeable only through formal change control. In this system, architectural baselines define expected structural patterns against which drift is measured.

  **Coupling Anomaly**         Unauthorized or unexpected dependency relationship between software modules that violates architectural constraints, potentially compromising modularity, testability, or maintainability.

  **Cyclic Dependency**        Circular reference pattern where Module A depends on Module B, which depends on Module C, which depends back on Module A, creating a dependency cycle that compromises system modularity and testing isolation.

  **Dependency Graph**         Directed graph structure representing relationships between software components, where nodes represent modules/classes and edges represent dependencies (imports, function calls, inheritance).

  **Explainable AI (XAI)**     AI techniques producing decisions, recommendations, or predictions accompanied by human-interpretable reasoning, enabling users to understand why the AI reached a particular conclusion.

  **Graph Database**           Database management system using graph structures with nodes, edges, and properties to represent and store data, optimized for querying relationships and traversing connected data patterns.

  **Layer Violation**          Architectural anti-pattern where code in one tier bypasses the immediately adjacent tier to access functionality in a non-adjacent tier, compromising separation of concerns (e.g., presentation layer directly accessing data layer).

  **Quality Gate**             Automated checkpoint in the development pipeline validating code against predefined quality criteria (test coverage, complexity metrics, security vulnerabilities) and blocking deployment if thresholds are not met.

  **Static Analysis**          Automated examination of source code without executing the program, identifying potential defects, security vulnerabilities, code smells, and compliance violations through pattern matching and rule-based evaluation.

  **Technical Debt**           Implied cost of future refactoring work caused by choosing quick/easy solutions now instead of better approaches that would take longer, accumulating maintenance burden over time.

  **Webhook**                  HTTP callback mechanism enabling real-time event notifications from one system to another, where the receiving system provides an endpoint URL that the sending system calls when specified events occur.
  ---------------------------- -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# 2. Overall Description

## 2.1 Product Perspective

The AI-Based Reviewer platform is a web-based application accessible from any device supporting a modern web browser. The system integrates with GitHub repositories and provides automated code review and architectural analysis capabilities.

System Environment:

• **Presentation Layer:** Web-based user interface delivering responsive, interactive dashboards with real-time updates, supporting both desktop and mobile browser access.

• **Application Layer:** RESTful API services providing asynchronous request processing with automatic documentation. Orchestrates business logic including user authentication, repository management, analysis task scheduling, and result aggregation. Supports horizontal scaling through stateless architecture.

• **Data Persistence Layer:** Hybrid database architecture combining graph database for relationship-intensive architectural data (code structure, dependencies, call relationships) with relational database for transactional data (user accounts, audit logs). In-memory data store provides caching and message queue functionality for asynchronous task processing.

• **AI Analysis Layer:** Integration with Large Language Model APIs providing contextual code analysis, architectural reasoning, and natural language suggestion generation. Implements fallback mechanisms and rate limiting. Enriches AI prompts with structural context from graph database, enabling architectural impact analysis.

• **Integration Layer:** GitHub webhook receivers for real-time pull request event notifications with automated comment posting. Secure authentication flow for repository access authorization. Supports webhook signature verification for security.

## 2.2 User Characteristics

  --------------------------- ---------------------------------------------- ------------------------------------------- ------------------------------------------------------------------------------------------------------------------------------------------------
  **Role**                    **Access Level**                               **Definition**                              **Responsibilities**

  **Administrator**           Full system access                             System-level configuration and management   User account management, system configuration, compliance settings, platform health monitoring, integration setup, security policy enforcement

  **Manager**                 Read-only comprehensive + project management   Project oversight and reporting             Dashboard monitoring, report generation, quality metrics review, team performance analysis, compliance oversight, project creation

  **Pull Request Reviewer**   Read/Write analysis access                     Code review and quality assurance           Code review execution, AI suggestion acceptance/rejection, architectural compliance validation, feedback provision to developers

  **Programmer**              Read/Write own projects                        Software developer submitting code          Code submission, PR creation, AI feedback interpretation, suggested fix implementation, project creation and management

  **Visitor**                 Read-only on granted projects                  Limited read-only access                    View project details and analysis results for projects explicitly granted by admin or project owner
  --------------------------- ---------------------------------------------- ------------------------------------------- ------------------------------------------------------------------------------------------------------------------------------------------------

## 2.3 Constraints

**Technical Constraints**

\- Must integrate with GitHub API and webhooks

\- Must support Python, JavaScript, TypeScript, Java, and Go for code analysis

\- Must operate within external API rate limits

\- Must support modern browsers (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+)

**Regulatory Constraints**

\- Must comply with GDPR for EU user data

\- Must comply with SOC 2 Type II for enterprise customers

\- Must implement OWASP Top 10 security controls

\- Must maintain audit logs for 7 years for compliance

**Business Constraints**

\- Initial release must support up to 100 concurrent users

\- Analysis must complete within 2 minutes for repositories \< 50K LOC

\- System must achieve 99.5% uptime SLA

\- Must support English language interface (internationalization in future releases)

# 3. User Requirement Specification (URS)

URS-01: Guest shall be able to register by providing username, email, and password.

URS-02: User shall be able to login using valid credentials.

URS-03: User shall be able to add GitHub repository by providing repository URL.

URS-04: User shall receive automated code review feedback when pull request is submitted on github.

URS-05: User shall be able to view interactive dependency graphs and architecture evolution.

URS-06: Manager shall be able to view code quality metrics dashboard with exportable reports.

URS-07: Administrator shall be able to configure analysis settings and compliance standards.

  ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  **ID**       **Priority**   **User Story**                                                                                                                         **Acceptance Criteria**
  ------------ -------------- -------------------------------------------------------------------------------------------------------------------------------------- ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  **URS-01**   Must Have      As a Guest, I want to register by providing username, email, and password, so that I can access the platform                           \- Registration form validates input in real-time\<br\>- System sends confirmation email\<br\>- Account is created with default \"User\" role\<br\>- User is redirected to login page

  **URS-02**   Must Have      As a User, I want to login using valid credentials, so that I can access my projects                                                   \- System validates credentials\<br\>- JWT token is generated with 24-hour expiry\<br\>- User is redirected to dashboard\<br\>- Failed attempts are logged

  **URS-03**   Must Have      As a User, I want to add GitHub repository by providing repository URL, so that it can be analyzed                                     \- System validates GitHub URL format\<br\>- OAuth authorization flow is initiated\<br\>- Webhook is configured automatically\<br\>- Repository appears in project list

  **URS-04**   Must Have      As a Programmer, I want to receive automated code review feedback when pull request is submitted, so that I can improve code quality   \- Analysis starts within 30 seconds of PR creation\<br\>- Comments are posted to GitHub PR\<br\>- Issues are categorized by severity\<br\>- Suggestions are actionable

  **URS-05**   Should Have    As a Reviewer, I want to view interactive dependency graphs and architecture evolution, so that I can understand system structure      \- Graph renders within 5 seconds\<br\>- Supports zoom, pan, and filter\<br\>- Shows circular dependencies highlighted\<br\>- Displays historical changes

  **URS-06**   Should Have    As a Manager, I want to view code quality metrics dashboard with exportable reports, so that I can track team performance              \- Dashboard loads within 3 seconds\<br\>- Shows trends over time\<br\>- Supports PDF/CSV export\<br\>- Includes quality score, issue counts, technical debt

  **URS-07**   Must Have      As an Administrator, I want to configure analysis settings and compliance standards, so that I can customize platform behavior         \- Settings are saved immediately\<br\>- Changes apply to new analyses\<br\>- Supports ISO/IEC 25010, Google Style Guide\<br\>- Audit log records all changes
  ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# 4. Software Requirement Specification (SRS)

**Priority Level Classification:**
- **P0 (Critical)**: System cannot function without this requirement. Failure causes complete system failure or critical security breach.
- **P1 (High)**: Core functionality requirement. Failure significantly impacts primary use cases.
- **P2 (Medium)**: Important but not critical. Failure impacts secondary features or user experience.
- **P3 (Low)**: Nice-to-have enhancement. Failure has minimal impact on core functionality.

4.1 Authentication and Authorization

  ----------------- ----------------- ------- ----------------------------------------------------------------- -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  ID                Priority          Level   Requirement                                                       Acceptance Criteria

  SRS-001           Must Have         P0      System shall authenticate users using secure token-based system   \- Access tokens expire after 24 hours\<br\>- Refresh tokens valid for 7 days\<br\>- Passwords must be securely hashed\<br\>- Tokens include user ID, role, and expiry

  SRS-002           Must Have         P0      System shall implement role-based access control (RBAC) with 5 roles            \- Permissions enforced at API level\<br\>- Roles: Visitor \< Programmer \< Reviewer \< Manager \< Admin\<br\>- Unauthorized access returns HTTP 403\<br\>- All access attempts logged

  SRS-003           Must Have         P1      System shall support secure authorization for GitHub integration                           \- Standard authorization flow implemented\<br\>- Tokens stored encrypted\<br\>- Supports token refresh\<br\>- Revocation supported
  ----------------- ----------------- ------- ----------------------------------------------------------------- -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

4.2 Repository Management

  ----------- ------------- ------- ---------------------------------------------------------------- ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  ID          Priority      Level   Requirement                                                      Acceptance Criteria

  SRS-004     Must Have     P1      System shall configure GitHub webhooks for pull request events   \- Webhook endpoint configured\<br\>- Events: PR opened, synchronized, closed\<br\>- Signature verification for security\<br\>- Retry failed deliveries up to 3 times

  SRS-005     Must Have     P1      System shall validate GitHub repository URLs before adding       \- Format: https://github.com/{owner}/{repo}\<br\>- Checks repository exists\<br\>- Verifies user has admin access\<br\>- Prevents duplicate additions

  SRS-006     Should Have   P2      System shall support repository synchronization                  \- Fetches latest commits\<br\>- Updates branch information\<br\>- Syncs PR list\<br\>- Runs on-demand or scheduled
  ----------- ------------- ------- ---------------------------------------------------------------- ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

4.3 Code Analysis

  ----------------- ----------------- ------- -------------------------------------------------------------------------- --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  ID                Priority          Level   Requirement                                                                Acceptance Criteria

  SRS-007           Must Have         P1      System shall parse source code to generate abstract syntax trees and extract dependencies    \- Supports Python, JavaScript, TypeScript, Java, Go\<br\>- Extracts imports, function calls, class inheritance\<br\>- Handles syntax errors gracefully\<br\>- Generates AST within 2 seconds per file

  SRS-008           Must Have         P1      System shall integrate with AI language models for code analysis   \- Sends code with architectural context\<br\>- Implements rate limiting\<br\>- Fallback to secondary model on failure\<br\>- Timeout after 30 seconds

  SRS-009           Must Have         P1      System shall categorize issues by severity (Critical, High, Medium, Low)   \- Critical: Security vulnerabilities, data loss risks\<br\>- High: Logic errors, performance issues\<br\>- Medium: Code smells, maintainability\<br\>- Low: Style violations, minor improvements

  SRS-010           Must Have         P1      System shall post review comments to GitHub pull requests                     \- Comments include file path, line number, description\<br\>- Grouped by severity\<br\>- Includes suggested fixes\<br\>- Posted within 1 minute of analysis completion

  SRS-011           Should Have       P2      System shall capture user feedback (Accept/Dismiss) on review comments     \- Feedback stored in database\<br\>- Used for model refinement\<br\>- Aggregated in analytics dashboard\<br\>- Supports bulk actions
  ----------------- ----------------- ------- -------------------------------------------------------------------------- --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

4.4 Architecture Analysis

  ----------------- ----------------- ------- ---------------------------------------------------------------------------------------------------------------------- -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  ID                Priority          Level   Requirement                                                                                                            Acceptance Criteria

  SRS-012           Must Have         P1      System shall store dependency graphs in graph database                                                                 \- Nodes: Modules, Classes, Functions\<br\>- Relationships: DEPENDS_ON, CALLS, INHERITS\<br\>- Properties: name, path, complexity, timestamp\<br\>- Indexed by project_id and entity_name

  SRS-013           Must Have         P1      System shall detect architectural drift by identifying cyclic dependencies, coupling anomalies, and layer violations   \- Cyclic dependencies detected using graph algorithms\<br\>- Coupling measured by dependency count\<br\>- Layer violations checked against defined architecture\<br\>- Results stored with severity rating

  SRS-014           Should Have       P2      System shall render interactive dependency graphs                                                          \- Supports zoom (0.1x to 10x)\<br\>- Pan with mouse drag\<br\>- Filter by entity type, severity\<br\>- Export as PNG/SVG\<br\>- Loads within 5 seconds for graphs \< 1000 nodes
  ----------------- ----------------- ------- ---------------------------------------------------------------------------------------------------------------------- -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

4.5 Compliance Verification

  ----------------- ----------------- ------- --------------------------------------------------------------------------- -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  ID                Priority          Level   Requirement                                                                 Acceptance Criteria

  SRS-015           Must Have         P1      System shall verify compliance with ISO/IEC 25010 quality model             \- Checks: Functionality, Reliability, Usability, Efficiency, Maintainability, Portability\<br\>- Generates compliance report\<br\>- Highlights violations\<br\>- Provides remediation guidance

  SRS-016           Should Have       P2      System shall verify compliance with ISO/IEC 23396 architectural standards   \- Validates layered architecture\<br\>- Checks separation of concerns\<br\>- Verifies interface contracts\<br\>- Reports architectural anti-patterns

  SRS-017           Should Have       P3      System shall verify compliance with Google Style Guides                     \- Language-specific rules (Python PEP 8, JavaScript Standard)\<br\>- Naming conventions\<br\>- Documentation requirements\<br\>- Configurable rule sets
  ----------------- ----------------- ------- --------------------------------------------------------------------------- -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

4.6 Performance and Scalability

  ----------------- ----------------- ------- --------------------------------------------------------------------- ----------------------------------------------------------------------------------------------------------------------------------------------------
  ID                Priority          Level   Requirement                                                           Acceptance Criteria

  SRS-018           Must Have         P1      System shall process small repositories (\<10K LOC) in 8-12 seconds   \- P50: 8 seconds\<br\>- P95: 12 seconds\<br\>- P99: 15 seconds\<br\>- Measured from webhook receipt to comment posting

  SRS-019           Must Have         P1      System shall use message queue for asynchronous task processing                  \- Tasks queued immediately (\< 100ms)\<br\>- FIFO processing order\<br\>- Failed tasks retry with exponential backoff\<br\>- Max 3 retry attempts

  SRS-020           Should Have       P2      System shall support horizontal scaling of analysis workers           \- Stateless worker design\<br\>- Load balanced via message queue\<br\>- Auto-scaling based on queue depth\<br\>- Graceful shutdown on scale-down
  ----------------- ----------------- ------- --------------------------------------------------------------------- ----------------------------------------------------------------------------------------------------------------------------------------------------

# 5. Non-Functional Requirements (NFR)

## 5.1 Performance Requirements

  ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  ID             Category         Requirement                                                 Target                                                                                                                            Measurement Method
  -------------- ---------------- ----------------------------------------------------------- --------------------------------------------------------------------------------------------------------------------------------- ------------------------------------------
  NFR-001        Response Time    API endpoints shall respond within acceptable time limits   \- GET requests: \< 500ms (P95)\<br\>- POST requests: \< 1s (P95)\<br\>- Analysis tasks: \< 2min for \<50K LOC                    Application Performance Monitoring (APM)

  NFR-002        Throughput       System shall handle concurrent analysis requests            \- 10 concurrent analyses\<br\>- 100 concurrent API requests\<br\>- 1000 concurrent dashboard users                               Load testing with JMeter

  NFR-003        Scalability      System shall scale horizontally to handle increased load    \- Add workers without downtime\<br\>- Linear performance scaling up to 50 workers\<br\>- Auto-scale based on queue depth \> 20   Kubernetes HPA metrics

  NFR-004        Resource Usage   Analysis workers shall operate within resource limits       \- CPU: \< 2 cores per worker\<br\>- Memory: \< 4GB per worker\<br\>- Disk I/O: \< 100 MB/s                                       Container resource monitoring
  ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

## 5.2 Security Requirements

  --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  ID            Category                   Requirement                                                  Implementation                                                                                                                                          Verification
  ------------- -------------------------- ------------------------------------------------------------ ------------------------------------------------------------------------------------------------------------------------------------------------------- ------------------------------
  NFR-005       Authentication             System shall enforce strong password policies                \- Min 8 characters\<br\>- Uppercase, lowercase, number, special char\<br\>- Password history (last 5)\<br\>- Account lockout after 5 failed attempts   Automated security tests

  NFR-006       Authorization              System shall implement least privilege access control        \- Role-based permissions\<br\>- Resource-level access control\<br\>- API endpoint authorization\<br\>- Audit all access attempts                       Penetration testing

  NFR-007       Data Encryption            System shall encrypt sensitive data at rest and in transit   \- TLS 1.3 for all connections\<br\>- AES-256 for database encryption\<br\>- Encrypted environment variables\<br\>- Secure key management (AWS KMS)     Security audit

  NFR-008       Input Validation           System shall validate and sanitize all user inputs           \- SQL injection prevention\<br\>- XSS protection\<br\>- CSRF tokens\<br\>- Rate limiting (100 req/min per user)                                        OWASP ZAP scanning

  NFR-009       Audit Logging              System shall log all security-relevant events                \- Authentication attempts\<br\>- Authorization failures\<br\>- Data modifications\<br\>- Configuration changes\<br\>- Retention: 7 years               Log analysis tools

  NFR-010       Vulnerability Management   System shall be scanned for vulnerabilities regularly        \- Weekly dependency scans\<br\>- Monthly penetration tests\<br\>- Automated CVE monitoring\<br\>- Patch within 30 days of disclosure                   Snyk, OWASP Dependency-Check
  --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

## 5.3 Availability and Reliability

  -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  ID            Category              Requirement                                         Target                                                                                                                                                                      Measurement
  ------------- --------------------- --------------------------------------------------- --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- -----------------------------
  NFR-011       Uptime                System shall maintain high availability             \- 99.5% uptime (43.8 hours downtime/year)\<br\>- Planned maintenance windows: 4 hours/month\<br\>- Unplanned downtime: \< 2 hours/month                                    Uptime monitoring (Pingdom)

  NFR-012       Fault Tolerance       System shall handle component failures gracefully   \- Database failover: \< 30 seconds\<br\>- Service restart: \< 10 seconds\<br\>- No data loss on failure\<br\>- Automatic retry for transient errors                        Chaos engineering tests

  NFR-013       Backup and Recovery   System shall backup data regularly                  \- Database backups: Daily full, hourly incremental\<br\>- Retention: 30 days\<br\>- Recovery Time Objective (RTO): 4 hours\<br\>- Recovery Point Objective (RPO): 1 hour   Disaster recovery drills

  NFR-014       Error Handling        System shall handle errors gracefully               \- User-friendly error messages\<br\>- Detailed logs for debugging\<br\>- Automatic error reporting\<br\>- Graceful degradation                                             Error tracking (Sentry)
  -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

## 5.4 Usability Requirements

  -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  ID             Category         Requirement                                             Criteria                                                                                                                                                                   Validation
  -------------- ---------------- ------------------------------------------------------- -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- ----------------------
  NFR-015        User Interface   System shall provide intuitive user interface           \- Consistent design language\<br\>- Responsive layout (mobile, tablet, desktop)\<br\>- Accessibility (WCAG 2.1 Level AA)\<br\>- Loading indicators for async operations   Usability testing

  NFR-016        Documentation    System shall provide comprehensive documentation        \- User guide\<br\>- API documentation (OpenAPI)\<br\>- Administrator manual\<br\>- Inline help and tooltips                                                               Documentation review

  NFR-017        Learnability     New users shall be productive within 30 minutes         \- Onboarding tutorial\<br\>- Sample projects\<br\>- Video tutorials\<br\>- Context-sensitive help                                                                         User testing

  NFR-018        Error Messages   System shall provide clear, actionable error messages   \- Plain language (no technical jargon)\<br\>- Specific problem description\<br\>- Suggested resolution steps\<br\>- Link to documentation                                 User feedback
  -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

## 5.5 Maintainability Requirements

  -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  ID            Category       Requirement                                      Implementation                                                                                                                                     Verification
  ------------- -------------- ------------------------------------------------ -------------------------------------------------------------------------------------------------------------------------------------------------- ----------------------
  NFR-019       Code Quality   Codebase shall maintain high quality standards   \- Test coverage: \> 80%\<br\>- Code complexity: \< 10 cyclomatic complexity\<br\>- Documentation: All public APIs\<br\>- Linting: Zero warnings   CI/CD quality gates

  NFR-020       Modularity     System shall be modular and loosely coupled      \- Microservices architecture\<br\>- Clear service boundaries\<br\>- API-based communication\<br\>- Independent deployment                         Architecture review

  NFR-021       Monitoring     System shall provide comprehensive monitoring    \- Application metrics (Prometheus)\<br\>- Log aggregation (ELK)\<br\>- Distributed tracing (Jaeger)\<br\>- Alerting (PagerDuty)                   Monitoring dashboard

  NFR-022       Deployment     System shall support automated deployment        \- CI/CD pipeline (GitHub Actions)\<br\>- Infrastructure as Code (Terraform)\<br\>- Blue-green deployment\<br\>- Rollback capability               Deployment tests
  -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

## 5.6 Compatibility Requirements

  ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  Category                Requirement                                           Supported Versions                                                                                      Testing
  ----------------------- ----------------------------------------------------- ------------------------------------------------------------------------------------------------------- -------------------------
  Browser Compatibility   System shall support modern web browsers              \- Chrome 90+\<br\>- Firefox 88+\<br\>- Safari 14+\<br\>- Edge 90+                                      Cross-browser testing

  Programming Languages   System shall analyze multiple programming languages   \- Python 3.8+\<br\>- JavaScript ES6+\<br\>- TypeScript 4.0+\<br\>- Java 11+\<br\>- Go 1.16+            Language-specific tests

  Integration             System shall integrate with external services         \- GitHub API v3\<br\>- OpenAI API v1\<br\>- Anthropic API v1\<br\>- Neo4j 4.4+\<br\>- PostgreSQL 13+   Integration tests
  ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

## 5.7 Compliance Requirements

  --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  ID             Category             Requirement                                            Standard                                                                                          Audit Frequency
  -------------- -------------------- ------------------------------------------------------ ------------------------------------------------------------------------------------------------- -----------------
  NFR-026        Data Privacy         System shall comply with data protection regulations   \- GDPR (EU)\<br\>- CCPA (California)\<br\>- Data retention policies\<br\>- Right to deletion     Annual

  NFR-027        Security Standards   System shall comply with security standards            \- SOC 2 Type II\<br\>- OWASP Top 10\<br\>- CWE Top 25\<br\>- ISO 27001                           Bi-annual

  NFR-028        Accessibility        System shall comply with accessibility standards       \- WCAG 2.1 Level AA\<br\>- Section 508\<br\>- Keyboard navigation\<br\>- Screen reader support   Quarterly
  --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

## 5.8 Portability Requirements

  -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  ID             Category                    Requirement                                                    Quantified Target                                                                                                                                    Verification Method
  -------------- --------------------------- -------------------------------------------------------------- -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- ---------------------------
  NFR-029        Platform Independence       System shall run on multiple operating systems                 \- Linux (Ubuntu 20.04+, RHEL 8+, Amazon Linux 2)\<br\>- Windows Server 2019+\<br\>- macOS 11+ (development only)\<br\>- Container runtime: Docker 20.10+, Kubernetes 1.21+                           Cross-platform testing

  NFR-030        Database Portability        System shall support migration between database instances      \- PostgreSQL migration time: \< 2 hours for 100GB database\<br\>- Neo4j migration time: \< 1 hour for 1M nodes\<br\>- Zero data loss during migration\<br\>- Automated migration scripts provided   Migration testing

  NFR-031        Cloud Provider Portability  System shall be deployable on multiple cloud platforms         \- AWS (primary): ECS, RDS, ElastiCache\<br\>- Azure (secondary): AKS, Azure Database, Redis Cache\<br\>- GCP (tertiary): GKE, Cloud SQL, Memorystore\<br\>- Migration time between clouds: \< 8 hours   Multi-cloud deployment

  NFR-032        Data Export Portability     System shall export data in standard, interoperable formats    \- User data: JSON (RFC 8259)\<br\>- Analysis results: CSV (RFC 4180), JSON\<br\>- Architecture graphs: GraphML, GEXF, JSON\<br\>- Reports: PDF/A-1b, HTML5\<br\>- Export completion: \< 5 minutes for 10K records   Export validation tests

  NFR-033        Configuration Portability   System shall support environment-agnostic configuration        \- Environment variables for all deployment-specific settings\<br\>- Configuration templates provided for dev, staging, production\<br\>- No hardcoded environment-specific values\<br\>- Configuration validation on startup   Configuration audit

  NFR-034        API Version Portability     System shall maintain backward compatibility for API versions  \- Support N-1 API version for minimum 12 months\<br\>- Deprecation notice: 6 months before removal\<br\>- Version negotiation via Accept header\<br\>- Breaking changes only in major versions                                API compatibility tests

  NFR-035        LLM Provider Portability    System shall support multiple LLM providers interchangeably    \- OpenAI GPT-4 (primary)\<br\>- Anthropic Claude 3.5 (secondary)\<br\>- Azure OpenAI (tertiary)\<br\>- Provider switch time: \< 5 minutes via configuration\<br\>- Consistent output format across providers                   Provider switching tests
  -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

## 5.9 Testability Specifications for Non-Functional Requirements

This section defines how each NFR category will be tested, measured, and validated to ensure compliance with specified targets.

### 5.9.1 Performance Testing Specifications

| NFR ID | Test Type | Test Tool | Test Data | Pass Criteria | Test Frequency |
|--------|-----------|-----------|-----------|---------------|----------------|
| NFR-001 | Load Testing | Apache JMeter, k6 | Synthetic API requests with realistic payloads | P95 latency meets targets for 3 consecutive runs | Every release |
| NFR-002 | Concurrency Testing | Locust, Artillery | 100 concurrent users, 10 concurrent analyses | No errors, throughput ≥ target for 10 minutes | Every release |
| NFR-003 | Scalability Testing | Kubernetes HPA + Prometheus | Queue depth 0→50→100 tasks | Linear scaling, no performance degradation | Monthly |
| NFR-004 | Resource Monitoring | Prometheus + Grafana | Production workload simulation | Resource usage within limits for 24 hours | Continuous |

### 5.9.2 Security Testing Specifications

| NFR ID | Test Type | Test Tool | Test Scope | Pass Criteria | Test Frequency |
|--------|-----------|-----------|------------|---------------|----------------|
| NFR-005 | Password Policy Testing | Automated unit tests | Registration, password change flows | All policy rules enforced, lockout functional | Every build |
| NFR-006 | Authorization Testing | Postman, pytest | All API endpoints, all roles | Unauthorized access returns 403, audit logged | Every release |
| NFR-007 | Encryption Validation | SSL Labs, testssl.sh | TLS configuration, database encryption | A+ rating, AES-256 verified | Quarterly |
| NFR-008 | Vulnerability Scanning | OWASP ZAP, Burp Suite | All web endpoints, input fields | Zero high/critical vulnerabilities | Weekly |
| NFR-009 | Audit Log Testing | Log analysis scripts | All security events | 100% event capture, 7-year retention verified | Monthly |
| NFR-010 | Dependency Scanning | Snyk, OWASP Dependency-Check | All project dependencies | Zero high/critical CVEs | Daily (CI/CD) |

### 5.9.3 Availability and Reliability Testing Specifications

| NFR ID | Test Type | Test Tool | Test Scenario | Pass Criteria | Test Frequency |
|--------|-----------|-----------|---------------|---------------|----------------|
| NFR-011 | Uptime Monitoring | Pingdom, UptimeRobot | 24/7 endpoint monitoring | ≥99.5% uptime over 30 days | Continuous |
| NFR-012 | Chaos Engineering | Chaos Monkey, Gremlin | Random service/pod termination | Automatic recovery, no data loss | Monthly |
| NFR-013 | Backup/Recovery Testing | Custom scripts | Full database restore | RTO ≤ 4 hours, RPO ≤ 1 hour, data integrity 100% | Quarterly |
| NFR-014 | Error Handling Testing | Pytest, integration tests | Network failures, invalid inputs, timeouts | Graceful degradation, user-friendly messages | Every release |

### 5.9.4 Usability Testing Specifications

| NFR ID | Test Type | Test Method | Test Participants | Pass Criteria | Test Frequency |
|--------|-----------|-------------|-------------------|---------------|----------------|
| NFR-015 | UI/UX Testing | User testing sessions, heuristic evaluation | 5-10 representative users | SUS score ≥ 70, task completion ≥ 90% | Every major release |
| NFR-016 | Documentation Review | Peer review, user feedback | Technical writers, end users | Completeness 100%, clarity rating ≥ 4/5 | Every release |
| NFR-017 | Learnability Testing | Time-to-task completion | 5 new users | 80% complete onboarding tasks in ≤ 30 minutes | Every major release |
| NFR-018 | Error Message Testing | Usability testing, A/B testing | 10 users per error scenario | 80% understand problem and resolution | Every release |

### 5.9.5 Maintainability Testing Specifications

| NFR ID | Test Type | Test Tool | Measurement | Pass Criteria | Test Frequency |
|--------|-----------|-----------|-------------|---------------|----------------|
| NFR-019 | Code Quality Analysis | SonarQube, CodeClimate | Coverage, complexity, duplication | Coverage ≥80%, complexity ≤10, duplication ≤3% | Every commit |
| NFR-020 | Architecture Compliance | ArchUnit, dependency-cruiser | Module dependencies, layer violations | Zero violations of defined architecture rules | Every build |
| NFR-021 | Monitoring Validation | Prometheus queries, Grafana dashboards | Metric completeness, alert functionality | 100% critical metrics captured, alerts fire correctly | Monthly |
| NFR-022 | Deployment Testing | CI/CD pipeline execution | Automated deployment to staging | Zero-downtime deployment, rollback in ≤ 5 minutes | Every deployment |

### 5.9.6 Compatibility Testing Specifications

| NFR ID | Test Type | Test Tool | Test Matrix | Pass Criteria | Test Frequency |
|--------|-----------|-----------|-------------|---------------|----------------|
| NFR-023 | Browser Compatibility | BrowserStack, Selenium Grid | Chrome 90+, Firefox 88+, Safari 14+, Edge 90+ | 100% functional parity, visual consistency | Every release |
| NFR-024 | Language Support Testing | Language-specific test suites | Python 3.8+, JS ES6+, TS 4.0+, Java 11+, Go 1.16+ | Successful AST parsing, accurate analysis | Every release |
| NFR-025 | Integration Testing | Postman, pytest | GitHub API v3, OpenAI API, Neo4j 4.4+, PostgreSQL 13+ | All integrations functional, error handling verified | Every release |

### 5.9.7 Compliance Testing Specifications

| NFR ID | Test Type | Test Method | Audit Scope | Pass Criteria | Test Frequency |
|--------|-----------|-------------|-------------|---------------|----------------|
| NFR-026 | GDPR Compliance Audit | Manual audit + automated checks | Data collection, storage, deletion, export | 100% compliance with GDPR articles | Annual |
| NFR-027 | Security Standards Audit | Third-party SOC 2 audit | Infrastructure, access controls, monitoring | SOC 2 Type II certification | Bi-annual |
| NFR-028 | Accessibility Testing | axe DevTools, WAVE, manual testing | All UI components, keyboard navigation | WCAG 2.1 Level AA compliance, zero critical issues | Quarterly |

### 5.9.8 Portability Testing Specifications

| NFR ID | Test Type | Test Environment | Test Procedure | Pass Criteria | Test Frequency |
|--------|-----------|------------------|----------------|---------------|----------------|
| NFR-029 | Platform Testing | Ubuntu 20.04, RHEL 8, Windows Server 2019, Docker, K8s | Deploy and run full test suite on each platform | 100% test pass rate on all platforms | Every major release |
| NFR-030 | Database Migration Testing | Staging environment | Execute migration scripts, validate data integrity | Migration time within target, zero data loss | Before each migration |
| NFR-031 | Multi-Cloud Deployment | AWS, Azure, GCP test accounts | Deploy infrastructure, run smoke tests | Successful deployment, all services operational | Quarterly |
| NFR-032 | Data Export Testing | Production-like dataset | Export all data types, validate format compliance | Valid format, complete data, time within target | Every release |
| NFR-033 | Configuration Testing | Dev, staging, production configs | Deploy with each config, validate behavior | No hardcoded values, successful startup | Every deployment |
| NFR-034 | API Versioning Testing | Automated API tests | Test N and N-1 API versions simultaneously | Both versions functional, backward compatibility maintained | Every API change |
| NFR-035 | LLM Provider Testing | OpenAI, Anthropic, Azure OpenAI | Switch providers, run analysis suite | Consistent results, switch time within target | Monthly |

# 5A. Interface Requirements

## 5A.1 User Interface Requirements

### 5A.1.1 General UI Requirements

| ID | Requirement | Specification | Priority |
|----|-------------|---------------|----------|
| UI-001 | Responsive Design | System shall provide responsive layouts for desktop (≥1920px), tablet (768-1919px), and mobile (≤767px) | Must Have |
| UI-002 | Theme Support | System shall support light and dark themes with user preference persistence | Should Have |
| UI-003 | Navigation | System shall provide consistent navigation with breadcrumbs, sidebar menu, and top navigation bar | Must Have |
| UI-004 | Loading States | System shall display loading indicators for all asynchronous operations (spinners, progress bars, skeleton screens) | Must Have |
| UI-005 | Error Display | System shall display inline validation errors, toast notifications for actions, and modal dialogs for critical errors | Must Have |

### 5A.1.2 Dashboard Interface

| Component | Description | Interaction | Accessibility |
|-----------|-------------|-------------|---------------|
| **Project List** | Grid/list view of all accessible projects with search and filter | Click to view details, hover for quick actions | Keyboard navigable, ARIA labels |
| **Analysis Queue** | Real-time queue status with progress indicators | Auto-refresh every 5 seconds, manual refresh button | Screen reader announcements |
| **Metrics Dashboard** | Charts showing code quality trends, issue distribution, analysis history | Interactive charts with drill-down, export to CSV/PDF | Alt text for charts, data tables |
| **Recent Activity** | Timeline of recent reviews, comments, and system events | Infinite scroll, filter by date/user/action | Semantic HTML, focus management |

### 5A.1.3 Code Review Interface

| Component | Description | Interaction | Accessibility |
|-----------|-------------|-------------|---------------|
| **Diff Viewer** | Side-by-side or unified diff view with syntax highlighting | Toggle view mode, expand/collapse sections | Keyboard shortcuts, high contrast |
| **Comment Thread** | Inline comments with replies, reactions, and resolution status | Add/edit/delete comments, resolve threads | Focus trap in modals, ARIA live regions |
| **Suggestion Panel** | AI-generated suggestions with severity, confidence, and explanation | Accept/reject/modify suggestions, view details | Keyboard navigation, screen reader support |
| **File Tree** | Hierarchical view of changed files with status indicators | Expand/collapse folders, jump to file | Tree navigation with arrow keys |

### 5A.1.4 Architecture Visualization Interface

| Component | Description | Interaction | Accessibility |
|-----------|-------------|-------------|---------------|
| **Dependency Graph** | Interactive force-directed graph with nodes (modules) and edges (dependencies) | Zoom, pan, drag nodes, filter by type/severity | SVG with ARIA labels, keyboard zoom |
| **Graph Controls** | Toolbar with layout options, filters, search, and export | Click to apply, keyboard shortcuts | Button labels, focus indicators |
| **Node Details Panel** | Side panel showing module details, metrics, and dependencies | Click node to open, close with X or ESC | Modal dialog, focus management |
| **Legend** | Visual legend for node colors, edge types, and severity indicators | Static display, tooltips on hover | Text alternatives, high contrast |

## 5A.2 Hardware Interface Requirements

### 5A.2.1 Client Hardware Requirements

| Component | Minimum | Recommended | Purpose |
|-----------|---------|-------------|---------|
| **Processor** | Dual-core 2.0 GHz | Quad-core 2.5 GHz+ | Browser rendering, JavaScript execution |
| **Memory** | 4 GB RAM | 8 GB RAM+ | Multiple browser tabs, large graph rendering |
| **Display** | 1366x768 resolution | 1920x1080+ resolution | UI visibility, graph visualization |
| **Network** | 5 Mbps download, 1 Mbps upload | 25 Mbps download, 5 Mbps upload | API requests, real-time updates |
| **Storage** | 100 MB free space | 500 MB free space | Browser cache, local storage |

### 5A.2.2 Server Hardware Requirements

| Component | Development | Staging | Production | Purpose |
|-----------|-------------|---------|------------|---------|
| **CPU** | 2 vCPU | 2 vCPU | 4-8 vCPU (auto-scale) | API processing, analysis tasks |
| **Memory** | 4 GB | 4 GB | 8-16 GB (auto-scale) | Application runtime, caching |
| **Storage** | 20 GB SSD | 50 GB SSD | 200 GB SSD | Application files, logs, temp data |
| **Network** | 100 Mbps | 1 Gbps | 10 Gbps | API traffic, database connections |
| **Database Storage** | 10 GB | 50 GB | 500 GB (expandable) | PostgreSQL, Neo4j data |

## 5A.3 Software Interface Requirements

### 5A.3.1 External Service Interfaces

| Service | Interface Type | Protocol | Authentication | Data Format | Error Handling |
|---------|---------------|----------|----------------|-------------|----------------|
| **GitHub API** | REST API | HTTPS | OAuth 2.0 | JSON | Retry with exponential backoff, fallback to webhook queue |
| **OpenAI API** | REST API | HTTPS | API Key (Bearer token) | JSON | Rate limit handling, fallback to Claude API |
| **Anthropic Claude API** | REST API | HTTPS | API Key (x-api-key header) | JSON | Rate limit handling, queue requests |
| **Neo4j AuraDB** | Bolt Protocol | bolt+s:// | Username/Password | Cypher queries | Connection pooling, automatic reconnection |
| **PostgreSQL** | Native Protocol | TCP/IP (SSL) | Username/Password | SQL | Connection pooling, transaction retry |
| **Redis** | RESP Protocol | TCP/IP | Password (optional) | Key-value | Automatic reconnection, fallback to direct processing |

### 5A.3.2 Internal Service Interfaces

| Service | Interface | Port | Protocol | Data Format | Purpose |
|---------|-----------|------|----------|-------------|---------|
| **API Gateway** | REST API | 3000 | HTTP/HTTPS | JSON | Route requests to backend services |
| **Auth Service** | REST API | 3001 | HTTP | JSON | Authentication, authorization, session management |
| **Code Review Service** | REST API | 3002 | HTTP | JSON | AST parsing, LLM integration, review generation |
| **Architecture Service** | REST API | 3003 | HTTP | JSON | Graph analysis, drift detection, visualization data |
| **Project Service** | REST API | 3004 | HTTP | JSON | Repository management, webhook handling |
| **Audit Service** | REST API | 3005 | HTTP | JSON | Audit log creation, querying, reporting |

### 5A.3.3 Database Interfaces

| Database | Version | Connection | Query Language | Purpose | Backup |
|----------|---------|------------|----------------|---------|--------|
| **PostgreSQL** | 15+ | psycopg2 (Python), pg (Node.js) | SQL | User data, projects, audit logs, sessions | Daily full, hourly incremental |
| **Neo4j** | 5.x | neo4j-driver (Python/JS) | Cypher | Dependency graphs, AST storage, architecture data | Daily snapshot |
| **Redis** | 7.x | redis-py (Python), ioredis (Node.js) | Redis commands | Caching, session storage, task queue | AOF persistence |

## 5A.4 Communication Interfaces

### 5A.4.1 Network Protocols

| Protocol | Usage | Port | Encryption | Purpose |
|----------|-------|------|------------|---------|
| **HTTPS** | Web traffic, API requests | 443 | TLS 1.3 | Secure client-server communication |
| **WebSocket** | Real-time updates | 443 (WSS) | TLS 1.3 | Live dashboard updates, notification push |
| **Bolt+S** | Neo4j connection | 7687 | TLS | Secure graph database queries |
| **PostgreSQL SSL** | Database connection | 5432 | TLS | Secure relational database access |

### 5A.4.2 Data Exchange Formats

| Format | Usage | Schema Validation | Versioning |
|--------|-------|-------------------|------------|
| **JSON** | API requests/responses | JSON Schema | API version in URL path (/api/v1/) |
| **JSON Lines** | Log streaming | Line-delimited JSON | N/A |
| **CSV** | Data export | RFC 4180 | N/A |
| **SVG** | Graph export | SVG 1.1 | N/A |
| **Markdown** | Documentation, comments | CommonMark | N/A |

### 5A.4.3 API Versioning Strategy

| Aspect | Specification |
|--------|---------------|
| **Version Format** | Semantic versioning (v1, v2, v3) in URL path |
| **Deprecation Policy** | 6-month notice before version removal |
| **Backward Compatibility** | Maintain previous version for 12 months |
| **Version Header** | Accept `API-Version` header as alternative to URL versioning |
| **Documentation** | Separate docs for each API version |

# 5B. Environment Requirements

## 5B.1 Development Environment

| Component | Specification | Purpose |
|-----------|---------------|---------|
| **Operating System** | macOS Sonoma 14.0+, Ubuntu 22.04+, Windows 10/11 | Local development |
| **Runtime** | Python 3.11+, Node.js 20+ | Application execution |
| **Database** | PostgreSQL 15 (local), Neo4j Desktop 5.x, Redis 7.x (Docker) | Data storage |
| **IDE** | VS Code, PyCharm, WebStorm | Code editing |
| **Version Control** | Git 2.40+, GitHub Desktop (optional) | Source code management |
| **Container Runtime** | Docker Desktop 24.x | Service containerization |
| **Package Managers** | pip 23+, npm 10+, poetry 1.7+ | Dependency management |

## 5B.2 Testing Environment

| Component | Specification | Purpose |
|-----------|---------------|---------|
| **Operating System** | Ubuntu 24.04 LTS (Docker containers) | Consistent test environment |
| **CI/CD Platform** | GitHub Actions | Automated testing |
| **Test Frameworks** | pytest 7.4+, Jest 29+, Playwright 1.40+ | Unit, integration, E2E tests |
| **Test Data** | Faker 20+, Factory Boy 3.3+ | Test data generation |
| **Mock Services** | Wiremock 3.3+, MSW 2.0+ | External service mocking |
| **Coverage Tools** | pytest-cov 4.1+, Istanbul (Jest) | Code coverage measurement |

## 5B.3 Staging Environment

| Component | Specification | Purpose |
|-----------|---------------|---------|
| **Cloud Provider** | AWS (us-east-1 region) | Infrastructure hosting |
| **Compute** | EC2 t3.medium (2 vCPU, 4GB RAM) | Application servers |
| **Database** | RDS PostgreSQL db.t3.medium, Neo4j AuraDB Professional | Data storage |
| **Cache** | ElastiCache Redis cache.t3.micro | Caching layer |
| **Load Balancer** | Application Load Balancer | Traffic distribution |
| **DNS** | Route 53 | Domain management |
| **SSL/TLS** | AWS Certificate Manager | HTTPS encryption |
| **Monitoring** | CloudWatch | Metrics and logs |

## 5B.4 Production Environment

| Component | Specification | Purpose |
|-----------|---------------|---------|
| **Cloud Provider** | AWS (Multi-AZ deployment in us-east-1) | High availability |
| **Compute** | EC2 t3.large (2 vCPU, 8GB RAM), Auto Scaling (2-10 instances) | Application servers |
| **Database** | RDS PostgreSQL db.t3.large (Multi-AZ), Neo4j AuraDB Enterprise | Data storage |
| **Cache** | ElastiCache Redis cache.t3.small (Multi-AZ) | Caching layer |
| **CDN** | CloudFront | Static asset delivery |
| **Load Balancer** | Application Load Balancer (Multi-AZ) | Traffic distribution |
| **DNS** | Route 53 with health checks | Domain management |
| **SSL/TLS** | AWS Certificate Manager with auto-renewal | HTTPS encryption |
| **Monitoring** | CloudWatch + DataDog | Comprehensive monitoring |
| **Backup** | Automated daily backups, 30-day retention | Disaster recovery |

# 5C. Emergency and Fault Handling Requirements

## 5C.1 Error Detection and Reporting

| ID | Requirement | Implementation | Priority |
|----|-------------|----------------|----------|
| EFH-001 | System shall detect and log all errors | Centralized error tracking with Sentry, structured logging with correlation IDs | Critical |
| EFH-002 | System shall categorize errors by severity | Critical (system down), High (feature broken), Medium (degraded), Low (cosmetic) | Critical |
| EFH-003 | System shall alert on-call engineers for critical errors | PagerDuty integration with escalation policy | Critical |
| EFH-004 | System shall provide error context | Stack traces, request IDs, user context, system state | High |

## 5C.2 Fault Tolerance Mechanisms

| Fault Scenario | Detection | Response | Recovery | RTO | RPO |
|----------------|-----------|----------|----------|-----|-----|
| **Database Connection Loss** | Connection timeout (5s) | Retry with exponential backoff (3 attempts) | Automatic reconnection | 30s | 0 |
| **LLM API Failure** | HTTP 5xx or timeout (30s) | Fallback to secondary provider (Claude ↔ GPT-4) | Queue request for retry | 60s | 0 |
| **GitHub API Rate Limit** | HTTP 429 response | Queue requests, respect rate limit headers | Resume after reset | 60min | 0 |
| **Redis Cache Failure** | Connection error | Bypass cache, direct database access | Automatic reconnection | 10s | 0 |
| **Worker Process Crash** | Health check failure | Restart worker, reassign tasks | Automatic restart | 30s | 0 |
| **Database Primary Failure** | Health check failure | Automatic failover to standby (Multi-AZ) | Promote standby to primary | 30s | 1min |

## 5C.3 Graceful Degradation

| Service Unavailable | Degraded Functionality | User Experience | Notification |
|---------------------|------------------------|-----------------|--------------|
| **LLM API** | Code review without AI suggestions, manual review only | Warning banner: "AI suggestions temporarily unavailable" | Email to admins |
| **Neo4j** | Architecture analysis disabled, code review continues | Warning: "Architecture visualization unavailable" | Dashboard alert |
| **GitHub API** | Manual repository sync, webhook queue | Info: "Automatic sync paused, manual sync available" | Status page |
| **Redis** | Slower performance, direct database queries | No visible impact (slight delay) | Internal monitoring alert |

## 5C.4 Emergency Procedures

### 5C.4.1 System Shutdown Procedure
1. **Notification:** Alert all users 15 minutes before shutdown
2. **Queue Drain:** Stop accepting new analysis requests, complete in-progress tasks
3. **Session Preservation:** Save user sessions to database
4. **Graceful Stop:** Terminate services in reverse dependency order
5. **Verification:** Confirm all data persisted, no orphaned transactions

### 5C.4.2 Emergency Rollback Procedure
1. **Trigger:** Critical bug detected in production (P0 severity)
2. **Decision:** Engineering lead approves rollback within 15 minutes
3. **Execution:** Blue-green deployment switch to previous version
4. **Verification:** Health checks pass, error rate returns to baseline
5. **Communication:** Notify users of rollback and issue resolution timeline

### 5C.4.3 Data Corruption Recovery
1. **Detection:** Data integrity check fails or user reports corruption
2. **Isolation:** Identify affected data scope (users, projects, time range)
3. **Restoration:** Restore from most recent clean backup
4. **Validation:** Verify data integrity, run consistency checks
5. **Notification:** Inform affected users of data restoration

## 5C.5 Disaster Recovery Requirements

| Disaster Scenario | RTO | RPO | Recovery Procedure |
|-------------------|-----|-----|--------------------|
| **Complete Region Failure** | 4 hours | 1 hour | Failover to backup region, restore from backups, update DNS |
| **Database Corruption** | 2 hours | 1 hour | Restore from latest backup, replay transaction logs |
| **Ransomware Attack** | 8 hours | 24 hours | Restore from offline backups, security audit, credential rotation |
| **Data Center Outage** | 1 hour | 5 minutes | Multi-AZ failover (automatic), verify service health |

# 6. Specific Requirements (Use Cases)

## 6.1 Use Case Diagram

### 6.1.1 Feature 1 

![IMG_256](media/image1.png){width="6.5465277777777775in" height="2.0416666666666665in"}

### 6.1.2 Feature 2 

![IMG_256](media/image2.png){width="6.5625in" height="3.7840277777777778in"}

### 6.1.3 Feature 3 

![IMG_256](media/image3.png){width="6.520833333333333in" height="3.2527777777777778in"}

### 6.1.4 Feature 4 

![IMG_256](media/image4.png){width="6.541666666666667in" height="7.766666666666667in"}

## 6.2 Use Case Descriptions

**UC-01 User Registration**

+----------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------+----------------------------------------------------------------+----------------------+
| **Use Case ID**                  |                                                                                                                                                            | **UC-01**                                                                                  |                                                                |                      |
+----------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------+----------------------------------------------------------------+----------------------+
| **Use Case Name**                |                                                                                                                                                            | **User Registration**                                                                      |                                                                |                      |
+----------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------+----------------------------------------------------------------+----------------------+
| **Created By**                   | **BaiXuan Zhang**                                                                                                                                          | **Last Update By**                                                                         |                                                                | **BaiXuan Zhang**    |
+----------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------+----------------------------------------------------------------+----------------------+
| **Date Created**                 | **07/02/2026**                                                                                                                                             | **Last Revision Date**                                                                     |                                                                | **07/02/2026**       |
+----------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------+----------------------------------------------------------------+----------------------+
| **Actors**                       | **Guest**                                                                                                                                                  |                                                                                            |                                                                |                      |
+----------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------+----------------------------------------------------------------+----------------------+
| **Description**                  | **Allows a guest user to create a new account on the AI-Based Reviewer platform to access code review and architecture analysis features.**                |                                                                                            |                                                                |                      |
+----------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------+----------------------------------------------------------------+----------------------+
| **Trigger**                      | **Guest clicks the \'Register\' button on the landing page.**                                                                                              |                                                                                            |                                                                |                      |
+----------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------+----------------------------------------------------------------+----------------------+
| **Preconditions**                | **1. Guest is on the registration page.**                                                                                                                  |                                                                                            |                                                                |                      |
|                                  |                                                                                                                                                            |                                                                                            |                                                                |                      |
|                                  | **2. Guest has a valid email address.**                                                                                                                    |                                                                                            |                                                                |                      |
+----------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------+----------------------------------------------------------------+----------------------+
| **Use Case Input Specification** |                                                                                                                                                            |                                                                                            |                                                                |                      |
+----------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------+----------------------------------------------------------------+----------------------+
| **Input**                        | **Type**                                                                                                                                                   | **Constraint**                                                                             |                                                                | **Example**          |
+----------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------+----------------------------------------------------------------+----------------------+
| **Username**                     | **String**                                                                                                                                                 | **3-30 characters, alphanumeric and underscore only**                                      |                                                                | **john_dev123**      |
+----------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------+----------------------------------------------------------------+----------------------+
| **Email**                        | **Email**                                                                                                                                                  | **Valid email format**                                                                     |                                                                | **john@example.com** |
+----------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------+----------------------------------------------------------------+----------------------+
| **Password**                     | **String**                                                                                                                                                 | **Minimum 8 characters, must contain uppercase, lowercase, number, and special character** |                                                                | **SecurePass@123**   |
+----------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------+----------------------------------------------------------------+----------------------+
| **Postconditions**               | **New user account is created in the database, confirmation email is sent, and guest is redirected to login page.**                                        |                                                                                            |                                                                |                      |
+----------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------+----------------------------------------------------------------+----------------------+
| **Normal Flows**                 | **User**                                                                                                                                                   |                                                                                            | **System**                                                     |                      |
+----------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------+----------------------------------------------------------------+----------------------+
|                                  | **2. User enters username, email, and password.**                                                                                                          |                                                                                            | **1. System displays registration form.**                      |                      |
|                                  |                                                                                                                                                            |                                                                                            |                                                                |                      |
|                                  | **4. User clicks \'Register\' button.**                                                                                                                    |                                                                                            | **3. System validates input format in real-time.**             |                      |
|                                  |                                                                                                                                                            |                                                                                            |                                                                |                      |
|                                  |                                                                                                                                                            |                                                                                            | **5. System checks for duplicate username/email.**             |                      |
|                                  |                                                                                                                                                            |                                                                                            |                                                                |                      |
|                                  |                                                                                                                                                            |                                                                                            | **6. System encrypts password using bcrypt.**                  |                      |
|                                  |                                                                                                                                                            |                                                                                            |                                                                |                      |
|                                  |                                                                                                                                                            |                                                                                            | **7. System creates user record in PostgreSQL.**               |                      |
|                                  |                                                                                                                                                            |                                                                                            |                                                                |                      |
|                                  |                                                                                                                                                            |                                                                                            | **8. System sends confirmation email.**                        |                      |
|                                  |                                                                                                                                                            |                                                                                            |                                                                |                      |
|                                  |                                                                                                                                                            |                                                                                            | **9. System displays success message and redirects to login.** |                      |
+----------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------+----------------------------------------------------------------+----------------------+
| **Alternative Flow**             | **3A. If username/email already exists: System displays error message \'Username/Email already taken\' and prompts user to choose different credentials.** |                                                                                            |                                                                |                      |
+----------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------+----------------------------------------------------------------+----------------------+
| **Exception Flow**               | **E1. If password does not meet complexity requirements: System displays specific validation errors.**                                                     |                                                                                            |                                                                |                      |
|                                  |                                                                                                                                                            |                                                                                            |                                                                |                      |
|                                  | **E2. If email service is unavailable: System creates account but flags for manual email verification.**                                                   |                                                                                            |                                                                |                      |
+----------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------+----------------------------------------------------------------+----------------------+
| **Note**                         | **Passwords are hashed using bcrypt with salt rounds of 12.**                                                                                              |                                                                                            |                                                                |                      |
+----------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------+----------------------------------------------------------------+----------------------+

**UC-02: User Login**

+----------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------------------+-----------------------------------------------------------+----------------------+
| **Use Case ID**                  |                                                                                                                                                              | **UC-02**                             |                                                           |                      |
+----------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------------------+-----------------------------------------------------------+----------------------+
| **Use Case Name**                |                                                                                                                                                              | **User Login**                        |                                                           |                      |
+----------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------------------+-----------------------------------------------------------+----------------------+
| **Created By**                   | **BaiXuan Zhang**                                                                                                                                            | **Last Update By**                    |                                                           | **BaiXuan Zhang**    |
+----------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------------------+-----------------------------------------------------------+----------------------+
| **Date Created**                 | **07/02/2026**                                                                                                                                               | **Last Revision Date**                |                                                           | **07/02/2026**       |
+----------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------------------+-----------------------------------------------------------+----------------------+
| **Actors**                       | **Guest, User**                                                                                                                                              |                                       |                                                           |                      |
+----------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------------------+-----------------------------------------------------------+----------------------+
| **Description**                  | **Allows a guest to authenticate and access the AI-Based Reviewer platform using valid credentials.**                                                        |                                       |                                                           |                      |
+----------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------------------+-----------------------------------------------------------+----------------------+
| **Trigger**                      | **Guest clicks the \'Login\' button on the landing page or navigates to the login URL.**                                                                     |                                       |                                                           |                      |
+----------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------------------+-----------------------------------------------------------+----------------------+
| **Preconditions**                | **1. User has already registered an account.**                                                                                                               |                                       |                                                           |                      |
|                                  |                                                                                                                                                              |                                       |                                                           |                      |
|                                  | **2. Guest is on the login page.**                                                                                                                           |                                       |                                                           |                      |
|                                  |                                                                                                                                                              |                                       |                                                           |                      |
|                                  | **3. User is not currently logged in.**                                                                                                                      |                                       |                                                           |                      |
+----------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------------------+-----------------------------------------------------------+----------------------+
| **Use Case Input Specification** |                                                                                                                                                              |                                       |                                                           |                      |
+----------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------------------+-----------------------------------------------------------+----------------------+
| **Input**                        | **Type**                                                                                                                                                     | **Constraint**                        |                                                           | **Example**          |
+----------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------------------+-----------------------------------------------------------+----------------------+
| **Email or Username**            | **String**                                                                                                                                                   | **Must match registered account**     |                                                           | **john@example.com** |
+----------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------------------+-----------------------------------------------------------+----------------------+
| **Password**                     | **String**                                                                                                                                                   | **Must match stored hashed password** |                                                           | **SecurePass@123**   |
+----------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------------------+-----------------------------------------------------------+----------------------+
| **Postconditions**               | **User is authenticated, JWT token is generated and stored, user is redirected to dashboard with active session.**                                           |                                       |                                                           |                      |
+----------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------------------+-----------------------------------------------------------+----------------------+
| **Normal Flows**                 | **User**                                                                                                                                                     |                                       | **System**                                                |                      |
+----------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------------------+-----------------------------------------------------------+----------------------+
|                                  | **2. User enters email/username.**                                                                                                                           |                                       | **1. System displays login form.**                        |                      |
|                                  |                                                                                                                                                              |                                       |                                                           |                      |
|                                  | **4. User enters password.**                                                                                                                                 |                                       | **3. System validates email/username format.**            |                      |
|                                  |                                                                                                                                                              |                                       |                                                           |                      |
|                                  | **6. User clicks \'Login\' button.**                                                                                                                         |                                       | **5. System masks password input.**                       |                      |
|                                  |                                                                                                                                                              |                                       |                                                           |                      |
|                                  |                                                                                                                                                              |                                       | **7. System validates credentials against database.**     |                      |
|                                  |                                                                                                                                                              |                                       |                                                           |                      |
|                                  |                                                                                                                                                              |                                       | **8. System retrieves user record from PostgreSQL.**      |                      |
|                                  |                                                                                                                                                              |                                       |                                                           |                      |
|                                  |                                                                                                                                                              |                                       | **9. System verifies password using bcrypt comparison.**  |                      |
|                                  |                                                                                                                                                              |                                       |                                                           |                      |
|                                  |                                                                                                                                                              |                                       | **10. System generates JWT token with user_id and role.** |                      |
|                                  |                                                                                                                                                              |                                       |                                                           |                      |
|                                  |                                                                                                                                                              |                                       | **11. System sets token expiration (24 hours).**          |                      |
|                                  |                                                                                                                                                              |                                       |                                                           |                      |
|                                  |                                                                                                                                                              |                                       | **12. System returns token to client.**                   |                      |
|                                  |                                                                                                                                                              |                                       |                                                           |                      |
|                                  |                                                                                                                                                              |                                       | **13. System redirects to dashboard.**                    |                      |
|                                  |                                                                                                                                                              |                                       |                                                           |                      |
|                                  |                                                                                                                                                              |                                       | **14. System logs successful login event.**               |                      |
+----------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------------------+-----------------------------------------------------------+----------------------+
| **Alternative Flow**             | **7A. If email/username not found: System displays error \'Invalid credentials\' without revealing which field is incorrect (security best practice).**      |                                       |                                                           |                      |
|                                  |                                                                                                                                                              |                                       |                                                           |                      |
|                                  | **9A. If password is incorrect: System displays error \'Invalid credentials\' and increments failed login counter.**                                         |                                       |                                                           |                      |
|                                  |                                                                                                                                                              |                                       |                                                           |                      |
|                                  | **9B. If account is locked (after 5 failed attempts): System displays \'Account locked. Please reset password or contact support.\'**                        |                                       |                                                           |                      |
|                                  |                                                                                                                                                              |                                       |                                                           |                      |
|                                  | **12A. If user selects \'Remember me\': System extends token expiration to 30 days.**                                                                        |                                       |                                                           |                      |
+----------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------------------+-----------------------------------------------------------+----------------------+
| **Exception Flow**               | **E1. If database connection fails: System displays \'Service temporarily unavailable. Please try again later.\'**                                           |                                       |                                                           |                      |
|                                  |                                                                                                                                                              |                                       |                                                           |                      |
|                                  | **E2. If too many concurrent login attempts from same IP: System implements rate limiting and displays \'Too many login attempts. Please wait 5 minutes.\'** |                                       |                                                           |                      |
|                                  |                                                                                                                                                              |                                       |                                                           |                      |
|                                  | **E3. If JWT generation fails: System logs error and displays \'Authentication failed. Please try again.\'**                                                 |                                       |                                                           |                      |
+----------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------------------+-----------------------------------------------------------+----------------------+
| **Note**                         | **Password is never logged or transmitted in plain text. Failed login attempts are logged for security monitoring.**                                         |                                       |                                                           |                      |
+----------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------------------+-----------------------------------------------------------+----------------------+

**UC-03 Add GitHub Repository**

+----------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------+-----------------------------------------------------------------+------------------------------------------------------------------------+----------------------------------------+
| **Use Case ID**                  |                                                                                                                                                             | **UC-03**                                                       |                                                                        |                                        |
+----------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------+-----------------------------------------------------------------+------------------------------------------------------------------------+----------------------------------------+
| **Use Case Name**                |                                                                                                                                                             | **Add GitHub Repository**                                       |                                                                        |                                        |
+----------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------+-----------------------------------------------------------------+------------------------------------------------------------------------+----------------------------------------+
| **Created By**                   | **BaiXuan Zhang**                                                                                                                                           | **Last Update By**                                              |                                                                        | **BaiXuan Zhang**                      |
+----------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------+-----------------------------------------------------------------+------------------------------------------------------------------------+----------------------------------------+
| **Date Created**                 | **07/02/2026**                                                                                                                                              | **Last Revision Date**                                          |                                                                        | **07/02/2026**                         |
+----------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------+-----------------------------------------------------------------+------------------------------------------------------------------------+----------------------------------------+
| **Actors**                       | **Programmer, Manager**                                                                                                                                     |                                                                 |                                                                        |                                        |
+----------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------+-----------------------------------------------------------------+------------------------------------------------------------------------+----------------------------------------+
| **Description**                  | **User connects a GitHub repository to the platform for automated code review and architecture monitoring.**                                                |                                                                 |                                                                        |                                        |
+----------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------+-----------------------------------------------------------------+------------------------------------------------------------------------+----------------------------------------+
| **Trigger**                      | **User clicks \'Add Repository\' button in the project management dashboard.**                                                                              |                                                                 |                                                                        |                                        |
+----------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------+-----------------------------------------------------------------+------------------------------------------------------------------------+----------------------------------------+
| **Preconditions**                | **1. User is authenticated and logged in.**                                                                                                                 |                                                                 |                                                                        |                                        |
|                                  |                                                                                                                                                             |                                                                 |                                                                        |                                        |
|                                  | **2. User has access to the GitHub repository.**                                                                                                            |                                                                 |                                                                        |                                        |
|                                  |                                                                                                                                                             |                                                                 |                                                                        |                                        |
|                                  | **3. GitHub OAuth token is configured (if using private repos).**                                                                                           |                                                                 |                                                                        |                                        |
+----------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------+-----------------------------------------------------------------+------------------------------------------------------------------------+----------------------------------------+
| **Use Case Input Specification** |                                                                                                                                                             |                                                                 |                                                                        |                                        |
+----------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------+-----------------------------------------------------------------+------------------------------------------------------------------------+----------------------------------------+
| **Input**                        | **Type**                                                                                                                                                    | **Constraint**                                                  |                                                                        | **Example**                            |
+----------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------+-----------------------------------------------------------------+------------------------------------------------------------------------+----------------------------------------+
| **Repository URL**               | **URL**                                                                                                                                                     | **Valid GitHub repository URL (https://github.com/owner/repo)** |                                                                        | **https://github.com/user/my-project** |
+----------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------+-----------------------------------------------------------------+------------------------------------------------------------------------+----------------------------------------+
| **Branch**                       | **String**                                                                                                                                                  | **Valid branch name (optional, defaults to \'main\')**          |                                                                        | **develop**                            |
+----------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------+-----------------------------------------------------------------+------------------------------------------------------------------------+----------------------------------------+
| **Webhook Secret**               | **String**                                                                                                                                                  | **Optional secret for webhook security**                        |                                                                        | **webhook_secret_123**                 |
+----------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------+-----------------------------------------------------------------+------------------------------------------------------------------------+----------------------------------------+
| **Postconditions**               | **Repository is added to the system, GitHub webhook is configured, initial repository analysis is queued, and repository appears in user\'s project list.** |                                                                 |                                                                        |                                        |
+----------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------+-----------------------------------------------------------------+------------------------------------------------------------------------+----------------------------------------+
| **Normal Flows**                 | **User**                                                                                                                                                    |                                                                 | **System**                                                             |                                        |
+----------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------+-----------------------------------------------------------------+------------------------------------------------------------------------+----------------------------------------+
|                                  | **2. User enters GitHub repository URL.**                                                                                                                   |                                                                 | **1. System displays \'Add Repository\' form.**                        |                                        |
|                                  |                                                                                                                                                             |                                                                 |                                                                        |                                        |
|                                  | **4. User optionally specifies target branch.**                                                                                                             |                                                                 | **3. System validates URL format.**                                    |                                        |
|                                  |                                                                                                                                                             |                                                                 |                                                                        |                                        |
|                                  | **6. User clicks \'Connect Repository\' button.**                                                                                                           |                                                                 | **5. System checks repository accessibility via GitHub API.**          |                                        |
|                                  |                                                                                                                                                             |                                                                 |                                                                        |                                        |
|                                  |                                                                                                                                                             |                                                                 | **7. System creates webhook on GitHub repository for PR events.**      |                                        |
|                                  |                                                                                                                                                             |                                                                 |                                                                        |                                        |
|                                  |                                                                                                                                                             |                                                                 | **8. System clones repository to temporary storage.**                  |                                        |
|                                  |                                                                                                                                                             |                                                                 |                                                                        |                                        |
|                                  |                                                                                                                                                             |                                                                 | **9. System initializes AST parsing and dependency graph extraction.** |                                        |
|                                  |                                                                                                                                                             |                                                                 |                                                                        |                                        |
|                                  |                                                                                                                                                             |                                                                 | **10. System stores repository metadata in PostgreSQL.**               |                                        |
|                                  |                                                                                                                                                             |                                                                 |                                                                        |                                        |
|                                  |                                                                                                                                                             |                                                                 | **11. System queues initial analysis task in Redis.**                  |                                        |
|                                  |                                                                                                                                                             |                                                                 |                                                                        |                                        |
|                                  |                                                                                                                                                             |                                                                 | **12. System displays success notification with repository ID.**       |                                        |
+----------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------+-----------------------------------------------------------------+------------------------------------------------------------------------+----------------------------------------+
| **Alternative Flow**             | **5A. If repository is private and OAuth token is not configured: System prompts user to authenticate with GitHub OAuth.**                                  |                                                                 |                                                                        |                                        |
|                                  |                                                                                                                                                             |                                                                 |                                                                        |                                        |
|                                  | **7A. If webhook creation fails: System logs error but still allows manual PR analysis via URL submission.**                                                |                                                                 |                                                                        |                                        |
+----------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------+-----------------------------------------------------------------+------------------------------------------------------------------------+----------------------------------------+
| **Exception Flow**               | **E1. If repository URL is invalid or inaccessible: System displays error \'Cannot access repository. Check URL and permissions.\'**                        |                                                                 |                                                                        |                                        |
|                                  |                                                                                                                                                             |                                                                 |                                                                        |                                        |
|                                  | **E2. If repository is too large (\>1GB): System displays warning and asks for user confirmation to proceed.**                                              |                                                                 |                                                                        |                                        |
|                                  |                                                                                                                                                             |                                                                 |                                                                        |                                        |
|                                  | **E3. If GitHub API rate limit is exceeded: System queues request for retry after cooldown period.**                                                        |                                                                 |                                                                        |                                        |
+----------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------+-----------------------------------------------------------------+------------------------------------------------------------------------+----------------------------------------+
| **Note**                         | **Webhook events: pull_request (opened, synchronize, reopened). Initial analysis may take 8-50 seconds depending on repository size.**                      |                                                                 |                                                                        |                                        |
+----------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------+-----------------------------------------------------------------+------------------------------------------------------------------------+----------------------------------------+

**UC-04 Submit Pull Request for Review**

+----------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------+------------------------------------------------------------+--------------------------------------------------------------------------+-------------------------------------------------+
| **Use Case ID**                  |                                                                                                                                                           | **UC-04**                                                  |                                                                          |                                                 |
+----------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------+------------------------------------------------------------+--------------------------------------------------------------------------+-------------------------------------------------+
| **Use Case Name**                |                                                                                                                                                           | **Submit Pull Request for Review**                         |                                                                          |                                                 |
+----------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------+------------------------------------------------------------+--------------------------------------------------------------------------+-------------------------------------------------+
| **Created By**                   | **BaiXuan Zhang**                                                                                                                                         | **Last Update By**                                         |                                                                          | **BaiXuan Zhang**                               |
+----------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------+------------------------------------------------------------+--------------------------------------------------------------------------+-------------------------------------------------+
| **Date Created**                 | **07/02/2026**                                                                                                                                            | **Last Revision Date**                                     |                                                                          | **07/02/2026**                                  |
+----------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------+------------------------------------------------------------+--------------------------------------------------------------------------+-------------------------------------------------+
| **Actors**                       | **Programmer**                                                                                                                                            |                                                            |                                                                          |                                                 |
+----------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------+------------------------------------------------------------+--------------------------------------------------------------------------+-------------------------------------------------+
| **Description**                  | **Programmer creates a pull request on GitHub, triggering automated AI-based code review and architectural analysis.**                                    |                                                            |                                                                          |                                                 |
+----------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------+------------------------------------------------------------+--------------------------------------------------------------------------+-------------------------------------------------+
| **Trigger**                      | **Programmer creates or updates a pull request in a connected GitHub repository.**                                                                        |                                                            |                                                                          |                                                 |
+----------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------+------------------------------------------------------------+--------------------------------------------------------------------------+-------------------------------------------------+
| **Preconditions**                | **1. Repository is connected to the platform with active webhook.**                                                                                       |                                                            |                                                                          |                                                 |
|                                  |                                                                                                                                                           |                                                            |                                                                          |                                                 |
|                                  | **2. Pull request contains code changes.**                                                                                                                |                                                            |                                                                          |                                                 |
|                                  |                                                                                                                                                           |                                                            |                                                                          |                                                 |
|                                  | **3. LLM API is available and configured.**                                                                                                               |                                                            |                                                                          |                                                 |
+----------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------+------------------------------------------------------------+--------------------------------------------------------------------------+-------------------------------------------------+
| **Use Case Input Specification** |                                                                                                                                                           |                                                            |                                                                          |                                                 |
+----------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------+------------------------------------------------------------+--------------------------------------------------------------------------+-------------------------------------------------+
| **Input**                        | **Type**                                                                                                                                                  | **Constraint**                                             |                                                                          | **Example**                                     |
+----------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------+------------------------------------------------------------+--------------------------------------------------------------------------+-------------------------------------------------+
| **Pull Request Event**           | **JSON**                                                                                                                                                  | **GitHub webhook payload containing PR metadata and diff** |                                                                          | **{ pr_number: 42, action: \'opened\', \... }** |
+----------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------+------------------------------------------------------------+--------------------------------------------------------------------------+-------------------------------------------------+
| **Code Diff**                    | **Text**                                                                                                                                                  | **Git diff format showing changes**                        |                                                                          | **+console.log(\'new feature\');**              |
+----------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------+------------------------------------------------------------+--------------------------------------------------------------------------+-------------------------------------------------+
| **Postconditions**               | **Code review results are posted as comments on GitHub PR, analysis data is stored in database, and architectural changes are reflected in Neo4j graph.** |                                                            |                                                                          |                                                 |
+----------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------+------------------------------------------------------------+--------------------------------------------------------------------------+-------------------------------------------------+
| **Normal Flows**                 | **User**                                                                                                                                                  |                                                            | **System**                                                               |                                                 |
+----------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------+------------------------------------------------------------+--------------------------------------------------------------------------+-------------------------------------------------+
|                                  | **1. Programmer creates pull request on GitHub.**                                                                                                         |                                                            | **2. GitHub webhook triggers platform endpoint.**                        |                                                 |
|                                  |                                                                                                                                                           |                                                            |                                                                          |                                                 |
|                                  | **8. Programmer views AI review comments on GitHub PR.**                                                                                                  |                                                            | **3. System extracts PR metadata and code diff.**                        |                                                 |
|                                  |                                                                                                                                                           |                                                            |                                                                          |                                                 |
|                                  |                                                                                                                                                           |                                                            | **4. System generates AST for changed files.**                           |                                                 |
|                                  |                                                                                                                                                           |                                                            |                                                                          |                                                 |
|                                  |                                                                                                                                                           |                                                            | **5. System queries Neo4j for architectural context.**                   |                                                 |
|                                  |                                                                                                                                                           |                                                            |                                                                          |                                                 |
|                                  |                                                                                                                                                           |                                                            | **6. System sends code + context to LLM for analysis.**                  |                                                 |
|                                  |                                                                                                                                                           |                                                            |                                                                          |                                                 |
|                                  |                                                                                                                                                           |                                                            | **7. System receives LLM analysis results.**                             |                                                 |
|                                  |                                                                                                                                                           |                                                            |                                                                          |                                                 |
|                                  |                                                                                                                                                           |                                                            | **9. System categorizes issues by severity (Critical/High/Medium/Low).** |                                                 |
|                                  |                                                                                                                                                           |                                                            |                                                                          |                                                 |
|                                  |                                                                                                                                                           |                                                            | **10. System checks for security vulnerabilities (OWASP Top 10).**       |                                                 |
|                                  |                                                                                                                                                           |                                                            |                                                                          |                                                 |
|                                  |                                                                                                                                                           |                                                            | **11. System verifies compliance with ISO/IEC 25010 and ISO/IEC 23396.** |                                                 |
|                                  |                                                                                                                                                           |                                                            |                                                                          |                                                 |
|                                  |                                                                                                                                                           |                                                            | **12. System posts formatted review comments to GitHub PR via API.**     |                                                 |
|                                  |                                                                                                                                                           |                                                            |                                                                          |                                                 |
|                                  |                                                                                                                                                           |                                                            | **13. System updates dependency graph in Neo4j.**                        |                                                 |
|                                  |                                                                                                                                                           |                                                            |                                                                          |                                                 |
|                                  |                                                                                                                                                           |                                                            | **14. System stores analysis results in PostgreSQL.**                    |                                                 |
|                                  |                                                                                                                                                           |                                                            |                                                                          |                                                 |
|                                  |                                                                                                                                                           |                                                            | **15. System sends notification email if critical issues found.**        |                                                 |
+----------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------+------------------------------------------------------------+--------------------------------------------------------------------------+-------------------------------------------------+
| **Alternative Flow**             | **6A. If LLM API timeout occurs: System retries up to 3 times with exponential backoff.**                                                                 |                                                            |                                                                          |                                                 |
|                                  |                                                                                                                                                           |                                                            |                                                                          |                                                 |
|                                  | **12A. If GitHub API fails to post comment: System stores review results internally and flags for manual posting.**                                       |                                                            |                                                                          |                                                 |
+----------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------+------------------------------------------------------------+--------------------------------------------------------------------------+-------------------------------------------------+
| **Exception Flow**               | **E1. If code diff is too large (\>10,000 lines): System splits analysis into chunks and aggregates results.**                                            |                                                            |                                                                          |                                                 |
|                                  |                                                                                                                                                           |                                                            |                                                                          |                                                 |
|                                  | **E2. If LLM API returns error: System falls back to rule-based static analysis and logs error for investigation.**                                       |                                                            |                                                                          |                                                 |
|                                  |                                                                                                                                                           |                                                            |                                                                          |                                                 |
|                                  | **E3. If architectural drift detection fails: System proceeds with code review only and logs graph database error.**                                      |                                                            |                                                                          |                                                 |
+----------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------+------------------------------------------------------------+--------------------------------------------------------------------------+-------------------------------------------------+
| **Note**                         | **Analysis time: 8-50 seconds depending on PR size and complexity. LLM models: GPT-4 or Claude 3.5 Sonnet.**                                              |                                                            |                                                                          |                                                 |
+----------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------+------------------------------------------------------------+--------------------------------------------------------------------------+-------------------------------------------------+

**UC-05 View Architecture Analysis**

+----------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------------------------------------+---------------------------------------------------------------------------------------------------+------------------------------+
| **Use Case ID**                  |                                                                                                                                                                | **UC-05**                                               |                                                                                                   |                              |
+----------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------------------------------------+---------------------------------------------------------------------------------------------------+------------------------------+
| **Use Case Name**                |                                                                                                                                                                | **View Architecture Analysis**                          |                                                                                                   |                              |
+----------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------------------------------------+---------------------------------------------------------------------------------------------------+------------------------------+
| **Created By**                   | **BaiXuan Zhang**                                                                                                                                              | **Last Update By**                                      |                                                                                                   | **BaiXuan Zhang**            |
+----------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------------------------------------+---------------------------------------------------------------------------------------------------+------------------------------+
| **Date Created**                 | **07/02/2026**                                                                                                                                                 | **Last Revision Date**                                  |                                                                                                   | **07/02/2026**               |
+----------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------------------------------------+---------------------------------------------------------------------------------------------------+------------------------------+
| **Actors**                       | **Reviewer, Manager, Programmer**                                                                                                                              |                                                         |                                                                                                   |                              |
+----------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------------------------------------+---------------------------------------------------------------------------------------------------+------------------------------+
| **Description**                  | **User views interactive dependency graph and architecture evolution to understand project structure and detect architectural drift.**                         |                                                         |                                                                                                   |                              |
+----------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------------------------------------+---------------------------------------------------------------------------------------------------+------------------------------+
| **Trigger**                      | **User navigates to \'Architecture\' tab in project dashboard.**                                                                                               |                                                         |                                                                                                   |                              |
+----------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------------------------------------+---------------------------------------------------------------------------------------------------+------------------------------+
| **Preconditions**                | **1. User is authenticated and has access to the project.**                                                                                                    |                                                         |                                                                                                   |                              |
|                                  |                                                                                                                                                                |                                                         |                                                                                                   |                              |
|                                  | **2. Repository has been analyzed at least once.**                                                                                                             |                                                         |                                                                                                   |                              |
|                                  |                                                                                                                                                                |                                                         |                                                                                                   |                              |
|                                  | **3. Dependency graph data exists in Neo4j database.**                                                                                                         |                                                         |                                                                                                   |                              |
+----------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------------------------------------+---------------------------------------------------------------------------------------------------+------------------------------+
| **Use Case Input Specification** |                                                                                                                                                                |                                                         |                                                                                                   |                              |
+----------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------------------------------------+---------------------------------------------------------------------------------------------------+------------------------------+
| **Input**                        | **Type**                                                                                                                                                       | **Constraint**                                          |                                                                                                   | **Example**                  |
+----------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------------------------------------+---------------------------------------------------------------------------------------------------+------------------------------+
| **Project ID**                   | **Integer**                                                                                                                                                    | **Valid project identifier**                            |                                                                                                   | **12345**                    |
+----------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------------------------------------+---------------------------------------------------------------------------------------------------+------------------------------+
| **View Filter**                  | **Enum**                                                                                                                                                       | **Options: All, Services, Modules, Classes, Functions** |                                                                                                   | **Services**                 |
+----------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------------------------------------+---------------------------------------------------------------------------------------------------+------------------------------+
| **Time Range**                   | **Date Range**                                                                                                                                                 | **Optional date range for evolution view**              |                                                                                                   | **2025-01-01 to 2026-02-07** |
+----------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------------------------------------+---------------------------------------------------------------------------------------------------+------------------------------+
| **Postconditions**               | **User sees interactive graph visualization with ability to zoom, filter, and export. Architectural issues are highlighted.**                                  |                                                         |                                                                                                   |                              |
+----------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------------------------------------+---------------------------------------------------------------------------------------------------+------------------------------+
| **Normal Flows**                 | **User**                                                                                                                                                       |                                                         | **System**                                                                                        |                              |
+----------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------------------------------------+---------------------------------------------------------------------------------------------------+------------------------------+
|                                  | **2. User selects project from project list.**                                                                                                                 |                                                         | **1. System displays project dashboard.**                                                         |                              |
|                                  |                                                                                                                                                                |                                                         |                                                                                                   |                              |
|                                  | **4. User clicks \'Architecture\' tab.**                                                                                                                       |                                                         | **3. System loads project metadata from PostgreSQL.**                                             |                              |
|                                  |                                                                                                                                                                |                                                         |                                                                                                   |                              |
|                                  | **6. User applies filters (e.g., view by service).**                                                                                                           |                                                         | **5. System queries Neo4j for dependency graph data.**                                            |                              |
|                                  |                                                                                                                                                                |                                                         |                                                                                                   |                              |
|                                  | **9. User clicks on nodes to view details.**                                                                                                                   |                                                         | **7. System renders interactive graph using D3.js/Cytoscape.**                                    |                              |
|                                  |                                                                                                                                                                |                                                         |                                                                                                   |                              |
|                                  | **11. User exports graph as PNG/SVG.**                                                                                                                         |                                                         | **8. System highlights circular dependencies in red.**                                            |                              |
|                                  |                                                                                                                                                                |                                                         |                                                                                                   |                              |
|                                  |                                                                                                                                                                |                                                         | **10. System displays node details panel showing dependencies, metrics, and historical changes.** |                              |
|                                  |                                                                                                                                                                |                                                         |                                                                                                   |                              |
|                                  |                                                                                                                                                                |                                                         | **12. System generates graph image file.**                                                        |                              |
|                                  |                                                                                                                                                                |                                                         |                                                                                                   |                              |
|                                  |                                                                                                                                                                |                                                         | **13. System provides download link.**                                                            |                              |
+----------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------------------------------------+---------------------------------------------------------------------------------------------------+------------------------------+
| **Alternative Flow**             | **5A. If no graph data exists: System displays message \'No architecture data available. Trigger initial analysis.\' with button to start analysis.**          |                                                         |                                                                                                   |                              |
|                                  |                                                                                                                                                                |                                                         |                                                                                                   |                              |
|                                  | **8A. If user enables \'Evolution View\': System displays timeline slider showing graph changes over selected time range.**                                    |                                                         |                                                                                                   |                              |
+----------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------------------------------------+---------------------------------------------------------------------------------------------------+------------------------------+
| **Exception Flow**               | **E1. If graph is too large to render (\>5000 nodes): System offers clustered view by default and warns about performance.**                                   |                                                         |                                                                                                   |                              |
|                                  |                                                                                                                                                                |                                                         |                                                                                                   |                              |
|                                  | **E2. If Neo4j query times out: System displays cached graph data with timestamp indicating staleness.**                                                       |                                                         |                                                                                                   |                              |
|                                  |                                                                                                                                                                |                                                         |                                                                                                   |                              |
|                                  | **E3. If export fails: System displays error and suggests reducing graph complexity via filters.**                                                             |                                                         |                                                                                                   |                              |
+----------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------------------------------------+---------------------------------------------------------------------------------------------------+------------------------------+
| **Note**                         | **Graph visualization uses force-directed layout. Color coding: Green=healthy, Yellow=moderate coupling, Red=circular dependency or architectural violation.** |                                                         |                                                                                                   |                              |
+----------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------------------------------------+---------------------------------------------------------------------------------------------------+------------------------------+

**UC-06 Monitor Code Quality Metrics**

+----------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------+----------------------------------------------------------------------------------------------------------------------+------------------------------+
| **Use Case ID**                  |                                                                                                                                                        | **UC-06**                                  |                                                                                                                      |                              |
+----------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------+----------------------------------------------------------------------------------------------------------------------+------------------------------+
| **Use Case Name**                |                                                                                                                                                        | **Monitor Code Quality Metrics**           |                                                                                                                      |                              |
+----------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------+----------------------------------------------------------------------------------------------------------------------+------------------------------+
| **Created By**                   | **BaiXuan Zhang**                                                                                                                                      | **Last Update By**                         |                                                                                                                      | **BaiXuan Zhang**            |
+----------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------+----------------------------------------------------------------------------------------------------------------------+------------------------------+
| **Date Created**                 | **07/02/2026**                                                                                                                                         | **Last Revision Date**                     |                                                                                                                      | **07/02/2026**               |
+----------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------+----------------------------------------------------------------------------------------------------------------------+------------------------------+
| **Actors**                       | **Manager, Reviewer**                                                                                                                                  |                                            |                                                                                                                      |                              |
+----------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------+----------------------------------------------------------------------------------------------------------------------+------------------------------+
| **Description**                  | **Manager views comprehensive dashboard showing code quality trends, defect density, compliance status, and team performance metrics.**                |                                            |                                                                                                                      |                              |
+----------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------+----------------------------------------------------------------------------------------------------------------------+------------------------------+
| **Trigger**                      | **Manager navigates to \'Metrics\' or \'Dashboard\' section.**                                                                                         |                                            |                                                                                                                      |                              |
+----------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------+----------------------------------------------------------------------------------------------------------------------+------------------------------+
| **Preconditions**                | **1. Manager is authenticated with appropriate role permissions.**                                                                                     |                                            |                                                                                                                      |                              |
|                                  |                                                                                                                                                        |                                            |                                                                                                                      |                              |
|                                  | **2. At least one repository has been analyzed.**                                                                                                      |                                            |                                                                                                                      |                              |
|                                  |                                                                                                                                                        |                                            |                                                                                                                      |                              |
|                                  | **3. Historical analysis data exists in PostgreSQL.**                                                                                                  |                                            |                                                                                                                      |                              |
+----------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------+----------------------------------------------------------------------------------------------------------------------+------------------------------+
| **Use Case Input Specification** |                                                                                                                                                        |                                            |                                                                                                                      |                              |
+----------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------+----------------------------------------------------------------------------------------------------------------------+------------------------------+
| **Input**                        | **Type**                                                                                                                                               | **Constraint**                             |                                                                                                                      | **Example**                  |
+----------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------+----------------------------------------------------------------------------------------------------------------------+------------------------------+
| **Date Range**                   | **Date Range**                                                                                                                                         | **Start and end dates for metrics period** |                                                                                                                      | **2025-12-01 to 2026-02-07** |
+----------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------+----------------------------------------------------------------------------------------------------------------------+------------------------------+
| **Repository Filter**            | **Array**                                                                                                                                              | **List of repository IDs (optional)**      |                                                                                                                      | **\[101, 102, 105\]**        |
+----------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------+----------------------------------------------------------------------------------------------------------------------+------------------------------+
| **Team Filter**                  | **String**                                                                                                                                             | **Team name or developer username**        |                                                                                                                      | **frontend-team**            |
+----------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------+----------------------------------------------------------------------------------------------------------------------+------------------------------+
| **Postconditions**               | **Manager sees visual charts and tables with metrics, can drill down into specific issues, and can export reports.**                                   |                                            |                                                                                                                      |                              |
+----------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------+----------------------------------------------------------------------------------------------------------------------+------------------------------+
| **Normal Flows**                 | **User**                                                                                                                                               |                                            | **System**                                                                                                           |                              |
+----------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------+----------------------------------------------------------------------------------------------------------------------+------------------------------+
|                                  | **2. Manager selects date range using date picker.**                                                                                                   |                                            | **1. System displays metrics dashboard.**                                                                            |                              |
|                                  |                                                                                                                                                        |                                            |                                                                                                                      |                              |
|                                  | **4. Manager optionally filters by repository or team.**                                                                                               |                                            | **3. System queries PostgreSQL for analysis history.**                                                               |                              |
|                                  |                                                                                                                                                        |                                            |                                                                                                                      |                              |
|                                  | **7. Manager clicks on specific metric to view details.**                                                                                              |                                            | **5. System aggregates data by time period.**                                                                        |                              |
|                                  |                                                                                                                                                        |                                            |                                                                                                                      |                              |
|                                  | **10. Manager exports report as PDF/CSV.**                                                                                                             |                                            | **6. System renders charts: line graphs (trends), bar charts (defects by severity), pie charts (issue categories).** |                              |
|                                  |                                                                                                                                                        |                                            |                                                                                                                      |                              |
|                                  |                                                                                                                                                        |                                            | **8. System displays drill-down view with list of specific issues.**                                                 |                              |
|                                  |                                                                                                                                                        |                                            |                                                                                                                      |                              |
|                                  |                                                                                                                                                        |                                            | **9. System calculates KPIs: defect density, MTTR, code churn, architectural health score.**                         |                              |
|                                  |                                                                                                                                                        |                                            |                                                                                                                      |                              |
|                                  |                                                                                                                                                        |                                            | **11. System generates report document.**                                                                            |                              |
|                                  |                                                                                                                                                        |                                            |                                                                                                                      |                              |
|                                  |                                                                                                                                                        |                                            | **12. System provides download link.**                                                                               |                              |
+----------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------+----------------------------------------------------------------------------------------------------------------------+------------------------------+
| **Alternative Flow**             | **6A. If no data exists for selected period: System displays message \'No analysis data found for this period\' and suggests expanding date range.**   |                                            |                                                                                                                      |                              |
|                                  |                                                                                                                                                        |                                            |                                                                                                                      |                              |
|                                  | **9A. If user requests compliance report: System generates detailed compliance matrix showing ISO/IEC 25010 and ISO/IEC 23396 conformance by module.** |                                            |                                                                                                                      |                              |
+----------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------+----------------------------------------------------------------------------------------------------------------------+------------------------------+
| **Exception Flow**               | **E1. If database query is slow (\>5 seconds): System displays loading indicator and fetches data asynchronously.**                                    |                                            |                                                                                                                      |                              |
|                                  |                                                                                                                                                        |                                            |                                                                                                                      |                              |
|                                  | **E2. If export fails due to large dataset: System offers to email report when ready.**                                                                |                                            |                                                                                                                      |                              |
|                                  |                                                                                                                                                        |                                            |                                                                                                                      |                              |
|                                  | **E3. If calculated metrics show anomalies: System flags outliers and suggests data verification.**                                                    |                                            |                                                                                                                      |                              |
+----------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------+----------------------------------------------------------------------------------------------------------------------+------------------------------+
| **Note**                         | **Metrics updated in real-time as new PRs are analyzed. Charts are interactive with tooltips and clickable elements.**                                 |                                            |                                                                                                                      |                              |
+----------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------------------------+----------------------------------------------------------------------------------------------------------------------+------------------------------+

**UC-07 Configure Analysis Settings**

+----------------------------------+--------------------------------------------------------------------------------------------------------------------------+------------------------------------------------+---------------------------------------------------------------+---------------------------------------------+
| **Use Case ID**                  |                                                                                                                          | **UC-07**                                      |                                                               |                                             |
+----------------------------------+--------------------------------------------------------------------------------------------------------------------------+------------------------------------------------+---------------------------------------------------------------+---------------------------------------------+
| **Use Case Name**                |                                                                                                                          | **Configure Analysis Settings**                |                                                               |                                             |
+----------------------------------+--------------------------------------------------------------------------------------------------------------------------+------------------------------------------------+---------------------------------------------------------------+---------------------------------------------+
| **Created By**                   | **BaiXuan Zhang**                                                                                                        | **Last Update By**                             |                                                               | **BaiXuan Zhang**                           |
+----------------------------------+--------------------------------------------------------------------------------------------------------------------------+------------------------------------------------+---------------------------------------------------------------+---------------------------------------------+
| **Date Created**                 | **07/02/2026**                                                                                                           | **Last Revision Date**                         |                                                               | **07/02/2026**                              |
+----------------------------------+--------------------------------------------------------------------------------------------------------------------------+------------------------------------------------+---------------------------------------------------------------+---------------------------------------------+
| **Actors**                       | **Administrator, Manager**                                                                                               |                                                |                                                               |                                             |
+----------------------------------+--------------------------------------------------------------------------------------------------------------------------+------------------------------------------------+---------------------------------------------------------------+---------------------------------------------+
| **Description**                  | **Admin configures analysis rules, severity thresholds, LLM model selection, and compliance standards for the project.** |                                                |                                                               |                                             |
+----------------------------------+--------------------------------------------------------------------------------------------------------------------------+------------------------------------------------+---------------------------------------------------------------+---------------------------------------------+
| **Trigger**                      | **Admin navigates to \'Settings\' \> \'Analysis Configuration\'.**                                                       |                                                |                                                               |                                             |
+----------------------------------+--------------------------------------------------------------------------------------------------------------------------+------------------------------------------------+---------------------------------------------------------------+---------------------------------------------+
| **Preconditions**                | **1. User has Administrator or Manager role.**                                                                           |                                                |                                                               |                                             |
|                                  |                                                                                                                          |                                                |                                                               |                                             |
|                                  | **2. User is authenticated.**                                                                                            |                                                |                                                               |                                             |
|                                  |                                                                                                                          |                                                |                                                               |                                             |
|                                  | **3. Project exists in the system.**                                                                                     |                                                |                                                               |                                             |
+----------------------------------+--------------------------------------------------------------------------------------------------------------------------+------------------------------------------------+---------------------------------------------------------------+---------------------------------------------+
| **Use Case Input Specification** |                                                                                                                          |                                                |                                                               |                                             |
+----------------------------------+--------------------------------------------------------------------------------------------------------------------------+------------------------------------------------+---------------------------------------------------------------+---------------------------------------------+
| **Input**                        | **Type**                                                                                                                 | **Constraint**                                 |                                                               | **Example**                                 |
+----------------------------------+--------------------------------------------------------------------------------------------------------------------------+------------------------------------------------+---------------------------------------------------------------+---------------------------------------------+
| **LLM Model**                    | **Enum**                                                                                                                 | **Options: GPT-4, Claude-3.5-Sonnet, Custom**  |                                                               | **Claude-3.5-Sonnet**                       |
+----------------------------------+--------------------------------------------------------------------------------------------------------------------------+------------------------------------------------+---------------------------------------------------------------+---------------------------------------------+
| **Severity Thresholds**          | **JSON**                                                                                                                 | **Numeric thresholds for categorizing issues** |                                                               | **{ critical: 90, high: 70, medium: 40 }**  |
+----------------------------------+--------------------------------------------------------------------------------------------------------------------------+------------------------------------------------+---------------------------------------------------------------+---------------------------------------------+
| **Compliance Standards**         | **Array**                                                                                                                | **List of enabled standards**                  |                                                               | **\[\'ISO/IEC 25010\', \'OWASP Top 10\'\]** |
+----------------------------------+--------------------------------------------------------------------------------------------------------------------------+------------------------------------------------+---------------------------------------------------------------+---------------------------------------------+
| **Auto-merge Rules**             | **Boolean**                                                                                                              | **Enable/disable auto-merge for passing PRs**  |                                                               | **false**                                   |
+----------------------------------+--------------------------------------------------------------------------------------------------------------------------+------------------------------------------------+---------------------------------------------------------------+---------------------------------------------+
| **Postconditions**               | **Configuration is saved and applied to future analyses. Existing analyses are not retroactively affected.**             |                                                |                                                               |                                             |
+----------------------------------+--------------------------------------------------------------------------------------------------------------------------+------------------------------------------------+---------------------------------------------------------------+---------------------------------------------+
| **Normal Flows**                 | **User**                                                                                                                 |                                                | **System**                                                    |                                             |
+----------------------------------+--------------------------------------------------------------------------------------------------------------------------+------------------------------------------------+---------------------------------------------------------------+---------------------------------------------+
|                                  | **2. Admin selects LLM model from dropdown.**                                                                            |                                                | **1. System displays current configuration settings.**        |                                             |
|                                  |                                                                                                                          |                                                |                                                               |                                             |
|                                  | **4. Admin adjusts severity threshold sliders.**                                                                         |                                                | **3. System validates model selection and API availability.** |                                             |
|                                  |                                                                                                                          |                                                |                                                               |                                             |
|                                  | **6. Admin enables/disables compliance standards.**                                                                      |                                                | **5. System validates threshold values (0-100).**             |                                             |
|                                  |                                                                                                                          |                                                |                                                               |                                             |
|                                  | **8. Admin clicks \'Save Configuration\'.**                                                                              |                                                | **7. System validates compliance standard compatibility.**    |                                             |
|                                  |                                                                                                                          |                                                |                                                               |                                             |
|                                  |                                                                                                                          |                                                | **9. System updates configuration in PostgreSQL.**            |                                             |
|                                  |                                                                                                                          |                                                |                                                               |                                             |
|                                  |                                                                                                                          |                                                | **10. System clears Redis cache for affected projects.**      |                                             |
|                                  |                                                                                                                          |                                                |                                                               |                                             |
|                                  |                                                                                                                          |                                                | **11. System displays success notification.**                 |                                             |
|                                  |                                                                                                                          |                                                |                                                               |                                             |
|                                  |                                                                                                                          |                                                | **12. System logs configuration change in audit log.**        |                                             |
+----------------------------------+--------------------------------------------------------------------------------------------------------------------------+------------------------------------------------+---------------------------------------------------------------+---------------------------------------------+
| **Alternative Flow**             | **3A. If selected LLM model requires additional API key: System prompts for API key input and validation.**              |                                                |                                                               |                                             |
|                                  |                                                                                                                          |                                                |                                                               |                                             |
|                                  | **9A. If user enables \'Apply to existing analyses\': System queues re-analysis of recent PRs with new settings.**       |                                                |                                                               |                                             |
+----------------------------------+--------------------------------------------------------------------------------------------------------------------------+------------------------------------------------+---------------------------------------------------------------+---------------------------------------------+
| **Exception Flow**               | **E1. If configuration validation fails: System highlights invalid fields and prevents save.**                           |                                                |                                                               |                                             |
|                                  |                                                                                                                          |                                                |                                                               |                                             |
|                                  | **E2. If database update fails: System displays error and retains previous configuration.**                              |                                                |                                                               |                                             |
|                                  |                                                                                                                          |                                                |                                                               |                                             |
|                                  | **E3. If compliance standard is deprecated: System displays warning but allows save with user confirmation.**            |                                                |                                                               |                                             |
+----------------------------------+--------------------------------------------------------------------------------------------------------------------------+------------------------------------------------+---------------------------------------------------------------+---------------------------------------------+
| **Note**                         | **Configuration changes are logged for audit compliance. Default settings follow industry best practices.**              |                                                |                                                               |                                             |
+----------------------------------+--------------------------------------------------------------------------------------------------------------------------+------------------------------------------------+---------------------------------------------------------------+---------------------------------------------+

## 6.3 Activity Diagram

![IMG_256](media/image5.png){width="6.579166666666667in" height="6.579166666666667in"}

![IMG_256](media/image6.png){width="6.559722222222222in" height="5.5625in"}

![IMG_256](media/image7.png){width="6.6722222222222225in" height="8.340277777777779in"}

![IMG_256](media/image8.png){width="4.745833333333334in" height="9.144444444444444in"}

![IMG_256](media/image9.png){width="6.577083333333333in" height="4.625in"}

![IMG_256](media/image10.png){width="6.675in" height="6.513888888888889in"}

![IMG_256](media/image11.png){width="6.582638888888889in" height="7.779166666666667in"}

# 7. API Specifications

## 7.1 Authentication Endpoints

### POST /api/auth/register

**Description:** Register a new user account

**Request Body:**

> {
>
> \"username\": \"string (3-30 chars, alphanumeric + underscore)\",
>
> \"email\": \"string (valid email format)\",
>
> \"password\": \"string (min 8 chars, complexity requirements)\"
>
> }

**Response 201 Created:**

> {
>
> \"success\": true,
>
> \"message\": \"Registration successful. Please verify your email.\",
>
> \"data\": {
>
> \"user_id\": \"uuid\",
>
> \"username\": \"string\",
>
> \"email\": \"string\",
>
> \"role\": \"user\",
>
> \"created_at\": \"ISO 8601 timestamp\"
>
> }
>
> }

**Error Responses:**

-   **400 Bad Request:** Invalid input format

> {
>
> \"success\": false,
>
> \"error\": \"VALIDATION_ERROR\",
>
> \"message\": \"Password must contain uppercase, lowercase, number, and special character\",
>
> \"field\": \"password\"
>
> }

-   **409 Conflict:** Username or email already exists

> {
>
> \"success\": false,
>
> \"error\": \"DUPLICATE_USER\",
>
> \"message\": \"Email already registered\"
>
> }

### POST /api/auth/login

**Description:** Authenticate user and receive JWT tokens

**Request Body:**

> {
>
> \"email\": \"string (email or username)\",
>
> \"password\": \"string\"
>
> }

**Response 200 OK:**

> {
>
> \"success\": true,
>
> \"data\": {
>
> \"access_token\": \"string (JWT, 24h expiry)\",
>
> \"refresh_token\": \"string (JWT, 7d expiry)\",
>
> \"user\": {
>
> \"id\": \"uuid\",
>
> \"username\": \"string\",
>
> \"email\": \"string\",
>
> \"role\": \"string\"
>
> }
>
> }
>
> }

**Error Responses:**

-   **401 Unauthorized:** Invalid credentials

-   **403 Forbidden:** Account locked or unverified

-   **429 Too Many Requests:** Rate limit exceeded

### POST /api/auth/refresh

**Description:** Refresh access token using refresh token

**Request Body:**

> {
>
> \"refresh_token\": \"string\"
>
> }

**Response 200 OK:**

> {
>
> \"success\": true,
>
> \"data\": {
>
> \"access_token\": \"string (new JWT, 24h expiry)\"
>
> }
>
> }

## 7.2 Repository Management Endpoints

### POST /api/repositories

**Description:** Add a new GitHub repository for analysis

**Headers:**

> Authorization: Bearer \<access_token\>

**Request Body:**

> {
>
> \"github_url\": \"string (https://github.com/{owner}/{repo})\",
>
> \"default_branch\": \"string (optional, default: main)\",
>
> \"config\": {
>
> \"enabled_rules\": \[\"security\", \"performance\", \"style\"\],
>
> \"severity_threshold\": \"medium\",
>
> \"auto_merge_on_pass\": false
>
> }
>
> }

**Response 201 Created:**

> {
>
> \"success\": true,
>
> \"data\": {
>
> \"project_id\": \"uuid\",
>
> \"name\": \"string\",
>
> \"github_url\": \"string\",
>
> \"default_branch\": \"string\",
>
> \"webhook_configured\": true,
>
> \"initial_scan_status\": \"queued\",
>
> \"created_at\": \"ISO 8601 timestamp\"
>
> }
>
> }

**Error Responses:**

-   **400 Bad Request:** Invalid GitHub URL

-   **403 Forbidden:** Insufficient GitHub permissions

-   **409 Conflict:** Repository already added

### GET /api/repositories

**Description:** List all repositories for authenticated user

**Headers:**

> Authorization: Bearer \<access_token\>

**Query Parameters:**

-   page (integer, default: 1)

-   limit (integer, default: 20, max: 100)

-   status (enum: active, inactive, all)

**Response 200 OK:**

> {
>
> \"success\": true,
>
> \"data\": {
>
> \"repositories\": \[
>
> {
>
> \"project_id\": \"uuid\",
>
> \"name\": \"string\",
>
> \"github_url\": \"string\",
>
> \"is_active\": true,
>
> \"last_analyzed\": \"ISO 8601 timestamp\",
>
> \"quality_score\": 85.5,
>
> \"total_issues\": 12
>
> }
>
> \],
>
> \"pagination\": {
>
> \"page\": 1,
>
> \"limit\": 20,
>
> \"total\": 45,
>
> \"total_pages\": 3
>
> }
>
> }
>
> }

### GET /api/repositories/{project_id}

**Description:** Get detailed information about a specific repository

**Response 200 OK:**

> {
>
> \"success\": true,
>
> \"data\": {
>
> \"project_id\": \"uuid\",
>
> \"name\": \"string\",
>
> \"github_url\": \"string\",
>
> \"default_branch\": \"string\",
>
> \"languages\": \[\"Python\", \"JavaScript\"\],
>
> \"is_active\": true,
>
> \"webhook_configured\": true,
>
> \"created_at\": \"ISO 8601 timestamp\",
>
> \"last_analyzed\": \"ISO 8601 timestamp\",
>
> \"metrics\": {
>
> \"quality_score\": 85.5,
>
> \"total_lines\": 15000,
>
> \"code_coverage\": 78.5,
>
> \"avg_complexity\": 4.2,
>
> \"technical_debt\": 120
>
> },
>
> \"recent_analyses\": \[
>
> {
>
> \"analysis_id\": \"uuid\",
>
> \"pr_number\": 42,
>
> \"status\": \"completed\",
>
> \"total_issues\": 5,
>
> \"completed_at\": \"ISO 8601 timestamp\"
>
> }
>
> \]
>
> }
>
> }

## 7.3 Analysis Endpoints

### GET /api/analyses/{analysis_id}

**Description:** Get detailed analysis results

**Response 200 OK:**

> {
>
> \"success\": true,
>
> \"data\": {
>
> \"analysis_id\": \"uuid\",
>
> \"pr_id\": \"uuid\",
>
> \"pr_number\": 42,
>
> \"status\": \"completed\",
>
> \"started_at\": \"ISO 8601 timestamp\",
>
> \"completed_at\": \"ISO 8601 timestamp\",
>
> \"processing_time\": 45,
>
> \"summary\": {
>
> \"total_issues\": 12,
>
> \"critical\": 1,
>
> \"high\": 3,
>
> \"medium\": 5,
>
> \"low\": 3
>
> },
>
> \"issues\": \[
>
> {
>
> \"issue_id\": \"uuid\",
>
> \"severity\": \"high\",
>
> \"category\": \"security\",
>
> \"title\": \"SQL Injection Vulnerability\",
>
> \"description\": \"User input is directly concatenated into SQL query\",
>
> \"file_path\": \"src/database.py\",
>
> \"line_number\": 45,
>
> \"suggestion\": \"Use parameterized queries or ORM\",
>
> \"code_snippet\": \"query = f\\\"SELECT \* FROM users WHERE id = {user_id}\\\"\"
>
> }
>
> \],
>
> \"compliance\": \[
>
> {
>
> \"standard\": \"ISO/IEC 25010\",
>
> \"clause\": \"Security\",
>
> \"status\": \"fail\",
>
> \"details\": \"1 critical security vulnerability detected\"
>
> }
>
> \]
>
> }
>
> }

### POST /api/analyses/{analysis_id}/feedback

**Description:** Submit feedback on analysis results

**Request Body:**

> {
>
> \"issue_id\": \"uuid\",
>
> \"action\": \"accept \| dismiss \| false_positive\",
>
> \"comment\": \"string (optional)\"
>
> }

**Response 200 OK:**

> {
>
> \"success\": true,
>
> \"message\": \"Feedback recorded successfully\"
>
> }

## 7.4 Architecture Endpoints

### GET /api/architecture/{project_id}/graph

**Description:** Get dependency graph data for visualization

**Query Parameters:**

-   entity_type (enum: file, class, function, all)

-   min_complexity (integer, optional)

-   max_depth (integer, default: 5)

**Response 200 OK:**

> {
>
> \"success\": true,
>
> \"data\": {
>
> \"nodes\": \[
>
> {
>
> \"id\": \"uuid\",
>
> \"type\": \"class\",
>
> \"name\": \"UserService\",
>
> \"file_path\": \"src/services/user.py\",
>
> \"complexity\": 8,
>
> \"lines\": 150
>
> }
>
> \],
>
> \"edges\": \[
>
> {
>
> \"source\": \"uuid\",
>
> \"target\": \"uuid\",
>
> \"type\": \"depends_on\",
>
> \"weight\": 5
>
> }
>
> \],
>
> \"metrics\": {
>
> \"total_nodes\": 45,
>
> \"total_edges\": 78,
>
> \"circular_dependencies\": 2,
>
> \"avg_coupling\": 3.5
>
> },
>
> \"circular_dependencies\": \[
>
> {
>
> \"cycle\": \[\"ModuleA\", \"ModuleB\", \"ModuleC\", \"ModuleA\"\],
>
> \"severity\": \"high\"
>
> }
>
> \]
>
> }
>
> }

## 7.5 Webhook Endpoints

### POST /api/webhooks/github

**Description:** Receive GitHub webhook events (internal use)

**Headers:**

> X-GitHub-Event: pull_request
>
> X-Hub-Signature-256: sha256=\<signature\>

**Request Body:** GitHub webhook payload (varies by event)

**Response 200 OK:**

> {
>
> \"success\": true,
>
> \"message\": \"Webhook processed\",
>
> \"task_id\": \"uuid\"
>
> }

## 7.6 Metrics Endpoints

### GET /api/metrics/{project_id}

**Description:** Get quality metrics and trends

**Query Parameters:**

-   period (enum: 7d, 30d, 90d, 1y)

-   metrics (array: quality_score, issues, complexity, coverage)

**Response 200 OK:**

> {
>
> \"success\": true,
>
> \"data\": {
>
> \"current\": {
>
> \"quality_score\": 85.5,
>
> \"total_issues\": 12,
>
> \"avg_complexity\": 4.2,
>
> \"code_coverage\": 78.5
>
> },
>
> \"trends\": \[
>
> {
>
> \"date\": \"2026-02-01\",
>
> \"quality_score\": 82.0,
>
> \"total_issues\": 18
>
> }
>
> \],
>
> \"comparison\": {
>
> \"quality_score_change\": \"+3.5\",
>
> \"issues_change\": \"-6\"
>
> }
>
> }
>
> }

## 7.7 Error Response Format

All API errors follow this standard format:

> {
>
> \"success\": false,
>
> \"error\": \"ERROR_CODE\",
>
> \"message\": \"Human-readable error message\",
>
> \"details\": {
>
> \"field\": \"specific_field\",
>
> \"constraint\": \"validation_rule\"
>
> },
>
> \"timestamp\": \"ISO 8601 timestamp\",
>
> \"request_id\": \"uuid\"
>
> }

### Common Error Codes

-   VALIDATION_ERROR: Input validation failed

-   AUTHENTICATION_REQUIRED: Missing or invalid authentication

-   AUTHORIZATION_FAILED: Insufficient permissions

-   RESOURCE_NOT_FOUND: Requested resource does not exist

-   DUPLICATE_RESOURCE: Resource already exists

-   RATE_LIMIT_EXCEEDED: Too many requests

-   EXTERNAL_SERVICE_ERROR: Third-party service failure

-   INTERNAL_SERVER_ERROR: Unexpected server error

# 8. Data Validation Rules

## 8.1 User Input Validation

  -------------- ----------- ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- --------------------------------------------------------------------------------------------- ---------------------------------------------------------------------------------------------------------------
  Field          Data Type   Validation Rules                                                                                                                                                              Regex Pattern                                                                                 Error Message

  Username       String      \- Length: 3-30 characters\<br\>- Alphanumeric and underscore only\<br\>- Must start with letter\<br\>- Case-insensitive uniqueness                                           \^\[a-zA-Z\]\[a-zA-Z0-9\_\]{2,29}\$                                                           \"Username must be 3-30 characters, start with a letter, and contain only letters, numbers, and underscores\"

  Email          String      \- Valid email format\<br\>- Max 100 characters\<br\>- Case-insensitive uniqueness\<br\>- No disposable email domains                                                         \^\[a-zA-Z0-9.\_%+-\]+@\[a-zA-Z0-9.-\]+\\.\[a-zA-Z\]{2,}\$                                    \"Please enter a valid email address\"

  Password       String      \- Min 8 characters\<br\>- Max 128 characters\<br\>- At least 1 uppercase\<br\>- At least 1 lowercase\<br\>- At least 1 number\<br\>- At least 1 special char (!@#\$%\^&\*)   \^(?=.\*\[a-z\])(?=.\*\[A-Z\])(?=.\*\\d)(?=.\*\[@\$!%\*?&\])\[A-Za-z\\d@\$!%\*?&\]{8,128}\$   \"Password must be 8-128 characters with uppercase, lowercase, number, and special character\"

  GitHub URL     URL         \- Format: https://github.com/{owner}/{repo}\<br\>- Owner: 1-39 chars, alphanumeric + hyphen\<br\>- Repo: 1-100 chars, alphanumeric + hyphen/underscore/dot                   \^https://github\\.com/\[a-zA-Z0-9-\]{1,39}/\[a-zA-Z0-9.\_-\]{1,100}\$                        \"Please enter a valid GitHub repository URL\"

  Project Name   String      \- Length: 3-200 characters\<br\>- Alphanumeric, spaces, hyphens, underscores\<br\>- Trim whitespace                                                                          \^\[a-zA-Z0-9 \_-\]{3,200}\$                                                                  \"Project name must be 3-200 characters\"
  -------------- ----------- ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- --------------------------------------------------------------------------------------------- ---------------------------------------------------------------------------------------------------------------

## 8.2 Business Logic Validation

  ----------------- ------------------------------------------------------ ------------------------------------------------------- --------------------------------------------------------------------
  Rule ID           Validation Rule                                        Implementation                                          Error Handling

  BV-01             Email must be unique across all users                  Database unique constraint + application-level check    Return 409 Conflict with message \"Email already registered\"

  BV-02             Username must be unique (case-insensitive)             Database unique index (lowercase) + application check   Return 409 Conflict with message \"Username already taken\"

  BV-03             Repository URL must be unique per platform instance    Database unique constraint on github_url                Return 409 Conflict with message \"Repository already connected\"

  BV-04             User must have GitHub admin access to add repository   GitHub API permission check before webhook creation     Return 403 Forbidden with message \"Admin access required\"

  BV-05             Analysis cannot be triggered for closed PRs            Check PR status before queuing analysis                 Return 400 Bad Request with message \"Cannot analyze closed PR\"

  BV-06             JWT token must not be expired                          Check exp claim in token                                Return 401 Unauthorized with message \"Token expired\"

  BV-07             User role must have required permission for action     RBAC permission matrix check                            Return 403 Forbidden with message \"Insufficient permissions\"

  BV-08             File size must not exceed 10MB for analysis            Check file size before parsing                          Skip file with warning \"File too large for analysis\"

  BV-09             Analysis queue must not exceed 1000 pending tasks      Check queue depth before adding task                    Return 429 Too Many Requests with message \"Analysis queue full\"

  BV-10             Webhook signature must be valid                        HMAC-SHA256 verification                                Return 401 Unauthorized with message \"Invalid webhook signature\"
  ----------------- ------------------------------------------------------ ------------------------------------------------------- --------------------------------------------------------------------

## 8.3 Data Sanitization Rules

  ---------------------------------------------- ---------------------------------------------------- --------------------------------------
  Input Type                                     Sanitization Method                                  Purpose

  User-generated text (comments, descriptions)   HTML entity encoding, strip script tags              Prevent XSS attacks

  SQL query parameters                           Parameterized queries, ORM escaping                  Prevent SQL injection

  File paths                                     Path normalization, directory traversal prevention   Prevent path traversal attacks

  GitHub URLs                                    URL parsing and validation, whitelist domain         Prevent SSRF attacks

  JSON payloads                                  Schema validation, type checking                     Prevent injection and type confusion

  Code snippets                                  Syntax highlighting escaping, no execution           Safe display of code
  ---------------------------------------------- ---------------------------------------------------- --------------------------------------

# 8A. Data Lifecycle Management

## 8A.1 Data Collection and Creation

| Data Type | Collection Method | Source | Retention Trigger | Privacy Classification |
|-----------|-------------------|--------|-------------------|------------------------|
| **User Account Data** | Registration form, OAuth | User input, GitHub API | Account creation | PII - Confidential |
| **Repository Metadata** | GitHub API, Webhooks | GitHub | Repository connection | Internal |
| **Code Analysis Data** | AST parsing, LLM API | Pull request diffs | PR submission | Internal |
| **Dependency Graphs** | Neo4j graph generation | Code analysis | Analysis completion | Internal |
| **Audit Logs** | Automatic logging | System events | User action | Internal - Immutable |
| **Session Data** | Authentication | User login | Session creation | Confidential |
| **Metrics Data** | Aggregation | Analysis results | Daily aggregation | Internal |

## 8A.2 Data Storage and Retention

| Data Type | Storage Location | Retention Period | Retention Rationale | Deletion Method |
|-----------|------------------|------------------|---------------------|-----------------|
| **User Accounts** | PostgreSQL | Active + 90 days after account deletion | GDPR compliance, user right to deletion | Soft delete → hard delete after 90 days |
| **Audit Logs** | PostgreSQL | 7 years | SOC 2, compliance requirements | Automated purge after 7 years |
| **Code Analysis Results** | PostgreSQL | 1 year | Historical analysis, trend tracking | Automated archival to S3, then deletion |
| **Dependency Graphs** | Neo4j | 6 months | Architecture drift detection | Automated graph node deletion |
| **Session Data** | Redis | 24 hours (JWT expiry) | Security best practice | Automatic expiration |
| **Temporary Analysis Data** | Redis | 1 hour | Processing only | Automatic expiration |
| **Backup Data** | S3 Glacier | 30 days | Disaster recovery | Automated lifecycle policy |
| **Metrics Aggregates** | PostgreSQL | 2 years | Long-term trend analysis | Automated purge |

## 8A.3 Data Access and Usage

| Data Type | Access Control | Access Method | Audit Requirement | Encryption |
|-----------|----------------|---------------|-------------------|------------|
| **User Credentials** | System only (hashed) | Bcrypt verification | All access attempts logged | At rest (AES-256), in transit (TLS 1.3) |
| **Personal Information** | User + Admin | RBAC-controlled API | Read/write logged | At rest (AES-256), in transit (TLS 1.3) |
| **Code Analysis Data** | Project members | RBAC + project isolation | Read logged | In transit (TLS 1.3) |
| **Audit Logs** | Admin only | Read-only API | Access logged | At rest (AES-256), immutable |
| **System Configuration** | Admin only | Configuration API | All changes logged | At rest (AES-256) |

## 8A.4 Data Archival

| Data Type | Archival Trigger | Archival Location | Archival Format | Retrieval Time | Cost |
|-----------|------------------|-------------------|-----------------|----------------|------|
| **Old Analysis Results** | > 1 year old | S3 Glacier Deep Archive | Compressed JSON | 12-48 hours | $0.00099/GB/month |
| **Historical Graphs** | > 6 months old | S3 Glacier | Graph export (JSON) | 3-5 hours | $0.004/GB/month |
| **Audit Logs** | > 2 years old | S3 Glacier | Compressed logs | 3-5 hours | $0.004/GB/month |
| **Database Backups** | > 30 days old | S3 Glacier | Encrypted backup | 3-5 hours | $0.004/GB/month |

## 8A.5 Data Deletion and Destruction

| Deletion Scenario | Trigger | Process | Verification | Compliance |
|-------------------|---------|---------|--------------|------------|
| **User Account Deletion** | User request or admin action | 1. Soft delete (mark as deleted)<br>2. Anonymize PII<br>3. Hard delete after 90 days | Deletion confirmation email, audit log entry | GDPR Article 17 (Right to Erasure) |
| **Project Deletion** | Owner request | 1. Delete analysis results<br>2. Delete dependency graphs<br>3. Delete project metadata | Cascade deletion verification | N/A |
| **Expired Session Data** | TTL expiration | Automatic Redis expiration | N/A | Security best practice |
| **Backup Expiration** | 30-day retention exceeded | S3 lifecycle policy deletion | S3 deletion logs | Data minimization |
| **Audit Log Purge** | 7-year retention exceeded | Automated batch deletion | Deletion audit log | SOC 2 compliance |

## 8A.6 Data Backup and Recovery

| Backup Type | Frequency | Retention | Storage | Recovery Time | Recovery Point |
|-------------|-----------|-----------|---------|---------------|----------------|
| **PostgreSQL Full Backup** | Daily at 2 AM UTC | 30 days | S3 Standard | 2 hours | 24 hours |
| **PostgreSQL Incremental** | Hourly | 7 days | S3 Standard | 1 hour | 1 hour |
| **Neo4j Snapshot** | Daily at 3 AM UTC | 14 days | S3 Standard | 3 hours | 24 hours |
| **Redis AOF** | Continuous | 7 days | EBS Volume | 10 minutes | 1 minute |
| **Configuration Backup** | On change | 90 days | S3 Standard | 30 minutes | 0 (versioned) |

## 8A.7 Data Migration and Portability

| Migration Scenario | Export Format | Export Method | Data Included | Compliance |
|-------------------|---------------|---------------|---------------|------------|
| **User Data Export** | JSON | API endpoint `/api/users/me/export` | Profile, projects, analysis history | GDPR Article 20 (Data Portability) |
| **Project Export** | ZIP (JSON + CSV) | API endpoint `/api/projects/{id}/export` | Metadata, analysis results, metrics | N/A |
| **Audit Log Export** | CSV | Admin API `/api/audit/export` | All audit entries for date range | SOC 2 compliance |
| **Database Migration** | SQL dump | pg_dump, neo4j-admin dump | Complete database | Disaster recovery |

## 8A.8 Data Quality and Integrity

| Quality Aspect | Requirement | Validation Method | Frequency | Remediation |
|----------------|-------------|-------------------|-----------|-------------|
| **Data Accuracy** | Analysis results match source code | Automated regression tests | Every release | Bug fix, reanalysis |
| **Data Completeness** | All required fields populated | Database constraints, API validation | Real-time | Reject incomplete data |
| **Data Consistency** | Foreign key integrity maintained | Database constraints, transaction management | Real-time | Transaction rollback |
| **Data Timeliness** | Analysis results within 2 minutes | Performance monitoring | Continuous | Performance optimization |
| **Data Uniqueness** | No duplicate records | Unique constraints, application logic | Real-time | Reject duplicates |

## 8A.9 Data Privacy and Consent

| Privacy Aspect | Implementation | User Control | Transparency |
|----------------|----------------|--------------|--------------|
| **Consent Management** | Explicit consent during registration | Consent preferences in user settings | Privacy policy, terms of service |
| **Data Minimization** | Collect only necessary data | N/A | Privacy policy disclosure |
| **Purpose Limitation** | Use data only for stated purposes | N/A | Privacy policy, consent form |
| **Access Control** | RBAC, project isolation | User can control project access | Access logs available to user |
| **Right to Access** | User data export API | Self-service export | Privacy policy |
| **Right to Rectification** | User profile update API | Self-service profile editing | User settings |
| **Right to Erasure** | Account deletion API | Self-service account deletion | Privacy policy, deletion confirmation |
| **Right to Restriction** | Account deactivation | Self-service deactivation | User settings |

# 9. Requirements Traceability Matrix (RTM)

## 9.1 URS to SRS Mapping

  ----------- ------------------------ ------------------------------------------------------ --------------------------- ----------- -------------
  URS ID      URS Description          Related SRS                                            Related NFR                 Use Case    Priority

  URS-01      Guest registration       SRS-001, SRS-002                                       NFR-005, NFR-008            UC-01       Must Have

  URS-02      User login               SRS-001, SRS-002                                       NFR-005, NFR-009            UC-02       Must Have

  URS-03      Add GitHub repository    SRS-004, SRS-005, SRS-006                              NFR-006, NFR-007            UC-03       Must Have

  URS-04      Automated PR review      SRS-007, SRS-008, SRS-009, SRS-010, SRS-018, SRS-019   NFR-001, NFR-002, NFR-014   UC-04       Must Have

  URS-05      View dependency graph    SRS-012, SRS-013, SRS-014                              NFR-001, NFR-015            UC-05       Should Have

  URS-06      View quality dashboard   SRS-015, SRS-016, SRS-017                              NFR-001, NFR-015, NFR-016   UC-06       Should Have

  URS-07      Configure settings       SRS-003, SRS-015, SRS-016, SRS-017                     NFR-006, NFR-009, NFR-022   UC-07       Must Have
  ----------- ------------------------ ------------------------------------------------------ --------------------------- ----------- -------------

## 9.2 SRS to Design Components Mapping

  --------- ---------------------- -------------------------------------------- ------------------------------------- ----------------------------------------- ----------------------------------
  SRS ID    Requirement            Design Component                             Database Tables                       API Endpoints                             Test Cases

  SRS-001   JWT authentication     AuthService, JWTManager                      users, sessions                       POST /api/auth/login, /api/auth/refresh   TC-AUTH-001 to TC-AUTH-005

  SRS-002   RBAC                   AuthorizationMiddleware, PermissionChecker   users, roles, permissions             All protected endpoints                   TC-RBAC-001 to TC-RBAC-010

  SRS-003   OAuth 2.0              GitHubOAuthService                           oauth_tokens                          POST /api/auth/github                     TC-OAUTH-001 to TC-OAUTH-003

  SRS-004   GitHub webhooks        WebhookHandler, SignatureVerifier            projects, webhooks                    POST /api/webhooks/github                 TC-WEBHOOK-001 to TC-WEBHOOK-005

  SRS-007   AST parsing            ASTParser, DependencyExtractor               code_entities, dependencies (Neo4j)   N/A (internal)                            TC-PARSE-001 to TC-PARSE-010

  SRS-008   LLM integration        LLMClient, PromptBuilder                     analysis_results, issues              N/A (internal)                            TC-LLM-001 to TC-LLM-008

  SRS-009   Issue categorization   IssueCategorizer, SeverityClassifier         issues                                GET /api/analyses/{id}                    TC-ISSUE-001 to TC-ISSUE-005

  SRS-010   GitHub comments        GitHubCommentPoster                          comments                              N/A (external API)                        TC-COMMENT-001 to TC-COMMENT-003

  SRS-012   Neo4j storage          Neo4jClient, GraphRepository                 N/A (graph database)                  GET /api/architecture/{id}/graph          TC-GRAPH-001 to TC-GRAPH-007

  SRS-013   Drift detection        ArchitectureDriftDetector, CycleDetector     architectural_violations              GET /api/architecture/{id}/drift          TC-DRIFT-001 to TC-DRIFT-005

  SRS-014   Graph visualization    D3GraphRenderer (frontend)                   N/A                                   GET /api/architecture/{id}/graph          TC-VIZ-001 to TC-VIZ-004

  SRS-018   Performance            TaskQueue, AnalysisWorker                    task_queue (Redis)                    N/A (internal)                            TC-PERF-001 to TC-PERF-010

  SRS-019   Redis queue            RedisClient, CeleryWorker                    N/A (Redis)                           N/A (internal)                            TC-QUEUE-001 to TC-QUEUE-005
  --------- ---------------------- -------------------------------------------- ------------------------------------- ----------------------------------------- ----------------------------------

## 9.3 NFR to Verification Method Mapping

  -------------- ----------------------- ----------------------- ------------------------------------------ ------------------------
  NFR ID         Requirement             Verification Method     Success Criteria                           Test Tool

  NFR-001        API response time       Performance testing     P95 \< 500ms for GET, \< 1s for POST       JMeter, Locust

  NFR-002        Concurrent requests     Load testing            100 concurrent users without degradation   JMeter

  NFR-003        Horizontal scaling      Scalability testing     Linear scaling up to 50 workers            Kubernetes metrics

  NFR-005        Password policy         Security testing        All requirements enforced                  Automated tests

  NFR-006        Authorization           Penetration testing     No unauthorized access                     OWASP ZAP

  NFR-007        Data encryption         Security audit          TLS 1.3, AES-256 verified                  SSL Labs, manual audit

  NFR-008        Input validation        Security testing        No injection vulnerabilities               OWASP ZAP, Burp Suite

  NFR-011        99.5% uptime            Monitoring              \< 43.8 hours downtime/year                Pingdom, Datadog

  NFR-015        User interface          Usability testing       80% task completion rate                   User testing sessions

  NFR-019        Code quality            Static analysis         \> 80% coverage, \< 10 complexity          SonarQube, pytest-cov

  NFR-023        Browser compatibility   Cross-browser testing   All features work on supported browsers    BrowserStack

  NFR-026        GDPR compliance         Compliance audit        All requirements met                       Legal review
  -------------- ----------------------- ----------------------- ------------------------------------------ ------------------------

## 9.4 Feature to Requirements Mapping

  ----------------------- ------------------------ ------------------------------------------------------ ------------------------------------ ------------- ----------------
  Feature                 Related URS              Related SRS                                            Related NFR                          Priority      Status

  Code Review             URS-04                   SRS-007, SRS-008, SRS-009, SRS-010, SRS-011            NFR-001, NFR-002, NFR-014            Must Have     In Development

  Architecture Analysis   URS-05                   SRS-012, SRS-013, SRS-014                              NFR-001, NFR-003, NFR-015            Must Have     In Development

  Authentication System   URS-01, URS-02, URS-07   SRS-001, SRS-002, SRS-003                              NFR-005, NFR-006, NFR-007, NFR-009   Must Have     In Development

  Project Management      URS-03, URS-06           SRS-004, SRS-005, SRS-006, SRS-015, SRS-016, SRS-017   NFR-001, NFR-015, NFR-016            Should Have   Planned
  ----------------------- ------------------------ ------------------------------------------------------ ------------------------------------ ------------- ----------------

## 9.5 Requirements to Code Mapping (Forward Traceability)

This section maps requirements to their implementation in the codebase, enabling verification that all requirements have been implemented.

| Requirement ID | Requirement Type | Implementation Module | File Path | Function/Class | Implementation Status | Code Review Status |
|----------------|------------------|----------------------|-----------|----------------|----------------------|-------------------|
| SRS-001 | Functional | Authentication | `services/auth-service/src/auth/jwt_manager.py` | `JWTManager.generate_token()` | Complete | Approved |
| SRS-002 | Functional | Authorization | `services/auth-service/src/auth/rbac.py` | `RBACMiddleware.check_permission()` | Complete | Approved |
| SRS-003 | Functional | OAuth | `services/auth-service/src/auth/github_oauth.py` | `GitHubOAuthService.authorize()` | Complete | Approved |
| SRS-004 | Functional | Webhooks | `services/api-gateway/src/webhooks/github_handler.py` | `GitHubWebhookHandler.handle_pr_event()` | Complete | Approved |
| SRS-005 | Functional | Repository Validation | `services/project-manager/src/repositories/validator.py` | `RepositoryValidator.validate_url()` | Complete | Approved |
| SRS-007 | Functional | AST Parsing | `services/code-review-engine/src/parsers/ast_parser.py` | `ASTParser.parse()` | Complete | Approved |
| SRS-008 | Functional | LLM Integration | `services/llm-service/src/clients/llm_client.py` | `LLMClient.analyze_code()` | Complete | Approved |
| SRS-009 | Functional | Issue Categorization | `services/code-review-engine/src/analysis/categorizer.py` | `IssueCategorizer.categorize()` | Complete | Approved |
| SRS-010 | Functional | GitHub Comments | `services/code-review-engine/src/github/comment_poster.py` | `CommentPoster.post_comments()` | Complete | Approved |
| SRS-012 | Functional | Graph Storage | `services/architecture-analyzer/src/graph/neo4j_manager.py` | `Neo4jManager.store_graph()` | Complete | Approved |
| SRS-013 | Functional | Drift Detection | `services/architecture-analyzer/src/analysis/drift_detector.py` | `DriftDetector.detect_drift()` | Complete | Approved |
| SRS-014 | Functional | Graph Visualization | `frontend/src/components/ArchitectureGraph.tsx` | `ArchitectureGraph` component | Complete | Approved |
| NFR-001 | Non-Functional | Performance | `services/*/src/middleware/performance.py` | `PerformanceMiddleware` | Complete | Approved |
| NFR-005 | Non-Functional | Password Policy | `services/auth-service/src/auth/password_validator.py` | `PasswordValidator.validate()` | Complete | Approved |
| NFR-007 | Non-Functional | Encryption | `services/*/src/security/encryption.py` | `EncryptionManager` | Complete | Approved |

## 9.6 Requirements to Test Cases Mapping (Verification Traceability)

This section maps requirements to their test cases, ensuring all requirements are adequately tested.

| Requirement ID | Requirement Type | Test Case ID | Test Type | Test File Path | Test Status | Coverage % | Last Run Date |
|----------------|------------------|--------------|-----------|----------------|-------------|------------|---------------|
| SRS-001 | Functional | TC-AUTH-001 to TC-AUTH-005 | Unit, Integration | `tests/auth/test_jwt_manager.py` | Passing | 95% | 2026-02-19 |
| SRS-002 | Functional | TC-RBAC-001 to TC-RBAC-010 | Unit, Integration | `tests/auth/test_rbac.py` | Passing | 92% | 2026-02-19 |
| SRS-003 | Functional | TC-OAUTH-001 to TC-OAUTH-003 | Integration | `tests/auth/test_github_oauth.py` | Passing | 88% | 2026-02-19 |
| SRS-004 | Functional | TC-WEBHOOK-001 to TC-WEBHOOK-005 | Integration | `tests/webhooks/test_github_handler.py` | Passing | 90% | 2026-02-19 |
| SRS-007 | Functional | TC-PARSE-001 to TC-PARSE-010 | Unit | `tests/parsers/test_ast_parser.py` | Passing | 94% | 2026-02-19 |
| SRS-008 | Functional | TC-LLM-001 to TC-LLM-008 | Integration, Mock | `tests/llm/test_llm_client.py` | Passing | 87% | 2026-02-19 |
| SRS-009 | Functional | TC-ISSUE-001 to TC-ISSUE-005 | Unit | `tests/analysis/test_categorizer.py` | Passing | 93% | 2026-02-19 |
| SRS-010 | Functional | TC-COMMENT-001 to TC-COMMENT-003 | Integration | `tests/github/test_comment_poster.py` | Passing | 89% | 2026-02-19 |
| SRS-012 | Functional | TC-GRAPH-001 to TC-GRAPH-007 | Integration | `tests/graph/test_neo4j_manager.py` | Passing | 91% | 2026-02-19 |
| SRS-013 | Functional | TC-DRIFT-001 to TC-DRIFT-006 | Unit, Integration | `tests/analysis/test_drift_detector.py` | Passing | 90% | 2026-02-19 |
| SRS-014 | Functional | TC-VIZ-001 to TC-VIZ-004 | E2E | `tests/e2e/test_graph_visualization.spec.ts` | Passing | 85% | 2026-02-19 |
| NFR-001 | Non-Functional | TC-PERF-001 to TC-PERF-010 | Performance | `tests/performance/test_api_latency.py` | Passing | N/A | 2026-02-18 |
| NFR-002 | Non-Functional | TC-LOAD-001 to TC-LOAD-005 | Load | `tests/performance/test_concurrency.py` | Passing | N/A | 2026-02-18 |
| NFR-005 | Non-Functional | TC-SEC-001 to TC-SEC-008 | Security | `tests/security/test_password_policy.py` | Passing | 96% | 2026-02-19 |
| NFR-007 | Non-Functional | TC-SEC-020 to TC-SEC-025 | Security | `tests/security/test_encryption.py` | Passing | 94% | 2026-02-19 |
| NFR-011 | Non-Functional | TC-AVAIL-001 to TC-AVAIL-003 | Monitoring | `tests/reliability/test_uptime.py` | Passing | N/A | 2026-02-19 |
| NFR-015 | Non-Functional | TC-UI-001 to TC-UI-015 | Usability | `tests/usability/test_user_interface.py` | Passing | N/A | 2026-02-17 |

## 9.7 Bidirectional Traceability Matrix (Complete Lifecycle)

This comprehensive matrix provides bidirectional traceability across the entire development lifecycle.

| URS ID | SRS ID | NFR ID | Design Component | Code Module | Test Case | Verification Status | Deployment Status |
|--------|--------|--------|------------------|-------------|-----------|---------------------|-------------------|
| URS-01 | SRS-001, SRS-002 | NFR-005, NFR-008 | AuthService | `auth-service/src/auth/` | TC-AUTH-001 to TC-AUTH-010 | Verified | Deployed (v1.2.0) |
| URS-02 | SRS-001, SRS-002 | NFR-005, NFR-009 | AuthService | `auth-service/src/auth/` | TC-AUTH-001 to TC-AUTH-005 | Verified | Deployed (v1.2.0) |
| URS-03 | SRS-004, SRS-005, SRS-006 | NFR-006, NFR-007 | ProjectManager | `project-manager/src/` | TC-REPO-001 to TC-REPO-008 | Verified | Deployed (v1.1.0) |
| URS-04 | SRS-007 to SRS-011, SRS-018, SRS-019 | NFR-001, NFR-002, NFR-014 | CodeReviewEngine | `code-review-engine/src/` | TC-REVIEW-001 to TC-REVIEW-025 | Verified | Deployed (v1.3.0) |
| URS-05 | SRS-012, SRS-013, SRS-014 | NFR-001, NFR-015 | ArchitectureAnalyzer | `architecture-analyzer/src/` | TC-ARCH-001 to TC-ARCH-015 | Verified | Deployed (v1.2.0) |
| URS-06 | SRS-015, SRS-016, SRS-017 | NFR-001, NFR-015, NFR-016 | MetricsDashboard | `frontend/src/components/metrics/` | TC-METRICS-001 to TC-METRICS-010 | Verified | Deployed (v1.1.0) |
| URS-07 | SRS-003, SRS-015 to SRS-017 | NFR-006, NFR-009, NFR-022 | ConfigManager | `api-gateway/src/config/` | TC-CONFIG-001 to TC-CONFIG-007 | Verified | Deployed (v1.0.0) |

## 9.8 Requirements Change Impact Analysis

This section tracks requirement changes and their impact across the system lifecycle.

| Change ID | Affected Requirement | Change Type | Change Date | Impact on Design | Impact on Code | Impact on Tests | Regression Risk | Change Status |
|-----------|---------------------|-------------|-------------|------------------|----------------|-----------------|-----------------|---------------|
| CHG-001 | SRS-008 | Enhancement | 2026-01-15 | LLMClient interface updated | Added Claude 3.5 support | 3 new test cases | Low | Complete |
| CHG-002 | NFR-001 | Modification | 2026-01-20 | Performance targets tightened | Caching layer added | Performance tests updated | Medium | Complete |
| CHG-003 | SRS-002 | Enhancement | 2026-02-01 | Added 5th role (Visitor) | RBAC logic updated | 5 new test cases | Low | Complete |
| CHG-004 | SRS-013 | Bug Fix | 2026-02-10 | Algorithm corrected | Drift detection fixed | Test case added | Low | Complete |
| CHG-005 | NFR-007 | Enhancement | 2026-02-12 | TLS 1.2 → TLS 1.3 | Configuration updated | Security tests updated | Low | Complete |

## 9.9 Uncovered Requirements Analysis

This section identifies requirements that lack adequate implementation or testing coverage.

| Requirement ID | Requirement Description | Coverage Gap Type | Gap Description | Remediation Plan | Target Date | Owner |
|----------------|------------------------|-------------------|-----------------|------------------|-------------|-------|
| SRS-006 | Repository synchronization | Partial Implementation | Scheduled sync not implemented | Implement cron job for scheduled sync | 2026-03-15 | Backend Team |
| SRS-011 | User feedback capture | Partial Testing | Bulk actions not tested | Add integration tests for bulk feedback | 2026-02-28 | QA Team |
| SRS-017 | Google Style Guide compliance | Partial Implementation | Java and Go style checks missing | Integrate Checkstyle and golangci-lint | 2026-03-30 | DevOps Team |
| NFR-020 | Modularity | Partial Verification | Architecture compliance tests missing | Implement ArchUnit tests | 2026-03-10 | Architecture Team |
| NFR-028 | Accessibility compliance | Partial Testing | Screen reader testing incomplete | Conduct manual accessibility audit | 2026-04-15 | Frontend Team |

## 9.10 Compliance Traceability

This section maps requirements to regulatory and standards compliance obligations.

| Compliance Standard | Related Requirements | Compliance Control | Verification Method | Audit Frequency | Last Audit Date | Compliance Status |
|---------------------|---------------------|-------------------|---------------------|-----------------|-----------------|-------------------|
| GDPR Article 6 (Lawful Basis) | SRS-001, SRS-002, NFR-026 | User consent management | Legal review, consent logs | Annual | 2025-12-01 | Compliant |
| GDPR Article 17 (Right to Erasure) | Data deletion requirements | Account deletion API | Functional testing, audit logs | Annual | 2025-12-01 | Compliant |
| GDPR Article 20 (Data Portability) | Data export requirements | Export API endpoints | Integration testing | Annual | 2025-12-01 | Compliant |
| SOC 2 - CC6.1 (Logical Access) | SRS-002, NFR-006 | RBAC implementation | Penetration testing | Bi-annual | 2025-11-15 | Compliant |
| SOC 2 - CC6.6 (Encryption) | NFR-007 | TLS 1.3, AES-256 | Security audit | Bi-annual | 2025-11-15 | Compliant |
| SOC 2 - CC7.2 (Monitoring) | NFR-009, NFR-021 | Audit logging, monitoring | Log analysis | Bi-annual | 2025-11-15 | Compliant |
| OWASP Top 10 - A01 (Broken Access Control) | SRS-002, NFR-006 | Authorization checks | OWASP ZAP scanning | Quarterly | 2026-02-01 | Compliant |
| OWASP Top 10 - A02 (Cryptographic Failures) | NFR-007 | Encryption implementation | Security testing | Quarterly | 2026-02-01 | Compliant |
| OWASP Top 10 - A03 (Injection) | NFR-008 | Input validation | OWASP ZAP, Burp Suite | Quarterly | 2026-02-01 | Compliant |
| WCAG 2.1 Level AA | NFR-028 | Accessibility features | axe DevTools, manual testing | Quarterly | 2026-01-15 | Partial (85%) |
| ISO/IEC 25010 | SRS-015, NFR-001 to NFR-028 | Quality attributes | Compliance checklist | Annual | 2025-12-01 | Compliant |

# 10. Acceptance Criteria

## 10.1 Feature Acceptance Criteria

Feature 1: Code Review

\[ \] System analyzes PR within 30 seconds of creation

\[ \] Analysis completes within 2 minutes for repositories \< 50K LOC

\[ \] Issues are categorized into 4 severity levels

\[ \] Comments are posted to GitHub PR with file path and line number

\[ \] LLM provides actionable suggestions for each issue

\[ \] User can accept/dismiss feedback

\[ \] System handles syntax errors gracefully

\[ \] Fallback to secondary LLM on primary failure

Feature 2: Architecture Analysis

\[ \] Dependency graph is stored in Neo4j

\[ \] Circular dependencies are detected and highlighted

\[ \] Graph renders within 5 seconds for \< 1000 nodes

\[ \] User can zoom, pan, and filter graph

\[ \] Layer violations are identified

\[ \] Coupling metrics are calculated

\[ \] Graph can be exported as PNG/SVG

Feature 3: Authentication System

\[ \] User can register with email and password

\[ \] Password meets complexity requirements

\[ \] JWT tokens are generated on login

\[ \] Tokens expire after 24 hours

\[ \] Refresh tokens work for 7 days

\[ \] RBAC enforces permissions

\[ \] Account locks after 5 failed attempts

\[ \] OAuth 2.0 works with GitHub

Feature 4: Project Management

\[ \] User can add GitHub repository

\[ \] Webhook is configured automatically

\[ \] Repository list displays quality metrics

\[ \] Dashboard shows trends over time

\[ \] Reports can be exported as PDF

\[ \] Settings can be configured per project

\[ \] Audit log records all changes

# 11. Appendices

Appendix A: References

ISO/IEC 25010:2011 - Systems and software Quality Requirements and Evaluation (SQuaRE)

ISO/IEC 23396:2020 - Software and systems engineering --- Architectural design

OWASP Top 10 - 2021

GitHub REST API Documentation - https://docs.github.com/en/rest

OpenAI API Documentation - https://platform.openai.com/docs

Neo4j Graph Database Documentation - https://neo4j.com/docs/

JWT RFC 7519 - https://tools.ietf.org/html/rfc7519

Appendix B: Document Conventions

Must Have: Critical requirement for MVP release

Should Have: Important but not critical for MVP

Could Have: Desirable but can be deferred

Won\'t Have: Out of scope for current release

Appendix C: Comprehensive Terminology Glossary

**A**

**Abstract Syntax Tree (AST)**: A tree representation of the abstract syntactic structure of source code, where each node represents a construct occurring in the source code. Used for code analysis, transformation, and generation.

**Acceptance Criteria**: Specific conditions that must be met for a requirement to be considered complete and acceptable to stakeholders.

**Agentic AI**: Artificial intelligence system capable of autonomous reasoning, decision-making, and action execution within defined parameters, characterized by goal-directed behavior and contextual adaptation.

**API (Application Programming Interface)**: A set of protocols, tools, and definitions for building and integrating application software, enabling communication between different software components.

**Architectural Drift**: Progressive deviation of a software system\'s actual structure from its intended design, typically accumulating through small incremental changes that individually appear harmless but collectively compromise architectural integrity.

**Audit Log**: Chronological record of system activities, security events, and user actions, maintained for compliance, security analysis, and troubleshooting purposes.

**Authentication**: Process of verifying the identity of a user, device, or system, typically through credentials such as username/password, tokens, or biometric data.

**Authorization**: Process of determining whether an authenticated entity has permission to access a specific resource or perform a particular action.

**B**

**Baseline Configuration**: Formally reviewed and agreed-upon specification serving as the basis for further development, changeable only through formal change control. In this system, architectural baselines define expected structural patterns against which drift is measured.

**Bcrypt**: Password hashing function designed to be computationally expensive, incorporating a salt to protect against rainbow table attacks and featuring an adjustable cost factor to remain resistant to brute-force attacks as computing power increases.

**C**

**Celery**: Distributed task queue system for Python, enabling asynchronous execution of tasks across multiple worker processes or machines, commonly used for background job processing.

**Circular Dependency**: See Cyclic Dependency.

**Code Smell**: Surface indication of a deeper problem in the code, representing poor design choices or implementation practices that may not prevent the code from functioning but make it harder to maintain, understand, or extend.

**Compliance**: Adherence to laws, regulations, standards, and internal policies relevant to the system\'s operation, data handling, and security practices.

**Coupling**: Degree of interdependence between software modules. High coupling indicates strong dependencies, making the system harder to maintain and test. Low coupling is generally preferred for modularity.

**Coupling Anomaly**: Unauthorized or unexpected dependency relationship between software modules that violates architectural constraints, potentially compromising modularity, testability, or maintainability.

**Cyclic Dependency**: Circular reference pattern where Module A depends on Module B, which depends on Module C, which depends back on Module A, creating a dependency cycle that compromises system modularity and testing isolation.

**Cyclomatic Complexity**: Software metric measuring the number of linearly independent paths through a program\'s source code, used to assess code complexity and testing requirements.

**D**

**Dependency Graph**: Directed graph structure representing relationships between software components, where nodes represent modules/classes and edges represent dependencies (imports, function calls, inheritance).

**Dependency Injection**: Design pattern where dependencies are provided to a component from external sources rather than created internally, improving testability and modularity.

**Drift Detection**: Automated process of identifying deviations between a system\'s current architecture and its intended design baseline, typically through graph analysis and pattern matching.

**E**

**Encryption**: Process of converting data into a coded format to prevent unauthorized access, using algorithms and keys to ensure confidentiality during storage (at rest) and transmission (in transit).

**Explainable AI (XAI)**: AI techniques producing decisions, recommendations, or predictions accompanied by human-interpretable reasoning, enabling users to understand why the AI reached a particular conclusion.

**F**

**Fault Tolerance**: System\'s ability to continue operating correctly even when some components fail, typically through redundancy, failover mechanisms, and graceful degradation.

**G**

**GDPR (General Data Protection Regulation)**: European Union regulation governing data protection and privacy, establishing requirements for data collection, processing, storage, and user rights.

**Graph Database**: Database management system using graph structures with nodes, edges, and properties to represent and store data, optimized for querying relationships and traversing connected data patterns.

**H**

**Horizontal Scaling**: Increasing system capacity by adding more machines or instances rather than upgrading existing hardware (vertical scaling), enabling linear performance improvements.

**I**

**Idempotency**: Property of operations that produce the same result regardless of how many times they are executed, critical for reliable distributed systems and API design.

**J**

**JWT (JSON Web Token)**: Compact, URL-safe means of representing claims between two parties, commonly used for authentication and information exchange in web applications. Consists of header, payload, and signature.

**L**

**Large Language Model (LLM)**: AI system trained on vast text data for understanding and generating human-like text, capable of tasks such as code analysis, natural language understanding, and content generation.

**Layer Violation**: Architectural anti-pattern where code in one tier bypasses the immediately adjacent tier to access functionality in a non-adjacent tier, compromising separation of concerns (e.g., presentation layer directly accessing data layer).

**M**

**Microservices**: Architectural style structuring an application as a collection of loosely coupled, independently deployable services, each implementing specific business capabilities.

**N**

**Neo4j**: Graph database management system implementing the property graph model, optimized for storing and querying highly connected data with complex relationships.

**Non-Functional Requirement (NFR)**: Requirement specifying system qualities such as performance, security, usability, and reliability, rather than specific behaviors or functions.

**O**

**OAuth 2.0**: Industry-standard protocol for authorization, enabling applications to obtain limited access to user accounts on HTTP services without exposing user credentials.

**OWASP (Open Web Application Security Project)**: Nonprofit foundation focused on improving software security, best known for the OWASP Top 10 list of critical web application security risks.

**P**

**Pull Request (PR)**: Proposed code change submitted for review before merging into the main codebase, enabling collaborative code review and quality control.

**Q**

**Quality Gate**: Automated checkpoint in the development pipeline validating code against predefined quality criteria (test coverage, complexity metrics, security vulnerabilities) and blocking deployment if thresholds are not met.

**R**

**RBAC (Role-Based Access Control)**: Access control paradigm where permissions are associated with roles, and users are assigned to roles, simplifying permission management in complex systems.

**Redis**: In-memory data structure store used as database, cache, message broker, and queue, known for high performance and support for various data structures.

**Requirements Traceability Matrix (RTM)**: Document mapping relationships between requirements, design elements, code components, and test cases, ensuring complete coverage and impact analysis.

**REST (Representational State Transfer)**: Architectural style for distributed systems, commonly used for web APIs, characterized by stateless communication, resource-based URLs, and standard HTTP methods.

**S**

**Separation of Concerns**: Design principle dividing a system into distinct sections, each addressing a separate concern or responsibility, improving maintainability and modularity.

**SOC 2 (Service Organization Control 2)**: Auditing standard for service organizations\' security, availability, processing integrity, confidentiality, and privacy controls, commonly required for SaaS providers.

**Static Analysis**: Automated examination of source code without executing the program, identifying potential defects, security vulnerabilities, code smells, and compliance violations through pattern matching and rule-based evaluation.

**T**

**Technical Debt**: Implied cost of future refactoring work caused by choosing quick/easy solutions now instead of better approaches that would take longer, accumulating maintenance burden over time.

**TLS (Transport Layer Security)**: Cryptographic protocol providing secure communication over computer networks, successor to SSL, commonly used for HTTPS connections.

**Traceability**: Ability to trace relationships between requirements, design, implementation, and testing artifacts throughout the development lifecycle.

**U**

**Unit Test**: Automated test verifying the behavior of a small, isolated piece of code (typically a function or method) in isolation from dependencies.

**W**

**Webhook**: HTTP callback mechanism enabling real-time event notifications from one system to another, where the receiving system provides an endpoint URL that the sending system calls when specified events occur.

**X**

**XSS (Cross-Site Scripting)**: Security vulnerability allowing attackers to inject malicious scripts into web pages viewed by other users, potentially stealing data or hijacking sessions.


