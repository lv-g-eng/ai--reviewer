# Detailed Use Case Descriptions
## AI-Based Code Reviewer Platform

---

## UC-01: User Registration

| Field | Value |
|-------|-------|
| **Use Case ID** | UC-01 |
| **Use Case Name** | User Registration |
| **Created By** | BaiXuan Zhang |
| **Date Created** | 2026-02-07 |
| **Last Updated By** | BaiXuan Zhang |
| **Last Revision Date** | 2026-02-16 |
| **Actors** | Guest |
| **Priority** | Must Have |
| **Description** | Allows a guest user to create a new account on the AI-Based Reviewer platform to access code review and architecture analysis features. |
| **Trigger** | Guest clicks the 'Register' button on the landing page. |

### Preconditions
1. Guest is on the registration page
2. Guest has a valid email address
3. Guest has not previously registered with the same email

### Input Specification

| Input | Type | Constraint | Example |
|-------|------|------------|---------|
| Username | String | 3-30 characters, alphanumeric and underscore only, unique | john_dev123 |
| Email | Email | Valid email format, unique | john@example.com |
| Password | String | Minimum 8 characters, must contain uppercase, lowercase, number, and special character | SecurePass@123 |
| Confirm Password | String | Must match Password field | SecurePass@123 |

### Postconditions
- New user account is created in the database with role "User"
- Confirmation email is sent to the provided email address
- User is redirected to login page with success message
- Audit log entry is created

### Normal Flow

| User Action | System Response |
|-------------|-----------------|
| 1. User navigates to registration page | 2. System displays registration form with fields: username, email, password, confirm password |
| 3. User enters username, email, and password | 4. System validates input format in real-time and displays validation feedback |
| 5. User clicks 'Register' button | 6. System checks for duplicate username/email in database |
| | 7. System encrypts password using bcrypt (cost factor 12) |
| | 8. System creates user record in PostgreSQL with default role "User" |
| | 9. System generates email verification token |
| | 10. System sends confirmation email with verification link |
| | 11. System displays success message: "Registration successful! Please check your email to verify your account." |
| | 12. System redirects to login page after 3 seconds |

### Alternative Flows

**3A. Invalid Input Format**
- 3A.1. System detects invalid input (e.g., email format, password strength)
- 3A.2. System displays inline error message with specific requirement
- 3A.3. User corrects input
- 3A.4. Resume at step 5

**6A. Duplicate Username or Email**
- 6A.1. System detects existing username or email
- 6A.2. System displays error: "Username/Email already exists. Please use a different one or login."
- 6A.3. User modifies input
- 6A.4. Resume at step 5

**10A. Email Sending Failure**
- 10A.1. System fails to send confirmation email
- 10A.2. System logs error and queues email for retry
- 10A.3. System displays message: "Account created. Verification email will be sent shortly."
- 10A.4. System redirects to login page

### Exception Flows

**E1. Database Connection Failure**
- E1.1. System cannot connect to database
- E1.2. System displays error: "Service temporarily unavailable. Please try again later."
- E1.3. System logs error for administrator review
- E1.4. Use case ends

**E2. System Overload**
- E2.1. System detects high load (> 1000 registrations/minute)
- E2.2. System implements rate limiting
- E2.3. System displays: "Too many registration attempts. Please try again in 5 minutes."
- E2.4. Use case ends

### Business Rules
- BR-01: Username must be unique across the system
- BR-02: Email must be unique across the system
- BR-03: Password must meet complexity requirements
- BR-04: New users are assigned "User" role by default
- BR-05: Email verification is required before full access

---

## UC-02: User Login

| Field | Value |
|-------|-------|
| **Use Case ID** | UC-02 |
| **Use Case Name** | User Login |
| **Actors** | User, Programmer, Reviewer, Manager, Administrator |
| **Priority** | Must Have |
| **Description** | Allows registered users to authenticate and access the platform using their credentials. |
| **Trigger** | User navigates to login page and enters credentials. |

### Preconditions
1. User has a registered account
2. User's account is active (not suspended)
3. User's email is verified

### Input Specification

| Input | Type | Constraint | Example |
|-------|------|------------|---------|
| Email/Username | String | Valid email or username | john@example.com or john_dev123 |
| Password | String | User's password | SecurePass@123 |
| Remember Me | Boolean | Optional, default false | true |

### Postconditions
- User is authenticated and session is created
- JWT access token (24-hour expiry) and refresh token (7-day expiry) are generated
- User is redirected to dashboard
- Last login timestamp is updated
- Login event is logged in audit log

### Normal Flow

| User Action | System Response |
|-------------|-----------------|
| 1. User navigates to login page | 2. System displays login form with email/username and password fields |
| 3. User enters credentials and clicks 'Login' | 4. System validates input format |
| | 5. System queries database for user record |
| | 6. System verifies password using bcrypt comparison |
| | 7. System checks account status (active, email verified) |
| | 8. System generates JWT access token (24h) and refresh token (7d) |
| | 9. System updates last_login timestamp |
| | 10. System creates audit log entry |
| | 11. System returns tokens in HTTP-only secure cookies |
| | 12. System redirects to dashboard |

### Alternative Flows

**6A. Invalid Credentials**
- 6A.1. Password does not match stored hash
- 6A.2. System increments failed login counter
- 6A.3. System displays: "Invalid email/username or password"
- 6A.4. If failed attempts < 5, resume at step 3
- 6A.5. If failed attempts >= 5, go to flow 6B

**6B. Account Lockout**
- 6B.1. System locks account for 30 minutes
- 6B.2. System sends email notification to user
- 6B.3. System displays: "Account locked due to multiple failed login attempts. Try again in 30 minutes or reset your password."
- 6B.4. Use case ends

**7A. Unverified Email**
- 7A.1. System detects email not verified
- 7A.2. System displays: "Please verify your email address. Resend verification email?"
- 7A.3. User clicks 'Resend'
- 7A.4. System sends new verification email
- 7A.5. Use case ends

**7B. Suspended Account**
- 7B.1. System detects account is suspended
- 7B.2. System displays: "Your account has been suspended. Contact support for assistance."
- 7B.3. Use case ends

### Business Rules
- BR-06: JWT access tokens expire after 24 hours
- BR-07: Refresh tokens expire after 7 days
- BR-08: Account locks after 5 failed login attempts
- BR-09: Lockout duration is 30 minutes
- BR-10: All login attempts are logged for security audit

---

## UC-03: Add GitHub Repository

| Field | Value |
|-------|-------|
| **Use Case ID** | UC-03 |
| **Use Case Name** | Add GitHub Repository |
| **Actors** | User, Programmer, Reviewer, Manager, Administrator |
| **Priority** | Must Have |
| **Description** | Allows authenticated users to connect a GitHub repository to the platform for automated code analysis. |
| **Trigger** | User clicks 'Add Repository' button on dashboard. |

### Preconditions
1. User is authenticated
2. User has GitHub account
3. User has admin access to the target repository
4. Repository is not already added to the platform

### Input Specification

| Input | Type | Constraint | Example |
|-------|------|------------|---------|
| GitHub URL | URL | Format: https://github.com/{owner}/{repo} | https://github.com/user/my-project |
| Default Branch | String | Valid branch name, default: main | main |
| Analysis Config | JSON | Optional configuration | {"enabled_rules": ["security", "performance"]} |

### Postconditions
- Repository is added to user's project list
- GitHub OAuth authorization is completed
- Webhook is configured on GitHub repository
- Initial repository scan is queued
- Project appears in dashboard

### Normal Flow

| User Action | System Response |
|-------------|-----------------|
| 1. User clicks 'Add Repository' | 2. System displays repository addition form |
| 3. User enters GitHub repository URL | 4. System validates URL format |
| | 5. System checks if repository already exists in system |
| | 6. System initiates GitHub OAuth flow |
| 7. User authorizes application on GitHub | 8. System receives OAuth callback with access token |
| | 9. System verifies user has admin access to repository |
| | 10. System fetches repository metadata (name, description, languages) |
| | 11. System generates webhook secret |
| | 12. System configures webhook on GitHub repository |
| | 13. System creates project record in PostgreSQL |
| | 14. System queues initial repository scan task |
| | 15. System displays success message and redirects to project page |

### Alternative Flows

**5A. Repository Already Exists**
- 5A.1. System detects repository URL already in database
- 5A.2. System displays: "This repository is already connected. View project?"
- 5A.3. User clicks 'View Project'
- 5A.4. System redirects to existing project page
- 5A.5. Use case ends

**9A. Insufficient Permissions**
- 9A.1. System detects user does not have admin access
- 9A.2. System displays: "You need admin access to this repository. Please contact the repository owner."
- 9A.3. Use case ends

**12A. Webhook Configuration Failure**
- 12A.1. GitHub API returns error when creating webhook
- 12A.2. System logs error details
- 12A.3. System displays: "Repository added but webhook configuration failed. Please configure manually or contact support."
- 12A.4. System provides manual webhook setup instructions
- 12A.5. Use case continues to step 13

### Business Rules
- BR-11: User must have GitHub admin access to add repository
- BR-12: Each repository can only be added once per platform instance
- BR-13: Webhook events monitored: pull_request (opened, synchronize, closed)
- BR-14: Initial scan analyzes default branch only
- BR-15: OAuth tokens are encrypted before storage

---


## UC-04: Automated Pull Request Review

| Field | Value |
|-------|-------|
| **Use Case ID** | UC-04 |
| **Use Case Name** | Automated Pull Request Review |
| **Actors** | System (automated), Programmer (receives feedback) |
| **Priority** | Must Have |
| **Description** | System automatically analyzes pull requests when created or updated, providing AI-powered code review feedback. |
| **Trigger** | GitHub webhook receives pull_request event (opened or synchronize). |

### Preconditions
1. Repository is connected to platform
2. Webhook is properly configured
3. Pull request contains code changes
4. Analysis workers are available

### Input Specification

| Input | Type | Source | Example |
|-------|------|--------|---------|
| PR Number | Integer | GitHub webhook | 42 |
| Repository | String | GitHub webhook | user/my-project |
| Changed Files | Array | GitHub API | ["src/main.py", "tests/test_main.py"] |
| Diff Content | String | GitHub API | "+def new_function():\n+    return True" |

### Postconditions
- Analysis is completed and stored in database
- Review comments are posted to GitHub PR
- Issues are categorized by severity
- Dependency graph is updated
- Notification is sent to PR author

### Normal Flow

| System Action | Details |
|---------------|---------|
| 1. System receives webhook event | Validates webhook signature using HMAC-SHA256 |
| 2. System extracts PR information | PR number, repository, author, branch, changed files |
| 3. System queues analysis task in Redis | Priority based on repository settings |
| 4. Analysis worker picks up task | Within 30 seconds of queuing |
| 5. Worker fetches PR diff from GitHub | Using GitHub API with OAuth token |
| 6. Worker parses changed files | Generates AST for each file |
| 7. Worker extracts code entities | Functions, classes, imports, dependencies |
| 8. Worker queries Neo4j for context | Existing dependencies, architectural patterns |
| 9. Worker builds LLM prompt | Code + context + compliance rules |
| 10. Worker sends request to LLM API | GPT-4 or Claude 3.5 with fallback |
| 11. Worker parses LLM response | Extracts issues, severity, suggestions |
| 12. Worker categorizes issues | Critical, High, Medium, Low |
| 13. Worker stores results in PostgreSQL | Analysis record with issues |
| 14. Worker updates dependency graph in Neo4j | New nodes and relationships |
| 15. Worker posts comments to GitHub PR | Grouped by file and severity |
| 16. Worker sends notification | Email/Slack to PR author |
| 17. System marks task as completed | Updates task status in Redis |

### Alternative Flows

**5A. GitHub API Rate Limit**
- 5A.1. GitHub API returns 403 rate limit error
- 5A.2. System calculates wait time from X-RateLimit-Reset header
- 5A.3. System requeues task with delay
- 5A.4. System logs rate limit event
- 5A.5. Resume at step 5 after delay

**10A. LLM API Failure**
- 10A.1. Primary LLM API (GPT-4) fails or times out
- 10A.2. System switches to secondary LLM (Claude 3.5)
- 10A.3. If secondary also fails, use rule-based analysis only
- 10A.4. System logs API failure
- 10A.5. Resume at step 11 with available results

**10B. LLM API Rate Limit**
- 10B.1. LLM API returns rate limit error
- 10B.2. System implements exponential backoff
- 10B.3. System requeues task with delay
- 10B.4. Resume at step 10 after delay

**15A. GitHub Comment Posting Failure**
- 15A.1. GitHub API fails to post comment
- 15A.2. System retries up to 3 times with exponential backoff
- 15A.3. If all retries fail, store comments in database only
- 15A.4. System notifies user via email with link to view results
- 15A.5. Continue to step 16

### Exception Flows

**E1. Parse Error**
- E1.1. AST parser fails due to syntax errors
- E1.2. System creates issue noting syntax error
- E1.3. System skips LLM analysis for unparseable files
- E1.4. Continue with parseable files

**E2. Analysis Timeout**
- E2.1. Analysis exceeds 5-minute timeout
- E2.2. System terminates analysis worker
- E2.3. System marks analysis as failed
- E2.4. System posts comment: "Analysis timed out. Please reduce PR size or contact support."
- E2.5. Use case ends

**E3. Worker Crash**
- E3.1. Analysis worker crashes unexpectedly
- E3.2. Task remains in "processing" state
- E3.3. Monitoring system detects stale task (> 10 minutes)
- E3.4. System requeues task with retry counter incremented
- E3.5. If retry count > 3, mark as failed and notify admin
- E3.6. Resume at step 4 or end use case

### Business Rules
- BR-16: Analysis must start within 30 seconds of PR creation
- BR-17: Analysis must complete within 5 minutes or timeout
- BR-18: Critical issues block PR merge (configurable)
- BR-19: LLM API calls are rate-limited to 10 requests/minute
- BR-20: Failed analyses retry up to 3 times with exponential backoff

---

## UC-05: View Dependency Graph

| Field | Value |
|-------|-------|
| **Use Case ID** | UC-05 |
| **Use Case Name** | View Interactive Dependency Graph |
| **Actors** | Programmer, Reviewer, Manager, Administrator |
| **Priority** | Should Have |
| **Description** | Allows users to visualize and interact with the project's dependency graph to understand architectural structure and identify issues. |
| **Trigger** | User clicks 'Architecture' tab on project page. |

### Preconditions
1. User is authenticated
2. User has access to the project
3. Project has been analyzed at least once
4. Dependency graph exists in Neo4j

### Input Specification

| Input | Type | Constraint | Example |
|-------|------|------------|---------|
| Project ID | UUID | Valid project identifier | 550e8400-e29b-41d4-a716-446655440000 |
| Filter Options | JSON | Optional filters | {"entity_type": "class", "min_complexity": 5} |
| Layout Algorithm | Enum | force, hierarchical, circular | force |

### Postconditions
- Dependency graph is rendered in browser
- User can interact with graph (zoom, pan, filter)
- Circular dependencies are highlighted
- Graph can be exported as image

### Normal Flow

| User Action | System Response |
|-------------|-----------------|
| 1. User navigates to Architecture tab | 2. System displays loading indicator |
| | 3. System queries Neo4j for project dependencies |
| | 4. System retrieves nodes (entities) and edges (dependencies) |
| | 5. System calculates graph metrics (complexity, coupling) |
| | 6. System detects circular dependencies using graph algorithms |
| | 7. System serializes graph data to JSON |
| | 8. System sends graph data to frontend |
| 9. Frontend renders graph using D3.js | 10. System applies force-directed layout algorithm |
| | 11. System highlights circular dependencies in red |
| | 12. System displays legend and controls |
| 13. User interacts with graph | 14. System responds to interactions: |
| - Zoom in/out | - Scales graph (0.1x to 10x) |
| - Pan | - Translates viewport |
| - Click node | - Shows entity details in sidebar |
| - Hover edge | - Shows dependency type and strength |
| - Apply filter | - Redraws graph with filtered data |
| 15. User clicks 'Export' | 16. System generates PNG/SVG image |
| | 17. System triggers browser download |

### Alternative Flows

**3A. Large Graph (> 1000 nodes)**
- 3A.1. System detects graph size exceeds threshold
- 3A.2. System displays warning: "Large graph detected. Consider applying filters."
- 3A.3. System offers predefined filter options
- 3A.4. User selects filter or proceeds without filtering
- 3A.5. Resume at step 4 with filtered query

**6A. No Circular Dependencies**
- 6A.1. System finds no circular dependencies
- 6A.2. System displays success badge: "No circular dependencies detected"
- 6A.3. Continue to step 7

**6B. Multiple Circular Dependencies**
- 6B.1. System detects multiple cycles
- 6B.2. System highlights all cycles in different colors
- 6B.3. System lists cycles in sidebar with severity
- 6B.4. Continue to step 7

### Business Rules
- BR-21: Graph rendering must complete within 5 seconds for < 1000 nodes
- BR-22: Circular dependencies are highlighted in red
- BR-23: Node size represents complexity (larger = more complex)
- BR-24: Edge thickness represents dependency strength
- BR-25: Graph data is cached for 5 minutes

---

## UC-06: View Quality Dashboard

| Field | Value |
|-------|-------|
| **Use Case ID** | UC-06 |
| **Use Case Name** | View Quality Metrics Dashboard |
| **Actors** | Manager, Administrator |
| **Priority** | Should Have |
| **Description** | Allows managers to view comprehensive quality metrics, trends, and reports for projects. |
| **Trigger** | User navigates to Dashboard page. |

### Preconditions
1. User is authenticated with Manager or Administrator role
2. User has access to at least one project
3. Projects have historical analysis data

### Postconditions
- Dashboard displays current quality metrics
- Trends are visualized over time
- Reports can be exported

### Normal Flow

| User Action | System Response |
|-------------|-----------------|
| 1. User navigates to Dashboard | 2. System queries PostgreSQL for user's projects |
| | 3. System retrieves latest quality metrics for each project |
| | 4. System calculates aggregate statistics |
| | 5. System queries historical data for trend analysis |
| | 6. System renders dashboard with charts and tables |
| 7. User selects time range (7d, 30d, 90d) | 8. System updates charts with filtered data |
| 9. User clicks on project | 10. System displays detailed project metrics |
| 11. User clicks 'Export Report' | 12. System generates PDF report |
| | 13. System includes: quality score, issue breakdown, trends, recommendations |
| | 14. System triggers download |

### Business Rules
- BR-26: Dashboard loads within 3 seconds
- BR-27: Metrics updated every 5 minutes
- BR-28: Historical data retained for 1 year
- BR-29: Reports include executive summary and detailed analysis

---

## UC-07: Configure Analysis Settings

| Field | Value |
|-------|-------|
| **Use Case ID** | UC-07 |
| **Use Case Name** | Configure Analysis Settings |
| **Actors** | Administrator |
| **Priority** | Must Have |
| **Description** | Allows administrators to configure analysis rules, compliance standards, and system behavior. |
| **Trigger** | Administrator navigates to Settings page. |

### Preconditions
1. User is authenticated with Administrator role
2. User has system configuration permissions

### Postconditions
- Settings are saved to database
- Changes apply to new analyses
- Audit log records configuration changes

### Normal Flow

| User Action | System Response |
|-------------|-----------------|
| 1. Admin navigates to Settings | 2. System displays current configuration |
| 3. Admin modifies settings | 4. System validates input in real-time |
| 5. Admin clicks 'Save' | 6. System validates all settings |
| | 7. System saves to database |
| | 8. System creates audit log entry |
| | 9. System displays success message |
| | 10. System notifies affected services |

### Business Rules
- BR-30: All configuration changes are audited
- BR-31: Settings changes require admin role
- BR-32: Invalid settings are rejected with clear error messages
- BR-33: Settings can be exported/imported as JSON

