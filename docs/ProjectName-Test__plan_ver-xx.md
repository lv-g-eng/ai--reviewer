**\[AI-Based Reviewer on Project Code and Architecture\] - Software Test Plan Template**

**Document Name:** \[e.g., EV_Better TestPlan_v3.1\] **Owner:** \[Names of responsible members\] **Version:** \[e.g., v3.1\] **Date:** \[Submission Date\]

**Document History**

  ------------- ------------ --------------- --------------- -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  **Version**   **Date**     **Author**      **Reviewer**    **Changes**

  v1.0          2026-02-07   BaiXuan Zhang   Dr. Siraprapa   Initial draft

  v2.1          2026-02-19   BaiXuan Zhang   Dr. Siraprapa   Complete revision with RBAC authentication, property-based testing, comprehensive test coverage; added STC-SEC-04 to STC-SEC-06, Section 6 test data, Section 7 defect management, Section 8 metrics, Section 9 entry/exit criteria, Section 10 risks

  v3.0          2026-02-20   BaiXuan Zhang   Dr. Siraprapa   Final version with complete IEEE 829 and ISO/IEC 29119 compliance; added Sections 12-22 including test organization RACI, environment topology, complete test type coverage, WBS, suspension/resumption criteria, quantified exit criteria, automation framework, defect lifecycle, deliverables, reporting standards, data security
  ------------- ------------ --------------- --------------- -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# 1. Introduction 

## 1.1 Purpose

This document establishes a comprehensive testing plan for the AI-Based Reviewer platform, including unit testing, integration testing, property-based testing, and system testing strategies to discover and address potential defects before deployment. The plan covers both the core code review functionality and the enterprise RBAC authentication system.

**1.2 Scope**

This test plan covers white-box and black-box testing activities used to verify all user requirements (URS) and system requirements (SRS). Testing includes:

\- **Functional Requirements:** Code review, architecture analysis, authentication, authorization, project management

\- **Non-Functional Requirements:** Performance, security, usability, reliability, maintainability

\- **Integration Testing:** GitHub API, LLM APIs, Neo4j, PostgreSQL, Redis

\- **Property-Based Testing:** 36 correctness properties for RBAC authentication system

\- **Security Testing:** Authentication, authorization, audit logging, input validation

**1.3 Acronyms and Definitions**

-   **UTC:** Unit Test Case.

-   **ITC:** Integration Test Case.

-   **STC:** System Test Case.

-   **PBT:** Property-Based Test

-   **TD:** Test Data.

-   **API:** Application Programming Interface

-   **AST:** Abstract Syntax Tree

-   **LLM:** Large Language Model

-   **RBAC:** Role-Based Access Control

-   **NFR:** Non-Functional Requirement

# 2. Test Plan and Procedures

## 2.1 Test Objectives

-   Detect and fix all critical and high-severity bugs before production release

-   Verify coverage of all functional requirements (100% of URS)

-   Validate all 36 correctness properties for RBAC authentication

-   Validate non-functional requirements (performance, security, scalability)

-   Ensure integration with external services (GitHub, LLM APIs) functions correctly

-   Achieve minimum 80% code coverage for critical components

-   Verify security controls meet OWASP Top 10 standards

## 2.2 Scope of Testing

**Unit Testing**

**Backend Components:**

-   AST Parser functions (Python, JavaScript, TypeScript, Java, Go)

-   Graph Analysis algorithms (circular dependency detection, coupling metrics)

-   Authentication service (password hashing, JWT generation/validation)

-   RBAC service (permission checking, role management)

-   Audit service (log creation, querying, filtering)

-   Data validation functions

-   Middleware components (authentication, authorization)

**Frontend Components:**

-   Authentication utilities (login, token management)

-   Route guards (permission checking, redirection)

-   Permission HOC components

-   Form validation

-   API client functions

**Integration Testing**

**External Service Integration:**

-   GitHub API integration (webhooks, PR comments, repository access)

-   LLM API integration (GPT-4, Claude 3.5 Sonnet)

-   Database operations (PostgreSQL transactions, Neo4j graph queries)

-   Redis queue operations (task queuing, caching)

**Internal Service Integration:**

-   Authentication → Authorization flow

-   Code Review Engine → Architecture Analyzer

-   Analysis Service → Audit Service

-   Frontend → Backend API

**Property-Based Testing**

**RBAC Authentication System (36 Properties):**

-   Authentication properties (5): Valid/invalid credentials, logout, token expiration, password hashing

-   RBAC properties (6): Role assignment, permissions, project ownership, access control

-   Authorization middleware properties (4): Token validation, role matching, error responses

-   Project isolation properties (3): Ownership checks, admin bypass, access grants

-   Frontend route protection properties (5): Route guards, conditional rendering, session expiration

-   Audit logging properties (4): Log completeness, persistence, immutability, filtering

-   User management properties (5): Field validation, role updates, session invalidation

-   Session management properties (4): Session creation, concurrent sessions, password change, token refresh

**System Testing**

**End-to-End User Workflows:**

-   User registration and login

-   Repository addition and webhook configuration

-   Pull request review workflow

-   Architecture visualization and analysis

-   Metrics dashboard functionality

-   Configuration management

-   User and role management (admin)

-   Project access control

## 2.3 Test Duration

  -----------------------------------------------------------------------------
  **Test Phase**                **Duration**            **Timeline**
  ----------------------------- ----------------------- -----------------------
  **Unit Testing**              2 weeks                 Week 1-2 of Mar 2026

  **Property-Based Testing**    1 week                  Week 3 of Mar 2026

  **Integration Testing**       1 week                  Week 4 of Mar 2026

  **System Testing**            2 weeks                 Week 1-2 of Apr 2026

  **Security Testing**          1 week                  Week 3 of Apr 2026

  **Performance Testing**       1 week                  Week 4 of Apr 2026

  **User Acceptance Testing**   1 week                  Week 1 of May 2026
  -----------------------------------------------------------------------------

**Total Duration:** 9 weeks

## 2.4 Test Responsibility

  -----------------------------------------------------------------------------------------------------------
  **Role**                            **Responsibility**
  ----------------------------------- -----------------------------------------------------------------------
  **Test Lead**                       Overall test strategy, coordination, reporting, quality gates

  **Backend Developer**               Unit tests for API services, AST parser, graph analysis, RBAC system

  **Frontend Developer**              UI component tests, integration tests for frontend, route guard tests

  **QA Engineer**                     System testing, test record documentation, test data management

  **Security Engineer**               Security testing, penetration testing, vulnerability assessment

  **DevOps Engineer**                 Performance testing, load testing, CI/CD pipeline integration
  -----------------------------------------------------------------------------------------------------------

## 2.5 Test Strategy

**White-box Testing**

**Unit Tests:**

-   Framework: pytest (Python), Jest (JavaScript/TypeScript)

-   Code coverage analysis with pytest-cov and Jest coverage

-   Mocking external dependencies (GitHub API, LLM APIs, databases)

-   Test isolation with fixtures and setup/teardown

-   Minimum 80% code coverage for critical components

**Property-Based Tests:**

-   Framework: Hypothesis (Python), fast-check (TypeScript)

-   Minimum 100 iterations per property

-   Randomized input generation

-   Shrinking to minimal failing examples

-   All 36 RBAC properties must pass

**Black-box Testing**

**System Testing:**

-   Based on use cases and user stories

-   Boundary value analysis for input validation

-   Equivalence partitioning for test data

-   Error guessing for edge cases

-   Exploratory testing for usability

**Security Testing:**

-   OWASP Top 10 vulnerability scanning

-   Authentication and authorization testing

-   Input validation and sanitization testing

-   SQL injection and XSS testing

-   Session management testing

-   Audit log verification

**Automated Testing**

**Continuous Integration:**

-   GitHub Actions for automated test execution

-   Automated regression testing on each commit

-   Quality gates: All tests must pass before merge

-   Code coverage reports on pull requests

-   Automated security scanning with Snyk

**Performance Testing:**

-   Load testing with Locust

-   Stress testing for peak load scenarios

-   Endurance testing for memory leaks

-   Spike testing for sudden load increases

-   Target: 99.5% uptime, \< 500ms API response time

## 2.6 Test Environment

**Hardware**

**Development:**

-   MacBook Pro M2, 16GB RAM (local development)

-   Windows 10/11, 16GB RAM (local development)

**Staging:**

-   AWS EC2 t3.medium instances (2 vCPU, 4GB RAM)

-   AWS RDS PostgreSQL db.t3.medium

-   AWS ElastiCache Redis cache.t3.micro

-   Neo4j AuraDB Professional

**Production:**

-   AWS EC2 t3.large instances (2 vCPU, 8GB RAM)

-   Auto-scaling group (2-10 instances)

-   AWS RDS PostgreSQL db.t3.large (Multi-AZ)

-   AWS ElastiCache Redis cache.t3.small (Multi-AZ)

-   Neo4j AuraDB Enterprise

**Software**

**Operating Systems:**

-   macOS Sonoma 14.0+

-   Ubuntu 24.04 LTS

-   Windows 10/11

**Browsers:**

-   Chrome 120+

-   Firefox 121+

-   Safari 17+

-   Edge 120+

**Development Tools:**

-   Python 3.11+

-   Node.js 20+

-   PostgreSQL 15

-   Neo4j 5.x

-   Redis 7.x

-   Docker 24.x

-   Kubernetes 1.28+

# 3. Unit Test Plan

## 3.1 Authentication Service Tests

**Test Module:** test_auth_service.py

  ---------------------------------------------------------------------------------------
  **UTC ID**        **Description**                   **Test Type**     **Priority**
  ----------------- --------------------------------- ----------------- -----------------
  UTC-AUTH-001      Password hashing with bcrypt      Unit              Critical

  UTC-AUTH-002      Password verification (valid)     Unit              Critical

  UTC-AUTH-003      Password verification (invalid)   Unit              Critical

  UTC-AUTH-004      JWT token generation              Unit              Critical

  UTC-AUTH-005      JWT token validation (valid)      Unit              Critical

  UTC-AUTH-006      JWT token validation (expired)    Unit              Critical

  UTC-AUTH-007      JWT token validation (tampered)   Unit              Critical

  UTC-AUTH-008      Login with valid credentials      Unit              Critical

  UTC-AUTH-009      Login with invalid credentials    Unit              Critical

  UTC-AUTH-010      Logout and session invalidation   Unit              Critical

  UTC-AUTH-011      Token refresh before expiration   Unit              High

  UTC-AUTH-012      Token refresh after expiration    Unit              High
  ---------------------------------------------------------------------------------------

**Property-Based Tests:**

-   PBT-AUTH-001: Property 1 - Valid credentials generate valid JWT tokens (100 iterations)

-   PBT-AUTH-002: Property 2 - Invalid credentials are rejected (100 iterations)

-   PBT-AUTH-003: Property 3 - Logout invalidates sessions (100 iterations)

-   PBT-AUTH-004: Property 4 - Expired tokens require re-authentication (100 iterations)

-   PBT-AUTH-005: Property 5 - Passwords are never stored in plaintext (100 iterations)

## 3.2 RBAC Service Tests

**Test Module:** test_rbac_service.py

  --------------------------------------------------------------------------------------------
  **UTC ID**        **Description**                        **Test Type**     **Priority**
  ----------------- -------------------------------------- ----------------- -----------------
  UTC-RBAC-001      Check permission for Admin role        Unit              Critical

  UTC-RBAC-002      Check permission for Programmer role   Unit              Critical

  UTC-RBAC-003      Check permission for Visitor role      Unit              Critical

  UTC-RBAC-004      Get role permissions mapping           Unit              High

  UTC-RBAC-005      Assign role to user                    Unit              Critical

  UTC-RBAC-006      Validate role enum values              Unit              High

  UTC-RBAC-007      Check project access (owner)           Unit              Critical

  UTC-RBAC-008      Check project access (granted)         Unit              Critical

  UTC-RBAC-009      Check project access (denied)          Unit              Critical

  UTC-RBAC-010      Admin bypass project isolation         Unit              Critical

  UTC-RBAC-011      Grant project access                   Unit              High

  UTC-RBAC-012      Revoke project access                  Unit              High
  --------------------------------------------------------------------------------------------

**Property-Based Tests:**

-   PBT-RBAC-001: Property 6 - Users have exactly one role (100 iterations)

-   PBT-RBAC-002: Property 7 - Admin users have all permissions (100 iterations)

-   PBT-RBAC-003: Property 10 - Visitors cannot modify resources (100 iterations)

-   PBT-RBAC-004: Property 16 - Project access requires ownership or grant (100 iterations)

-   PBT-RBAC-005: Property 17 - Admins bypass project isolation (100 iterations)

-   PBT-RBAC-006: Property 18 - Access grants enable project access (100 iterations)

-   PBT-RBAC-007: Property 29 - Role updates apply immediately (100 iterations)

-   PBT-RBAC-008: Property 32 - Authorization checks verify role permissions (100 iterations)

## 3.3 Audit Service Tests

**Test Module:** test_audit_service.py

  -----------------------------------------------------------------------------------------
  **UTC ID**        **Description**                     **Test Type**     **Priority**
  ----------------- ----------------------------------- ----------------- -----------------
  UTC-AUDIT-001     Create audit log entry              Unit              Critical

  UTC-AUDIT-002     Query logs with user filter         Unit              High

  UTC-AUDIT-003     Query logs with action filter       Unit              High

  UTC-AUDIT-004     Query logs with date range filter   Unit              High

  UTC-AUDIT-005     Query logs with pagination          Unit              High

  UTC-AUDIT-006     Get user-specific logs              Unit              High

  UTC-AUDIT-007     Verify log immutability             Unit              Critical
  -----------------------------------------------------------------------------------------

**Property-Based Tests:**

-   PBT-AUDIT-001: Property 24 - Audit logs contain required fields (100 iterations)

-   PBT-AUDIT-002: Property 25 - Audit logs persist immediately (100 iterations)

-   PBT-AUDIT-003: Property 26 - Users cannot modify audit logs (100 iterations)

-   PBT-AUDIT-004: Property 27 - Audit log queries filter correctly (100 iterations)

## 3.4 Authorization Middleware Tests

**Test Module:** test_auth_middleware.py

  -------------------------------------------------------------------------------------------
  **UTC ID**        **Description**                       **Test Type**     **Priority**
  ----------------- ------------------------------------- ----------------- -----------------
  UTC-MW-001        Authenticate valid JWT token          Unit              Critical

  UTC-MW-002        Reject invalid JWT token              Unit              Critical

  UTC-MW-003        Reject missing JWT token              Unit              Critical

  UTC-MW-004        Check role - matching role            Unit              Critical

  UTC-MW-005        Check role - non-matching role        Unit              Critical

  UTC-MW-006        Check permission - has permission     Unit              Critical

  UTC-MW-007        Check permission - lacks permission   Unit              Critical

  UTC-MW-008        Check project access - owner          Unit              Critical

  UTC-MW-009        Check project access - granted        Unit              Critical

  UTC-MW-010        Check project access - denied         Unit              Critical
  -------------------------------------------------------------------------------------------

**Property-Based Tests:**

-   PBT-MW-001: Property 13 - Matching roles grant access (100 iterations)

-   PBT-MW-002: Property 14 - Non-matching roles return 403 (100 iterations)

-   PBT-MW-003: Property 15 - Invalid tokens return 401 (100 iterations)

## 3.5 AST Parser Tests

**Test Module:** test_ast_parser.py

  ---------------------------------------------------------------------------------------
  **UTC ID**        **Description**                   **Test Type**     **Priority**
  ----------------- --------------------------------- ----------------- -----------------
  UTC-AST-001       Parse Python file                 Unit              Critical

  UTC-AST-002       Parse JavaScript file             Unit              Critical

  UTC-AST-003       Parse TypeScript file             Unit              Critical

  UTC-AST-004       Parse Java file                   Unit              High

  UTC-AST-005       Parse Go file                     Unit              High

  UTC-AST-006       Extract imports/dependencies      Unit              Critical

  UTC-AST-007       Extract function definitions      Unit              Critical

  UTC-AST-008       Extract class definitions         Unit              Critical

  UTC-AST-009       Handle syntax errors gracefully   Unit              High

  UTC-AST-010       Calculate cyclomatic complexity   Unit              High
  ---------------------------------------------------------------------------------------

## 3.6 Graph Analysis Tests

**Test Module:** test_graph_analysis.py

  ------------------------------------------------------------------------------------
  **UTC ID**        **Description**                **Test Type**     **Priority**
  ----------------- ------------------------------ ----------------- -----------------
  UTC-GRAPH-001     Detect circular dependencies   Unit              Critical

  UTC-GRAPH-002     Calculate coupling metrics     Unit              High

  UTC-GRAPH-003     Identify layer violations      Unit              High

  UTC-GRAPH-004     Build dependency graph         Unit              Critical

  UTC-GRAPH-005     Query graph relationships      Unit              High

  UTC-GRAPH-006     Update graph on code changes   Unit              High
  ------------------------------------------------------------------------------------

# 4. Integration Test Plan

## 4.1 GitHub API Integration

**Test Module:** test_github_integration.py

  ---------------------------------------------------------------------------------
  **ITC ID**              **Description**                   **Priority**
  ----------------------- --------------------------------- -----------------------
  ITC-GH-001              Configure webhook on repository   Critical

  ITC-GH-002              Receive PR opened webhook         Critical

  ITC-GH-003              Receive PR synchronized webhook   Critical

  ITC-GH-004              Fetch PR diff from GitHub         Critical

  ITC-GH-005              Post review comments to PR        Critical

  ITC-GH-006              Verify webhook signature          Critical

  ITC-GH-007              Handle webhook retry              High

  ITC-GH-008              OAuth authorization flow          Critical
  ---------------------------------------------------------------------------------

## 4.2 LLM API Integration

**Test Module:** test_llm_integration.py

  --------------------------------------------------------------------------------------
  **ITC ID**              **Description**                        **Priority**
  ----------------------- -------------------------------------- -----------------------
  ITC-LLM-001             Send code analysis request to GPT-4    Critical

  ITC-LLM-002             Send code analysis request to Claude   Critical

  ITC-LLM-003             Parse LLM response                     Critical

  ITC-LLM-004             Handle rate limiting                   High

  ITC-LLM-005             Fallback to secondary model            High

  ITC-LLM-006             Handle API timeout                     High

  ITC-LLM-007             Token counting and limits              High
  --------------------------------------------------------------------------------------

## 4.3 Database Integration

**Test Module:** test_database_integration.py

  ------------------------------------------------------------------------------------
  **ITC ID**              **Description**                      **Priority**
  ----------------------- ------------------------------------ -----------------------
  ITC-DB-001              PostgreSQL connection and queries    Critical

  ITC-DB-002              Neo4j connection and graph queries   Critical

  ITC-DB-003              Redis connection and caching         Critical

  ITC-DB-004              Transaction rollback on error        Critical

  ITC-DB-005              Database connection pooling          High

  ITC-DB-006              Query performance optimization       High
  ------------------------------------------------------------------------------------

# 5. System Test Plan

## 5.1 Authentication Feature

**STC-AUTH-01: User Registration**

**Description:** Verify a guest can successfully register to the system

**Prerequisite:** Browser is not logged in, on registration page

**Test Script:**

1.  Navigate to registration page

2.  Enter valid username (e.g., \'testuser123\')

3.  Enter valid email (e.g., \'test@example.com\')

4.  Enter valid password meeting complexity requirements

5.  Click \'Register\' button

6.  Verify success message is displayed

7.  Verify confirmation email sent

8.  Verify redirect to login page

**Expected Result:** User account created with default \"user\" role, confirmation email sent, redirected to login

**Priority:** Critical

**STC-AUTH-02: User Login**

**Description:** Verify user can login with valid credentials

**Prerequisite:** User account exists, browser not logged in

**Test Script:**

9.  Navigate to login page

10. Enter valid username

11. Enter valid password

12. Click \'Login\' button

13. Verify JWT token generated

14. Verify redirect to dashboard

15. Verify user session created

**Expected Result:** User authenticated, JWT token stored, redirected to dashboard

**Priority:** Critical

**STC-AUTH-03: User Logout**

**Description:** Verify user can logout and session is invalidated

**Prerequisite:** User is logged in

**Test Script:**

16. Click \'Logout\' button

17. Verify session invalidated

18. Verify JWT token cleared

19. Verify redirect to login page

20. Attempt to access protected route

21. Verify redirect to login page

**Expected Result:** Session invalidated, token cleared, cannot access protected routes

**Priority:** Critical

**STC-AUTH-04: Token Expiration**

**Description:** Verify expired tokens require re-authentication

**Prerequisite:** User logged in with token near expiration

**Test Script:**

22. Wait for token to expire (or mock time)

23. Attempt to access protected route

24. Verify 401 Unauthorized response

25. Verify redirect to login page

26. Login again

27. Verify new token generated

28. Verify access to protected route

**Expected Result:** Expired token rejected, user must re-authenticate

**Priority:** Critical

## 5.2 Authorization Feature

**STC-AUTHZ-01: Admin Full Access**

**Description:** Verify Admin users have full system access

**Prerequisite:** User logged in with Admin role

**Test Script:**

29. Navigate to user management page

30. Verify can create users

31. Verify can update user roles

32. Verify can delete users

33. Navigate to all projects

34. Verify can access any project

35. Navigate to system configuration

36. Verify can modify settings

**Expected Result:** Admin has full CRUD access to all resources

**Priority:** Critical

**STC-AUTHZ-02: Programmer Project Isolation**

**Description:** Verify Programmers can only access own or granted projects

**Prerequisite:** Two Programmer users with separate projects

**Test Script:**

37. Login as Programmer A

38. Create Project X

39. Verify Project X appears in project list

40. Logout and login as Programmer B

41. Attempt to access Project X

42. Verify 403 Forbidden response

43. Login as Admin

44. Grant Programmer B access to Project X

45. Login as Programmer B

46. Verify can now access Project X

**Expected Result:** Project isolation enforced, access grants work correctly

**Priority:** Critical

**STC-AUTHZ-03: Visitor Read-Only Access**

**Description:** Verify Visitors have read-only access to assigned projects

**Prerequisite:** Visitor user with assigned project

**Test Script:**

47. Login as Visitor

48. Navigate to assigned project

49. Verify can view project details

50. Attempt to update project

51. Verify 403 Forbidden response

52. Attempt to delete project

53. Verify 403 Forbidden response

54. Attempt to create new project

55. Verify 403 Forbidden response

**Expected Result:** Visitor can only view, cannot modify any resources

**Priority:** Critical

## 5.3 Code Review Feature

**STC-REVIEW-01: Automated PR Review**

**Description:** Verify system performs automated code review on pull request

**Prerequisite:** Repository connected with active webhook

**Test Script:**

56. Create pull request on GitHub with code changes

57. Wait for webhook trigger (max 10 seconds)

58. Verify analysis task appears in queue

59. Wait for analysis completion (8-50 seconds)

60. Verify review comments posted on GitHub PR

61. Verify issues categorized by severity

62. Verify dependency graph updated in Neo4j

63. Verify audit log entry created

**Expected Result:** AI review feedback posted, issues identified, graph updated, action logged

**Priority:** Critical

**STC-REVIEW-02: Issue Severity Classification**

**Description:** Verify issues are correctly classified by severity

**Prerequisite:** PR with various code issues

**Test Script:**

64. Submit PR with security vulnerability

65. Verify classified as Critical

66. Submit PR with logic error

67. Verify classified as High

68. Submit PR with code smell

69. Verify classified as Medium

70. Submit PR with style violation

71. Verify classified as Low

**Expected Result:** Issues correctly classified by severity level

**Priority:** High

## 5.4 Architecture Analysis Feature

**STC-ARCH-01: Dependency Graph Visualization**

**Description:** Verify user can view interactive architecture graph

**Prerequisite:** Repository analyzed at least once

**Test Script:**

72. Navigate to Architecture tab

73. Select project from dropdown

74. Verify dependency graph renders

75. Click on a node to view details

76. Apply filter (e.g., view by service)

77. Verify circular dependencies highlighted in red

78. Zoom in/out on graph

79. Pan across graph

80. Export graph as PNG

**Expected Result:** Graph displays correctly, filters work, interactions smooth, export succeeds

**Priority:** High

**STC-ARCH-02: Circular Dependency Detection**

**Description:** Verify system detects circular dependencies

**Prerequisite:** Repository with circular dependencies

**Test Script:**

81. Analyze repository with Module A → B → C → A cycle

82. Navigate to Architecture tab

83. Verify circular dependency highlighted

84. Click on cycle for details

85. Verify all modules in cycle listed

86. Verify severity rating shown

87. Verify remediation suggestions provided

**Expected Result:** Circular dependencies detected and highlighted with remediation guidance

**Priority:** High

## 5.5 Audit Logging Feature

**STC-AUDIT-01: Comprehensive Action Logging**

**Description:** Verify all sensitive actions are logged

**Prerequisite:** Admin user logged in

**Test Script:**

88. Perform login

89. Verify login logged with timestamp, IP, user agent

90. Create new user

91. Verify user creation logged

92. Update user role

93. Verify role change logged

94. Delete user

95. Verify deletion logged

96. Access project

97. Verify access logged

98. Modify configuration

99. Verify config change logged

100. Logout

101. Verify logout logged

**Expected Result:** All sensitive actions logged with complete information

**Priority:** Critical

**STC-AUDIT-02: Audit Log Query and Filter**

**Description:** Verify Admin can query and filter audit logs

**Prerequisite:** Admin user with historical audit data

**Test Script:**

102. Navigate to Audit Logs page

103. Query all logs

104. Verify logs displayed in reverse chronological order

105. Filter by specific user

106. Verify only that user\'s logs shown

107. Filter by action type (e.g., LOGIN)

108. Verify only login actions shown

109. Filter by date range

110. Verify only logs in range shown

111. Apply pagination

112. Verify correct page size and navigation

**Expected Result:** Audit logs queryable and filterable with accurate results

**Priority:** High

**STC-AUDIT-03: Audit Log Immutability**

**Description:** Verify audit logs cannot be modified or deleted

**Prerequisite:** Admin user with existing audit logs

**Test Script:**

113. Navigate to Audit Logs page

114. Attempt to edit log entry via UI

115. Verify no edit option available

116. Attempt to delete log entry via UI

117. Verify no delete option available

118. Attempt to modify log via API

119. Verify 403 Forbidden response

120. Attempt to delete log via API

121. Verify 403 Forbidden response

**Expected Result:** Audit logs are immutable, cannot be modified or deleted

**Priority:** Critical

## 5.6 User Management Feature

**STC-USER-01: Admin Create User**

**Description:** Verify Admin can create new users

**Prerequisite:** Admin user logged in

**Test Script:**

122. Navigate to User Management page

123. Click \'Create User\' button

124. Enter username, email, password

125. Select role (Programmer)

126. Click \'Create\' button

127. Verify success message

128. Verify user appears in user list

129. Verify audit log entry created

130. Logout and login as new user

131. Verify can authenticate

**Expected Result:** User created successfully, can authenticate, action logged

**Priority:** Critical

**STC-USER-02: Admin Update User Role**

**Description:** Verify Admin can update user roles with immediate effect

**Prerequisite:** Admin and Programmer users exist

**Test Script:**

132. Login as Programmer

133. Verify cannot access admin routes

134. Logout

135. Login as Admin

136. Navigate to User Management

137. Update Programmer role to Admin

138. Verify success message

139. Verify audit log entry created

140. Logout and login as updated user

141. Verify can now access admin routes

**Expected Result:** Role updated, permissions apply immediately, action logged

**Priority:** Critical

**STC-USER-03: Prevent Last Admin Deletion**

**Description:** Verify system prevents deletion of last Admin user

**Prerequisite:** Only one Admin user exists

**Test Script:**

142. Login as Admin

143. Navigate to User Management

144. Attempt to delete own account

145. Verify error message displayed

146. Verify deletion blocked

147. Create second Admin user

148. Attempt to delete first Admin

149. Verify deletion succeeds

**Expected Result:** Cannot delete last Admin, can delete when multiple Admins exist

**Priority:** Critical

## 5.7 Performance Testing

**STC-PERF-01: API Response Time**

**Description:** Verify API endpoints respond within acceptable time limits

**Test Script:**

150. Send 100 GET requests to /api/v1/projects

151. Measure response times

152. Verify P95 \< 500ms

153. Send 100 POST requests to /api/v1/auth/login

154. Measure response times

155. Verify P95 \< 1000ms

**Expected Result:** API response times meet NFR targets

**Priority:** High

**STC-PERF-02: Analysis Processing Time**

**Description:** Verify code analysis completes within time limits

**Test Script:**

156. Submit PR with \< 10K LOC

157. Measure time from webhook to comment posting

158. Verify completes in 8-12 seconds (P50)

159. Submit PR with 10K-50K LOC

160. Measure processing time

161. Verify completes in \< 2 minutes

**Expected Result:** Analysis processing times meet NFR targets

**Priority:** High

**STC-PERF-03: Concurrent User Load**

**Description:** Verify system handles concurrent users

**Test Script:**

162. Simulate 100 concurrent users

163. Each user performs: login, view dashboard, view project

164. Measure response times

165. Verify no errors

166. Verify response times remain acceptable

167. Increase to 500 concurrent users

168. Verify system remains stable

**Expected Result:** System handles 100+ concurrent users without degradation

**Priority:** High

## 5.8 Security Testing

**STC-SEC-01: SQL Injection Prevention**

**Description:** Verify system prevents SQL injection attacks

**Test Script:**

169. Attempt login with username: admin\' OR \'1\'=\'1

170. Verify login rejected

171. Attempt to create user with malicious input

172. Verify input sanitized

173. Attempt to query projects with SQL injection

174. Verify query fails safely

**Expected Result:** All SQL injection attempts blocked

**Priority:** Critical

**STC-SEC-02: XSS Prevention**

**Description:** Verify system prevents cross-site scripting attacks

**Test Script:**

175. Create project with name: \<script\>alert(\'XSS\')\</script\>

176. View project list

177. Verify script not executed

178. Verify HTML escaped

179. Submit PR comment with XSS payload

180. Verify payload sanitized

**Expected Result:** All XSS attempts blocked, HTML properly escaped

**Priority:** Critical

**STC-SEC-03: JWT Token Tampering**

**Description:** Verify tampered JWT tokens are rejected

**Test Script:**

181. Login and capture JWT token

182. Modify token payload (change role to Admin)

183. Attempt to access admin route with modified token

184. Verify 401 Unauthorized response

185. Modify token signature

186. Attempt to access any protected route

187. Verify 401 Unauthorized response

**Expected Result:** All tampered tokens rejected

**Priority:** Critical

**STC-SEC-04: Password Security**

**Description:** Verify password security requirements

**Test Script:**

188. Attempt to create user with weak password (\< 8 chars)

189. Verify rejected with error message

190. Attempt password without uppercase

191. Verify rejected

192. Attempt password without number

193. Verify rejected

194. Create user with strong password

195. Verify password hashed in database

196. Verify plaintext password not stored

**Expected Result:** Password requirements enforced, passwords securely hashed

**Priority:** Critical

**STC-SEC-05: Account Lockout**

**Description:** Verify account lockout after repeated failed login attempts

**Prerequisite:** Valid user account exists

**Test Script:**

197. Attempt login with wrong password (attempt 1)

198. Verify login rejected, no lockout yet

199. Repeat wrong password attempts 2-4

200. Verify each rejected, no lockout yet

201. Attempt wrong password (attempt 5)

202. Verify account locked

203. Attempt login with correct password

204. Verify still rejected due to lockout

205. Wait for lockout period to expire

206. Attempt login with correct password

207. Verify login succeeds

**Expected Result:** Account locked after 5 failed attempts, unlocks after lockout period

**Priority:** Critical

**STC-SEC-06: Rate Limiting**

**Description:** Verify API rate limiting prevents abuse

**Prerequisite:** Valid user account, API access

**Test Script:**

208. Send 100 requests to /api/auth/login within 1 minute

209. Verify first 100 requests processed

210. Send request 101

211. Verify 429 Too Many Requests response

212. Wait for rate limit window to reset

213. Send request again

214. Verify request processed normally

**Expected Result:** Rate limiting enforced at 100 requests/minute per user

**Priority:** High

## 5.9 Frontend Property-Based Tests

**Test Module:** frontend/src/components/auth/\_\_tests\_\_/

  ---------------------------------------------------------------------------------------------------------------------------------------
  **PBT ID**    **Property**                                                              **Framework**   **Iterations**   **Priority**
  ------------- ------------------------------------------------------------------------- --------------- ---------------- --------------
  PBT-FE-001    RBACGuard renders children when user has required role                    fast-check      100              Critical

  PBT-FE-002    RBACGuard redirects when user lacks required role                         fast-check      100              Critical

  PBT-FE-003    PermissionCheck shows content only when permission granted                fast-check      100              Critical

  PBT-FE-004    PermissionCheck hides content when permission denied                      fast-check      100              Critical

  PBT-FE-005    usePermission hook returns correct boolean for any role/permission pair   fast-check      100              High
  ---------------------------------------------------------------------------------------------------------------------------------------

# 6. Test Data Management

## 6.1 Test Data Requirements

**User Test Data:**

-   Admin users: 2 accounts

-   Programmer users: 5 accounts

-   Visitor users: 3 accounts

-   Inactive users: 2 accounts

**Project Test Data:**

-   Small projects (\< 10K LOC): 5 projects

-   Medium projects (10K-50K LOC): 3 projects

-   Large projects (\> 50K LOC): 2 projects

-   Projects with circular dependencies: 2 projects

-   Projects with layer violations: 2 projects

**Code Sample Data:**

-   Python files: 20 samples

-   JavaScript files: 20 samples

-   TypeScript files: 20 samples

-   Java files: 10 samples

-   Go files: 10 samples

## 6.2 Test Data Generation

**Automated Generation:**

-   Use Faker library for user data

-   Use Hypothesis/fast-check for property test data

-   Use factory pattern for model instances

-   Seed data scripts for consistent test environments

**Data Cleanup:**

-   Automated cleanup after each test run

-   Separate test database from development

-   Transaction rollback for unit tests

-   Database reset for integration tests

# 7. Defect Management

## 7.1 Defect Severity Levels

  ------------------------------------------------------------------------------------------------------------------------------------------
  **Severity**      **Definition**                                              **Example**                              **Response Time**
  ----------------- ----------------------------------------------------------- ---------------------------------------- -------------------
  **Critical**      System crash, data loss, security vulnerability             Authentication bypass, data corruption   4 hours

  **High**          Major feature broken, significant performance degradation   PR review fails, graph not rendering     24 hours

  **Medium**        Minor feature issue, workaround available                   UI glitch, slow query                    3 days

  **Low**           Cosmetic issue, minor inconvenience                         Typo, alignment issue                    1 week
  ------------------------------------------------------------------------------------------------------------------------------------------

## 7.2 Defect Tracking

**Tool:** GitHub Issues with labels

**Required Information:**

-   Title: Brief description

-   Severity: Critical/High/Medium/Low

-   Steps to reproduce

-   Expected vs actual behavior

-   Environment details

-   Screenshots/logs

-   Test case ID

## 7.3 Defect Resolution Process

215. **Report**: QA creates GitHub issue with all details

216. **Triage**: Test Lead assigns severity and priority

217. **Assign**: Issue assigned to developer

218. **Fix**: Developer implements fix and creates PR

219. **Verify**: QA verifies fix in test environment

220. **Close**: Issue closed when verified

# 8. Test Metrics and Reporting

## 8.1 Key Metrics

**Test Coverage:**

-   Code coverage: Target 80%+

-   Requirement coverage: Target 100%

-   Property coverage: 36/36 properties passing

**Test Execution:**

-   Total test cases executed

-   Pass/Fail/Blocked count

-   Pass rate: Target 95%+

-   Defect detection rate

**Performance:**

-   Average test execution time

-   CI/CD pipeline duration

-   Flaky test rate: Target \< 2%

## 8.2 Test Reports

**Daily Reports:**

-   Test execution summary

-   New defects found

-   Defects resolved

-   Blockers and risks

**Weekly Reports:**

-   Test progress vs plan

-   Coverage metrics

-   Defect trends

-   Risk assessment

**Final Report:**

-   Complete test summary

-   All test results

-   Defect summary

-   Quality assessment

-   Go/No-go recommendation

# 9. Entry and Exit Criteria

## 9.1 Entry Criteria

**Unit Testing:**

-   Code complete for module

-   Code review passed

-   Development environment set up

**Integration Testing:**

-   All unit tests passing

-   Integration environment ready

-   External services available (or mocked)

**System Testing:**

-   All integration tests passing

-   Staging environment deployed

-   Test data prepared

**UAT:**

-   All system tests passing

-   Production-like environment ready

-   User documentation complete

## 9.2 Exit Criteria

**Unit Testing:**

-   80%+ code coverage achieved

-   All critical/high priority tests passing

-   No critical defects open

**Integration Testing:**

-   All integration tests passing

-   External service integrations verified

-   No high severity defects open

**System Testing:**

-   All system test cases executed

-   95%+ pass rate achieved

-   All critical defects resolved

-   Performance targets met

**UAT:**

-   User acceptance obtained

-   All critical/high defects resolved

-   Production deployment approved

# 10. Risks and Mitigation

## 10.1 Test Risks

  ------------------------------------------------------------------------------------------------------------------
  **Risk**                       **Impact**        **Probability**   **Mitigation**
  ------------------------------ ----------------- ----------------- -----------------------------------------------
  External API unavailability    High              Medium            Use mocking, maintain test stubs

  Test environment instability   High              Low               Automated environment provisioning

  Insufficient test data         Medium            Low               Automated data generation

  Flaky tests                    Medium            Medium            Implement retry logic, improve test isolation

  Resource constraints           Medium            Low               Prioritize critical tests, parallel execution
  ------------------------------------------------------------------------------------------------------------------

## 10.2 Mitigation Strategies

**Technical Risks:**

-   Maintain comprehensive mocking layer

-   Implement circuit breakers for external services

-   Use containerization for consistent environments

-   Automated test data generation

**Schedule Risks:**

-   Prioritize critical path testing

-   Parallel test execution

-   Automated regression testing

-   Early defect detection

**Resource Risks:**

-   Cross-training team members

-   Automated test execution

-   Cloud-based test environments

-   Outsource non-critical testing

# 11. Approval

  ---------------------------------------------------------------------------------------------------
  **Role**               **Name**                     **Signature**                **Date**
  ---------------------- ---------------------------- ---------------------------- ------------------
  **Test Lead**          \_\_\_\_\_\_\_\_\_\_\_\_\_   \_\_\_\_\_\_\_\_\_\_\_\_\_   \_\_\_\_\_\_\_\_

  **Development Lead**   \_\_\_\_\_\_\_\_\_\_\_\_\_   \_\_\_\_\_\_\_\_\_\_\_\_\_   \_\_\_\_\_\_\_\_

  **Project Manager**    \_\_\_\_\_\_\_\_\_\_\_\_\_   \_\_\_\_\_\_\_\_\_\_\_\_\_   \_\_\_\_\_\_\_\_

  **QA Manager**         \_\_\_\_\_\_\_\_\_\_\_\_\_   \_\_\_\_\_\_\_\_\_\_\_\_\_   \_\_\_\_\_\_\_\_
  ---------------------------------------------------------------------------------------------------

**\[Feature Name\]**

-   **STC ID:** \[e.g., STC-01\].

-   **Description:** \[e.g., Testing if a Guest can register\].

-   **Prerequisite:** \[e.g., Browser not logged in\].

-   **Test Script (Steps):**


# 12. Test Organization and Roles (RACI Matrix)

## 12.1 Test Team Structure

| **Role** | **Name** | **Allocation** | **Responsibilities** |
|----------|----------|----------------|----------------------|
| **Test Lead** | BaiXuan Zhang | 20% | Overall test strategy, coordination, reporting, quality gates |
| **Backend Test Engineer** | BaiXuan Zhang | 30% | Unit tests for API services, AST parser, graph analysis, RBAC system |
| **Frontend Test Engineer** | BaiXuan Zhang | 15% | UI component tests, integration tests for frontend, route guard tests |
| **QA Engineer** | BaiXuan Zhang | 20% | System testing, test record documentation, test data management |
| **Security Test Engineer** | BaiXuan Zhang | 10% | Security testing, penetration testing, vulnerability assessment |
| **Performance Test Engineer** | BaiXuan Zhang | 10% | Performance testing, load testing, stress testing |
| **Test Reviewer** | Dr. Siraprapa | 5% | Test plan review, test results validation, quality assurance oversight |

**Note:** Single-person project with BaiXuan Zhang fulfilling multiple testing roles.

## 12.2 Testing RACI Matrix

| **Activity** | **Test Lead** | **Backend Tester** | **Frontend Tester** | **QA Engineer** | **Security Tester** | **Performance Tester** | **Test Reviewer** |
|--------------|---------------|-------------------|---------------------|-----------------|---------------------|------------------------|-------------------|
| Test Planning | R/A | C | C | C | C | C | I |
| Test Case Design | A | R | R | R | R | R | C |
| Unit Test Execution | A | R | R | I | I | I | I |
| Integration Test Execution | A | R | R | R | I | I | I |
| System Test Execution | A | C | C | R | I | I | C |
| Security Test Execution | A | I | I | C | R | I | C |
| Performance Test Execution | A | I | I | C | I | R | C |
| Defect Reporting | A | R | R | R | R | R | I |
| Test Reporting | R/A | C | C | C | C | C | I |
| Test Sign-off | C | I | I | I | I | I | R/A |

**Legend:** R = Responsible, A = Accountable, C = Consulted, I = Informed

## 12.3 Test Team Training Requirements

| **Skill Area** | **Current Level** | **Target Level** | **Training Method** | **Duration | **Timeline** |
|--------------|---------------|--------------|---------------------|----------|-----------|
| Property-Based Testing | Intermediate | Advanced | Online courses, Hypothesis/fast-check documentation | 2 weeks |
| Security Testing | Basic | Intermediate | OWASP training, security testing workshops | 3 weeks |
| Performance Testing | Basic | Intermediate | Load testing tutorials, Locust documentation | 2 weeks |
| Test Automation | Intermediate | Advanced | CI/CD best practices, GitHub Actions training | 2 weeks |
| Neo4j Graph Testing | Basic | Intermediate | Neo4j testing documentation, Cypher query optimization | 1 week |

# 13. Test Environment Topology and Configuration

## 13.1 Environment Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      Test Environment Topology                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐  │
│  │   Browser    │─────▶│  Load        │─────▶│   API        │  │
│  │   Clients    │      │  Balancer    │      │   Gateway    │  │
│  └──────────────┘      └──────────────┘      └──────────────┘  │
│                                                      │            │
│                        ┌─────────────────────────────┼───────┐  │
│                        │                             │       │  │
│              ┌─────────▼────────┐         ┌─────────▼──────┐│  │
│              │  Auth Service    │         │  Code Review   ││  │
│              │  (Port 3001)     │         │  Service       ││  │
│              └─────────┬────────┘         │  (Port 3002)   ││  │
│                        │                  └────────┬───────┘│  │
│              ┌─────────▼────────┐                 │         │  │
│              │  PostgreSQL      │◀────────────────┘         │  │
│              │  (Port 5432)     │                           │  │
│              └──────────────────┘                           │  │
│                                                              │  │
│              ┌──────────────────┐         ┌────────────────┐│  │
│              │  Neo4j Graph DB  │         │  Redis Cache   ││  │
│              │  (Port 7687)     │         │  (Port 6379)   ││  │
│              └──────────────────┘         └────────────────┘│  │
│                                                              │  │
│              ┌──────────────────────────────────────────────┘  │
│              │  External Services (Mocked in Test)             │
│              │  - GitHub API (Port 8080)                       │
│              │  - LLM API Mock (Port 8081)                     │
│              └─────────────────────────────────────────────────┘
└─────────────────────────────────────────────────────────────────┘
```

## 13.2 Environment Configuration Details

### 13.2.1 Development Environment

**Purpose:** Local development and unit testing

**Infrastructure:**
- Local machine (macOS/Windows/Linux)
- Docker Desktop for containerization
- Local PostgreSQL 15 instance
- Local Neo4j 5.x instance
- Local Redis 7.x instance

**Configuration:**
```yaml
Environment: development
Database: postgresql://localhost:5432/ai_reviewer_dev
Neo4j: bolt://localhost:7687
Redis: redis://localhost:6379
GitHub API: Mocked with Wiremock
LLM API: Mocked with local stub
Log Level: DEBUG
```

**Access Control:**
- All developers have full access
- No authentication required for local services
- Test data reset script available

### 13.2.2 Integration Test Environment

**Purpose:** Integration testing with external services

**Infrastructure:**
- Docker Compose multi-container setup
- Shared PostgreSQL container
- Shared Neo4j container
- Shared Redis container
- Mock service containers

**Configuration:**
```yaml
Environment: integration
Database: postgresql://postgres-test:5432/ai_reviewer_integration
Neo4j: bolt://neo4j-test:7687
Redis: redis://redis-test:6379
GitHub API: http://github-mock:8080
LLM API: http://llm-mock:8081
Log Level: INFO
Network: ai-reviewer-test-network
```

**Isolation:**
- Separate database per test run
- Automated cleanup after tests
- Network isolation between test runs

### 13.2.3 Staging Environment

**Purpose:** System testing, UAT, pre-production validation

**Infrastructure:**
- AWS EC2 t3.medium instances (2 vCPU, 4GB RAM)
- AWS RDS PostgreSQL db.t3.medium (Multi-AZ disabled)
- Neo4j AuraDB Professional
- AWS ElastiCache Redis cache.t3.micro
- AWS Application Load Balancer

**Configuration:**
```yaml
Environment: staging
Database: postgresql://staging-db.region.rds.amazonaws.com:5432/ai_reviewer_staging
Neo4j: neo4j+s://staging.databases.neo4j.io
Redis: redis://staging-cache.region.cache.amazonaws.com:6379
GitHub API: https://api.github.com (real, test organization)
LLM API: https://api.openai.com (real, rate-limited test key)
Log Level: INFO
SSL: Enabled
Domain: staging.ai-reviewer.example.com
```

**Access Control:**
- VPN required for database access
- IAM roles for AWS resource access
- Test accounts with limited GitHub permissions
- Separate LLM API key with spending limits

### 13.2.4 Production Environment

**Purpose:** Live system (not used for testing except smoke tests)

**Infrastructure:**
- AWS EC2 t3.large instances (2 vCPU, 8GB RAM)
- Auto-scaling group (2-10 instances)
- AWS RDS PostgreSQL db.t3.large (Multi-AZ enabled)
- Neo4j AuraDB Enterprise
- AWS ElastiCache Redis cache.t3.small (Multi-AZ enabled)
- AWS Application Load Balancer with SSL
- CloudFront CDN

**Configuration:**
```yaml
Environment: production
Database: postgresql://prod-db.region.rds.amazonaws.com:5432/ai_reviewer_prod
Neo4j: neo4j+s://prod.databases.neo4j.io
Redis: redis://prod-cache.region.cache.amazonaws.com:6379
GitHub API: https://api.github.com (real, production app)
LLM API: https://api.openai.com (real, production key)
Log Level: WARNING
SSL: Enforced
Domain: app.ai-reviewer.example.com
Backup: Daily automated backups
Monitoring: CloudWatch, Datadog
```

## 13.3 Test Data Preparation and Reset Procedures

### 13.3.1 Test Data Seeding

**Automated Seed Scripts:**
```bash
# Development environment
npm run seed:dev

# Integration test environment
npm run seed:integration

# Staging environment
npm run seed:staging
```

**Seed Data Contents:**
- 10 test user accounts (2 Admin, 5 Programmer, 3 Visitor)
- 15 test projects with varying sizes
- 50 code analysis results
- 100 audit log entries
- Sample dependency graphs

### 13.3.2 Test Data Reset

**Between Test Runs:**
```bash
# Reset database to clean state
npm run db:reset

# Reload seed data
npm run seed:integration
```

**Automated in CI/CD:**
- Database reset before each test suite
- Seed data loaded automatically
- Cleanup after test completion

### 13.3.3 Test Data Isolation

**Strategy:**
- Each test suite uses unique test data prefixes
- Parallel tests use separate database schemas
- Transaction rollback for unit tests
- Full database reset for integration tests

## 13.4 Environment Maintenance

**Daily:**
- Automated health checks
- Log rotation
- Disk space monitoring

**Weekly:**
- Database vacuum and analyze
- Cache clearing
- Security updates

**Monthly:**
- Full environment rebuild
- Dependency updates
- Performance baseline testing

# 14. Complete Test Type Coverage

## 14.1 Regression Testing

### 14.1.1 Regression Test Strategy

**Scope:** All previously passing tests re-executed after code changes

**Trigger Conditions:**
- Every commit to main branch
- Every pull request
- Before each release
- After bug fixes

**Test Selection:**
- Full regression: All tests (9 weeks)
- Targeted regression: Impacted modules only (1-2 days)
- Smoke regression: Critical paths only (2 hours)

**Automation:**
- 100% automated via CI/CD pipeline
- Parallel execution across 4 runners
- Automatic failure notification

### 14.1.2 Regression Test Cases

| **Regression ID** | **Test Area** | **Frequency** | **Duration** | **Priority** |
|-------------------|---------------|---------------|--------------|--------------|
| REG-001 | Authentication flow | Every commit | 5 min | Critical |
| REG-002 | Authorization checks | Every commit | 10 min | Critical |
| REG-003 | Code review workflow | Every commit | 15 min | Critical |
| REG-004 | Architecture analysis | Daily | 30 min | High |
| REG-005 | API endpoints | Every commit | 20 min | Critical |
| REG-006 | Database operations | Every commit | 10 min | Critical |
| REG-007 | UI components | Every PR | 15 min | High |
| REG-008 | Integration points | Daily | 25 min | High |

## 14.2 User Acceptance Testing (UAT)

### 14.2.1 UAT Process

**Participants:**
- Dr. Siraprapa (Academic Supervisor)
- 2-3 peer students (Programmer role)
- 1 external reviewer (Visitor role)

**Duration:** 1 week (Week 1 of May 2026)

**Environment:** Staging environment with production-like data

### 14.2.2 UAT Test Scenarios

**UAT-001: End-to-End Code Review Workflow**
- User registers and logs in
- Connects GitHub repository
- Submits pull request
- Reviews AI-generated feedback
- Accepts/rejects suggestions
- Merges pull request
- **Acceptance Criteria:** Complete workflow in < 5 minutes, feedback quality rated 4/5+

**UAT-002: Architecture Visualization**
- User navigates to Architecture tab
- Views dependency graph
- Identifies circular dependencies
- Exports graph as image
- **Acceptance Criteria:** Graph renders in < 3 seconds, all dependencies visible

**UAT-003: User Management (Admin)**
- Admin creates new user
- Assigns role
- Grants project access
- Views audit logs
- **Acceptance Criteria:** All operations complete successfully, audit trail complete

**UAT-004: Security and Access Control**
- Visitor attempts to modify project (should fail)
- Programmer accesses only assigned projects
- Admin accesses all projects
- **Acceptance Criteria:** All access controls enforced correctly

**UAT-005: Performance and Usability**
- User performs typical daily tasks
- Measures response times
- Evaluates UI intuitiveness
- **Acceptance Criteria:** All pages load < 2 seconds, usability rated 4/5+

### 14.2.3 UAT Acceptance Criteria

**Functional Acceptance:**
- 100% of critical user stories completed successfully
- 95%+ of high-priority user stories completed
- No critical or high-severity defects open

**Non-Functional Acceptance:**
- Performance targets met (API < 500ms, analysis < 50s)
- Security requirements validated
- Usability rating ≥ 4.0/5.0

**Documentation Acceptance:**
- User manual complete and accurate
- Installation guide validated
- API documentation complete

## 14.3 Compatibility Testing

### 14.3.1 Browser Compatibility Matrix

| **Browser** | **Version** | **OS** | **Test Coverage** | **Priority** |
|-------------|-------------|--------|-------------------|--------------|
| Chrome | 120+ | Windows 10/11 | Full | Critical |
| Chrome | 120+ | macOS Sonoma | Full | Critical |
| Chrome | 120+ | Ubuntu 24.04 | Smoke | High |
| Firefox | 121+ | Windows 10/11 | Full | High |
| Firefox | 121+ | macOS Sonoma | Full | High |
| Safari | 17+ | macOS Sonoma | Full | High |
| Edge | 120+ | Windows 10/11 | Smoke | Medium |

**Test Cases:**
- COMPAT-001: Login and authentication
- COMPAT-002: Dashboard rendering
- COMPAT-003: Graph visualization
- COMPAT-004: Form submissions
- COMPAT-005: File uploads
- COMPAT-006: Responsive design (mobile/tablet)

### 14.3.2 Programming Language Compatibility

| **Language** | **Versions** | **Test Projects** | **Priority** |
|--------------|--------------|-------------------|--------------|
| Python | 3.9, 3.10, 3.11, 3.12 | 5 sample projects | Critical |
| JavaScript | ES6, ES2020, ES2023 | 5 sample projects | Critical |
| TypeScript | 4.9, 5.0, 5.3 | 5 sample projects | Critical |
| Java | 11, 17, 21 | 3 sample projects | High |
| Go | 1.20, 1.21, 1.22 | 3 sample projects | High |

**Test Cases:**
- COMPAT-007: AST parsing for each language version
- COMPAT-008: Dependency extraction accuracy
- COMPAT-009: Code complexity calculation
- COMPAT-010: Syntax error handling

### 14.3.3 Operating System Compatibility

| **OS** | **Version** | **Test Type** | **Priority** |
|--------|-------------|---------------|--------------|
| Windows | 10, 11 | Full system test | Critical |
| macOS | Sonoma 14.0+ | Full system test | Critical |
| Ubuntu | 22.04 LTS, 24.04 LTS | Full system test | High |
| Docker | 24.x | Container deployment | Critical |

## 14.4 Usability Testing

### 14.4.1 Usability Test Objectives

- Evaluate ease of use for first-time users
- Identify UI/UX pain points
- Validate navigation and information architecture
- Assess accessibility compliance

### 14.4.2 Usability Test Scenarios

**USABILITY-001: First-Time User Onboarding**
- **Task:** Register, connect repository, receive first review
- **Success Criteria:** Complete in < 10 minutes without help
- **Metrics:** Task completion rate, time on task, error rate

**USABILITY-002: Dashboard Navigation**
- **Task:** Find specific project, view metrics, access settings
- **Success Criteria:** Locate all items in < 2 minutes
- **Metrics:** Navigation efficiency, clicks to target

**USABILITY-003: Code Review Interpretation**
- **Task:** Understand AI feedback, accept/reject suggestions
- **Success Criteria:** Correctly interpret 90%+ of feedback
- **Metrics:** Comprehension rate, action accuracy

**USABILITY-004: Accessibility Compliance**
- **Task:** Navigate using keyboard only, screen reader
- **Success Criteria:** All functions accessible, WCAG 2.1 AA compliant
- **Metrics:** Keyboard navigation success, screen reader compatibility

### 14.4.3 Usability Metrics

| **Metric** | **Target** | **Measurement Method** |
|------------|------------|------------------------|
| Task Success Rate | ≥ 90% | Observation, task completion |
| Time on Task | ≤ Target time | Timer, analytics |
| Error Rate | ≤ 5% | Error logging, observation |
| User Satisfaction | ≥ 4.0/5.0 | Post-test survey (SUS) |
| Learnability | ≥ 80% improvement | First vs. second attempt |

## 14.5 Disaster Recovery Testing

### 14.5.1 DR Test Scenarios

**DR-001: Database Failure Recovery**
- **Scenario:** PostgreSQL database crashes
- **Test Steps:**
  1. Simulate database crash
  2. Verify automatic failover to standby (Multi-AZ)
  3. Verify data integrity
  4. Measure recovery time
- **Success Criteria:** RTO < 5 minutes, RPO < 1 minute, no data loss

**DR-002: Application Server Failure**
- **Scenario:** Primary application server crashes
- **Test Steps:**
  1. Terminate EC2 instance
  2. Verify load balancer redirects traffic
  3. Verify auto-scaling launches new instance
  4. Measure service restoration time
- **Success Criteria:** RTO < 3 minutes, no user-visible downtime

**DR-003: Data Backup and Restore**
- **Scenario:** Catastrophic data loss requiring restore from backup
- **Test Steps:**
  1. Take full database backup
  2. Simulate data corruption
  3. Restore from backup
  4. Verify data integrity
  5. Measure restore time
- **Success Criteria:** Successful restore, RTO < 30 minutes, RPO < 24 hours

**DR-004: External Service Outage**
- **Scenario:** GitHub API or LLM API unavailable
- **Test Steps:**
  1. Simulate API outage
  2. Verify graceful degradation
  3. Verify queue-based retry mechanism
  4. Verify user notification
- **Success Criteria:** No system crash, requests queued, users notified

**DR-005: Complete Region Failure**
- **Scenario:** AWS region outage
- **Test Steps:**
  1. Simulate region failure
  2. Verify DNS failover to backup region
  3. Verify data replication
  4. Measure total recovery time
- **Success Criteria:** RTO < 1 hour, RPO < 5 minutes

### 14.5.2 DR Testing Schedule

| **Test** | **Frequency** | **Environment** | **Duration** |
|----------|---------------|-----------------|--------------|
| Database Failover | Quarterly | Staging | 1 hour |
| Server Failure | Monthly | Staging | 30 min |
| Backup Restore | Monthly | Staging | 2 hours |
| External Service Outage | Quarterly | Staging | 1 hour |
| Region Failure | Annually | Production (planned) | 4 hours |

# 15. Test Work Breakdown Structure (WBS)

## 15.1 Test WBS Hierarchy

```
1.0 Test Planning (Week 1 of Mar 2026)
  1.1 Test strategy definition (2 days)
  1.2 Test case design (3 days)
  1.3 Test environment setup (2 days)
  1.4 Test data preparation (1 day)
  1.5 Test plan review and approval (1 day)

2.0 Unit Testing (Week 1-2 of Mar 2026)
  2.1 Authentication service tests (2 days)
  2.2 RBAC service tests (2 days)
  2.3 Audit service tests (1 day)
  2.4 Authorization middleware tests (1 day)
  2.5 AST parser tests (2 days)
  2.6 Graph analysis tests (2 days)

3.0 Property-Based Testing (Week 3 of Mar 2026)
  3.1 Authentication properties (1 day)
  3.2 RBAC properties (2 days)
  3.3 Authorization middleware properties (1 day)
  3.4 Audit logging properties (1 day)
  3.5 Frontend route protection properties (1 day)
  3.6 Session management properties (1 day)

4.0 Integration Testing (Week 4 of Mar 2026)
  4.1 GitHub API integration (2 days)
  4.2 LLM API integration (2 days)
  4.3 Database integration (2 days)
  4.4 Internal service integration (1 day)

5.0 System Testing (Week 1-2 of Apr 2026)
  5.1 Authentication feature testing (2 days)
  5.2 Authorization feature testing (2 days)
  5.3 Code review feature testing (3 days)
  5.4 Architecture analysis testing (2 days)
  5.5 Audit logging testing (1 day)
  5.6 User management testing (2 days)

6.0 Security Testing (Week 3 of Apr 2026)
  6.1 OWASP Top 10 testing (3 days)
  6.2 Authentication security (1 day)
  6.3 Authorization security (1 day)
  6.4 Input validation testing (1 day)
  6.5 Security scan and remediation (1 day)

7.0 Performance Testing (Week 4 of Apr 2026)
  7.1 Load testing (2 days)
  7.2 Stress testing (1 day)
  7.3 Endurance testing (2 days)
  7.4 Performance optimization (2 days)

8.0 User Acceptance Testing (Week 1 of May 2026)
  8.1 UAT preparation (1 day)
  8.2 UAT execution (3 days)
  8.3 Feedback collection and analysis (1 day)
  8.4 UAT sign-off (1 day)

9.0 Test Reporting and Closure (Week 2 of May 2026)
  9.1 Final test report (2 days)
  9.2 Defect summary and analysis (1 day)
  9.3 Lessons learned (1 day)
  9.4 Test artifact archival (1 day)
```

## 15.2 Test Schedule with Dependencies

| **WBS ID** | **Task** | **Duration** | **Start Date** | **End Date** | **Dependencies** | **Resources** |
|------------|----------|--------------|----------------|--------------|------------------|---------------|
| 1.0 | Test Planning | 9 days | Mar 1, 2026 | Mar 11, 2026 | - | Test Lead |
| 2.0 | Unit Testing | 10 days | Mar 12, 2026 | Mar 25, 2026 | 1.0 | Backend/Frontend Testers |
| 3.0 | Property-Based Testing | 5 days | Mar 26, 2026 | Apr 1, 2026 | 2.0 | Backend/Frontend Testers |
| 4.0 | Integration Testing | 5 days | Apr 2, 2026 | Apr 8, 2026 | 3.0 | All Testers |
| 5.0 | System Testing | 10 days | Apr 9, 2026 | Apr 22, 2026 | 4.0 | QA Engineer |
| 6.0 | Security Testing | 5 days | Apr 23, 2026 | Apr 29, 2026 | 5.0 | Security Tester |
| 7.0 | Performance Testing | 5 days | Apr 30, 2026 | May 6, 2026 | 5.0 | Performance Tester |
| 8.0 | UAT | 5 days | May 7, 2026 | May 13, 2026 | 6.0, 7.0 | All + Stakeholders |
| 9.0 | Test Closure | 5 days | May 14, 2026 | May 20, 2026 | 8.0 | Test Lead |

## 15.3 Critical Path Analysis

**Critical Path:** 1.0 → 2.0 → 3.0 → 4.0 → 5.0 → 6.0 → 8.0 → 9.0

**Total Duration:** 54 days (approximately 11 weeks)

**Critical Activities:**
- Test planning completion (blocks all testing)
- Unit testing completion (blocks integration testing)
- System testing completion (blocks UAT)
- UAT sign-off (blocks production release)

**Float/Slack:**
- Performance testing: 5 days (can run parallel to security testing)
- Test data preparation: 2 days
- Documentation updates: 3 days

# 16. Test Suspension and Resumption Criteria

## 16.1 Test Suspension Criteria

Testing activities will be suspended if any of the following conditions occur:

**SUSPEND-001: Critical Environment Failure**
- **Condition:** Test environment unavailable for > 4 hours
- **Action:** Suspend all testing, notify stakeholders
- **Responsible:** Test Lead, DevOps Engineer

**SUSPEND-002: Blocking Defects**
- **Condition:** ≥ 3 critical defects OR ≥ 10 high-severity defects open
- **Action:** Suspend system testing, focus on defect resolution
- **Responsible:** Test Lead, Development Lead

**SUSPEND-003: Build Instability**
- **Condition:** Build failure rate > 30% over 24 hours
- **Action:** Suspend integration/system testing
- **Responsible:** Test Lead, DevOps Engineer

**SUSPEND-004: Test Data Corruption**
- **Condition:** Test data integrity compromised
- **Action:** Suspend all testing, restore test data
- **Responsible:** QA Engineer, Database Admin

**SUSPEND-005: Resource Unavailability**
- **Condition:** Key personnel unavailable (Test Lead, critical tester)
- **Action:** Suspend critical path activities
- **Responsible:** Project Manager

**SUSPEND-006: External Service Outage**
- **Condition:** GitHub API or LLM API unavailable for > 2 hours
- **Action:** Suspend integration/system tests requiring external services
- **Responsible:** Test Lead

## 16.2 Test Resumption Criteria

Testing activities will resume only when the following conditions are met:

**RESUME-001: Environment Restoration**
- **Condition:** Test environment fully operational
- **Verification:** Health check passes, all services responding
- **Approval:** Test Lead, DevOps Engineer
- **Action:** Resume from last checkpoint

**RESUME-002: Defect Resolution**
- **Condition:** Critical defects < 3 AND high-severity defects < 10
- **Verification:** All blocking defects verified fixed
- **Approval:** Test Lead, Development Lead
- **Action:** Re-run failed tests, continue testing

**RESUME-003: Build Stability**
- **Condition:** Build success rate > 90% over 24 hours
- **Verification:** CI/CD pipeline stable
- **Approval:** DevOps Engineer
- **Action:** Resume integration/system testing

**RESUME-004: Test Data Restoration**
- **Condition:** Test data restored and verified
- **Verification:** Data integrity checks pass
- **Approval:** QA Engineer
- **Action:** Resume from last checkpoint

**RESUME-005: Resource Availability**
- **Condition:** Key personnel available or backup assigned
- **Verification:** Resource allocation confirmed
- **Approval:** Project Manager
- **Action:** Resume critical path activities

**RESUME-006: External Service Recovery**
- **Condition:** External services operational for > 1 hour
- **Verification:** Service health checks pass
- **Approval:** Test Lead
- **Action:** Resume integration/system testing

## 16.3 Suspension/Resumption Process

**Suspension Process:**
1. Identify suspension condition
2. Document current test state and progress
3. Notify all stakeholders via email and Slack
4. Create suspension report with root cause
5. Assign responsibility for resolution
6. Set expected resumption date

**Resumption Process:**
1. Verify resumption criteria met
2. Obtain approval from responsible parties
3. Notify all stakeholders of resumption
4. Review test state and determine restart point
5. Execute smoke tests to verify environment
6. Resume testing activities

# 17. Quantified Test Completion and Exit Criteria

## 17.1 Unit Testing Completion Criteria

**Code Coverage:**
- Overall code coverage: ≥ 80%
- Critical components coverage: ≥ 90%
- Branch coverage: ≥ 75%

**Test Execution:**
- All unit tests executed: 100%
- Unit test pass rate: ≥ 95%
- No critical defects open
- High-severity defects: ≤ 2

**Quality Metrics:**
- Test execution time: ≤ 10 minutes
- Flaky test rate: ≤ 2%
- Code review: 100% of test code reviewed

## 17.2 Integration Testing Completion Criteria

**Test Execution:**
- All integration tests executed: 100%
- Integration test pass rate: ≥ 90%
- No critical defects open
- High-severity defects: ≤ 3

**Integration Coverage:**
- All external service integrations tested: 100%
- All internal service integrations tested: 100%
- Error handling scenarios tested: ≥ 80%

**Quality Metrics:**
- Integration test execution time: ≤ 30 minutes
- External service mock coverage: 100%

## 17.3 System Testing Completion Criteria

**Test Execution:**
- All system test cases executed: 100%
- System test pass rate: ≥ 95%
- No critical defects open
- High-severity defects: ≤ 1
- Medium-severity defects: ≤ 5

**Functional Coverage:**
- All URS requirements tested: 100%
- All SRS requirements tested: 100%
- All user workflows tested: 100%

**Non-Functional Requirements:**
- Performance targets met: 100%
  - API response time P95 < 500ms: ✓
  - Analysis processing time < 50s: ✓
  - Concurrent users ≥ 100: ✓
- Security requirements met: 100%
  - OWASP Top 10 compliance: ✓
  - Authentication/authorization: ✓
- Usability rating: ≥ 4.0/5.0

## 17.4 Property-Based Testing Completion Criteria

**Property Coverage:**
- All 36 RBAC properties tested: 100%
- All properties passing: 100%
- Minimum iterations per property: 100

**Property Categories:**
- Authentication properties (5): 100% passing
- RBAC properties (6): 100% passing
- Authorization middleware properties (4): 100% passing
- Project isolation properties (3): 100% passing
- Frontend route protection properties (5): 100% passing
- Audit logging properties (4): 100% passing
- User management properties (5): 100% passing
- Session management properties (4): 100% passing

## 17.5 Security Testing Completion Criteria

**Vulnerability Assessment:**
- OWASP Top 10 vulnerabilities: 0 found
- Critical security issues: 0 open
- High-severity security issues: 0 open
- Medium-severity security issues: ≤ 2 (with mitigation plan)

**Security Test Coverage:**
- Authentication security: 100% tested
- Authorization security: 100% tested
- Input validation: 100% tested
- Session management: 100% tested
- Audit logging: 100% tested

**Compliance:**
- Security scan completed: ✓
- Penetration testing completed: ✓
- Security review approved: ✓

## 17.6 Performance Testing Completion Criteria

**Load Testing:**
- Target load achieved: 100 concurrent users
- Response time targets met: P95 < 500ms
- Throughput targets met: ≥ 200 requests/second
- Error rate: < 0.1%

**Stress Testing:**
- Maximum load identified: ≥ 500 concurrent users
- Graceful degradation verified: ✓
- Recovery after stress verified: ✓

**Endurance Testing:**
- Test duration: ≥ 8 hours
- Memory leaks: None detected
- Performance degradation: < 5% over time

## 17.7 UAT Completion Criteria

**User Acceptance:**
- All UAT scenarios executed: 100%
- UAT pass rate: ≥ 90%
- User satisfaction rating: ≥ 4.0/5.0
- Critical feedback items: 0 open
- High-priority feedback items: ≤ 2

**Stakeholder Sign-off:**
- Academic supervisor approval: ✓
- Peer reviewer approval: ✓
- External reviewer approval: ✓

## 17.8 Overall Test Exit Criteria

**Test Execution:**
- All planned tests executed: 100%
- Overall test pass rate: ≥ 95%
- Test coverage: ≥ 80%

**Defect Status:**
- Critical defects: 0 open
- High-severity defects: 0 open
- Medium-severity defects: ≤ 3 (with workarounds)
- Low-severity defects: ≤ 10 (documented)

**Requirements Coverage:**
- URS coverage: 100%
- SRS coverage: 100%
- NFR coverage: 100%

**Quality Gates:**
- Code coverage: ≥ 80%
- Performance targets: 100% met
- Security requirements: 100% met
- Usability rating: ≥ 4.0/5.0

**Documentation:**
- Test plan: Complete and approved
- Test cases: Complete and reviewed
- Test records: Complete and archived
- Defect reports: Complete and closed
- Final test report: Complete and approved

**Stakeholder Approval:**
- Test Lead sign-off: ✓
- Development Lead sign-off: ✓
- Project Manager sign-off: ✓
- Academic Supervisor sign-off: ✓

# 18. Test Automation Strategy and Framework Design

## 18.1 Automation Objectives

**Primary Goals:**
- Achieve 90%+ automation coverage for regression tests
- Reduce manual testing effort by 70%
- Enable continuous testing in CI/CD pipeline
- Improve test execution speed by 80%
- Ensure consistent and repeatable test results

**Automation Scope:**
- Unit tests: 100% automated
- Integration tests: 100% automated
- System tests: 80% automated (20% manual exploratory)
- Performance tests: 100% automated
- Security tests: 90% automated (10% manual penetration)

## 18.2 Automation Framework Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                  Test Automation Framework                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Test Orchestration Layer                     │  │
│  │  - GitHub Actions (CI/CD)                                 │  │
│  │  - Test scheduling and parallel execution                 │  │
│  │  - Result aggregation and reporting                       │  │
│  └──────────────────────────────────────────────────────────┘  │
│                            │                                     │
│  ┌─────────────────────────┼────────────────────────────────┐  │
│  │                         │                                 │  │
│  ▼                         ▼                                 ▼  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐    │
│  │ Unit Test    │  │ Integration  │  │ System Test      │    │
│  │ Framework    │  │ Test         │  │ Framework        │    │
│  │              │  │ Framework    │  │                  │    │
│  │ - pytest     │  │ - pytest     │  │ - Playwright     │    │
│  │ - Jest       │  │ - Supertest  │  │ - Selenium       │    │
│  │ - Hypothesis │  │ - Testcontainers│ - Cypress       │    │
│  │ - fast-check │  │              │  │                  │    │
│  └──────────────┘  └──────────────┘  └──────────────────┘    │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Test Utilities Layer                         │  │
│  │  - Test data factories (Faker, Factory Boy)               │  │
│  │  - Mock services (Wiremock, MSW)                          │  │
│  │  - Database fixtures and seeders                          │  │
│  │  - Authentication helpers                                 │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Reporting Layer                              │  │
│  │  - Allure Reports (detailed test reports)                │  │
│  │  - Coverage reports (pytest-cov, Istanbul)                │  │
│  │  - Performance metrics (Locust reports)                   │  │
│  │  - Security scan reports (Snyk, OWASP ZAP)                │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## 18.3 Automation Tool Stack

### 18.3.1 Backend Testing Tools

| **Tool** | **Purpose** | **Version** | **Usage** |
|----------|-------------|-------------|-----------|
| pytest | Python unit/integration testing | 7.4+ | Backend API tests |
| Hypothesis | Property-based testing | 6.92+ | RBAC property tests |
| pytest-cov | Code coverage | 4.1+ | Coverage measurement |
| pytest-mock | Mocking framework | 3.12+ | External service mocks |
| Faker | Test data generation | 20.1+ | User/project data |
| Factory Boy | Model factories | 3.3+ | Database fixtures |

### 18.3.2 Frontend Testing Tools

| **Tool** | **Purpose** | **Version** | **Usage** |
|----------|-------------|-------------|-----------|
| Jest | JavaScript unit testing | 29+ | Component tests |
| React Testing Library | React component testing | 14+ | UI component tests |
| fast-check | Property-based testing | 3.15+ | Frontend property tests |
| Playwright | E2E testing | 1.40+ | System tests |
| Cypress | E2E testing (alternative) | 13+ | User workflow tests |
| MSW | API mocking | 2.0+ | Frontend API mocks |

### 18.3.3 Integration and System Testing Tools

| **Tool** | **Purpose** | **Version** | **Usage** |
|----------|-------------|-------------|-----------|
| Supertest | HTTP API testing | 6.3+ | API integration tests |
| Testcontainers | Container-based testing | 10+ | Database integration |
| Wiremock | HTTP service mocking | 3.3+ | External API mocks |
| Docker Compose | Multi-service testing | 2.23+ | Integration environment |

### 18.3.4 Performance and Security Testing Tools

| **Tool** | **Purpose** | **Version** | **Usage** |
|----------|-------------|-------------|-----------|
| Locust | Load testing | 2.20+ | Performance tests |
| k6 | Performance testing | 0.48+ | Load/stress tests |
| OWASP ZAP | Security scanning | 2.14+ | Vulnerability scanning |
| Snyk | Dependency scanning | Latest | Security vulnerabilities |
| Bandit | Python security linter | 1.7+ | Code security analysis |

## 18.4 CI/CD Integration

### 18.4.1 GitHub Actions Workflow

```yaml
name: Automated Test Suite

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run Backend Unit Tests
        run: |
          cd backend
          pytest tests/unit --cov --cov-report=xml
      - name: Run Frontend Unit Tests
        run: |
          cd frontend
          npm test -- --coverage
      - name: Upload Coverage
        uses: codecov/codecov-action@v3

  property-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run Property-Based Tests
        run: pytest tests/property --hypothesis-seed=random

  integration-tests:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
      neo4j:
        image: neo4j:5
      redis:
        image: redis:7
    steps:
      - uses: actions/checkout@v4
      - name: Run Integration Tests
        run: pytest tests/integration

  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run Snyk Security Scan
        uses: snyk/actions/python@master
      - name: Run Bandit Security Linter
        run: bandit -r backend/

  system-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run E2E Tests
        run: |
          npm run build
          npx playwright test

  performance-tests:
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4
      - name: Run Load Tests
        run: locust -f tests/performance/locustfile.py --headless
```

## 18.5 Test Data Management Strategy

### 18.5.1 Test Data Generation

**Factory Pattern Implementation:**
```python
# backend/tests/factories.py
import factory
from faker import Faker

fake = Faker()

class UserFactory(factory.Factory):
    class Meta:
        model = User
    
    username = factory.LazyFunction(lambda: fake.user_name())
    email = factory.LazyFunction(lambda: fake.email())
    role = factory.Iterator(['admin', 'programmer', 'visitor'])
    password_hash = factory.LazyFunction(lambda: hash_password('Test123!'))

class ProjectFactory(factory.Factory):
    class Meta:
        model = Project
    
    name = factory.LazyFunction(lambda: fake.company())
    repository_url = factory.LazyFunction(lambda: fake.url())
    owner = factory.SubFactory(UserFactory)
```

### 18.5.2 Test Data Isolation

**Strategy:**
- Each test uses unique data generated by factories
- Database transactions rolled back after each test
- Separate test database per environment
- Automated cleanup scripts

## 18.6 Automation Maintenance Strategy

**Code Review:**
- All test code reviewed before merge
- Test code quality standards enforced
- Regular refactoring to reduce duplication

**Flaky Test Management:**
- Automatic retry for flaky tests (max 3 attempts)
- Flaky test tracking and analysis
- Monthly flaky test remediation sprint

**Test Suite Optimization:**
- Parallel test execution (4 runners)
- Test execution time monitoring
- Slow test identification and optimization
- Selective test execution based on code changes

**Documentation:**
- Test framework documentation maintained
- Test writing guidelines published
- Onboarding guide for new testers

# 19. Complete Defect Management Lifecycle

## 19.1 Defect Lifecycle States

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│   NEW    │────▶│  OPEN    │────▶│ ASSIGNED │────▶│IN PROGRESS│
└──────────┘     └──────────┘     └──────────┘     └──────────┘
                                                           │
                                                           ▼
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  CLOSED  │◀────│ VERIFIED │◀────│  FIXED   │◀────│ RESOLVED │
└──────────┘     └──────────┘     └──────────┘     └──────────┘
      ▲                                                   │
      │                                                   ▼
      │                                            ┌──────────┐
      └────────────────────────────────────────────│REOPENED  │
                                                   └──────────┘
```

## 19.2 Defect Lifecycle Process

### 19.2.1 NEW → OPEN
- **Trigger:** Defect reported by tester
- **Action:** Test Lead reviews and validates
- **Criteria:** Defect is reproducible and valid
- **Responsible:** Test Lead
- **SLA:** 4 hours for critical, 24 hours for others

### 19.2.2 OPEN → ASSIGNED
- **Trigger:** Defect validated
- **Action:** Assign to developer based on component ownership
- **Criteria:** Developer availability confirmed
- **Responsible:** Test Lead, Development Lead
- **SLA:** 2 hours for critical, 8 hours for others

### 19.2.3 ASSIGNED → IN PROGRESS
- **Trigger:** Developer starts working on fix
- **Action:** Developer updates status, adds investigation notes
- **Criteria:** Root cause identified
- **Responsible:** Assigned Developer
- **SLA:** 4 hours for critical, 24 hours for others

### 19.2.4 IN PROGRESS → RESOLVED
- **Trigger:** Fix implemented and code reviewed
- **Action:** Developer creates PR with fix, links defect
- **Criteria:** Fix passes unit tests, code review approved
- **Responsible:** Assigned Developer
- **SLA:** 4 hours for critical, 48 hours for high, 5 days for medium

### 19.2.5 RESOLVED → VERIFIED
- **Trigger:** Fix merged to test environment
- **Action:** QA re-tests defect scenario
- **Criteria:** Defect no longer reproducible, regression tests pass
- **Responsible:** QA Engineer
- **SLA:** 4 hours for critical, 24 hours for others

### 19.2.6 VERIFIED → CLOSED
- **Trigger:** Fix verified in test environment
- **Action:** Test Lead closes defect
- **Criteria:** No regression, stakeholder approval
- **Responsible:** Test Lead
- **SLA:** 24 hours

### 19.2.7 VERIFIED → REOPENED
- **Trigger:** Defect still reproducible or regression found
- **Action:** QA reopens defect with details
- **Criteria:** Evidence of continued issue
- **Responsible:** QA Engineer
- **Next State:** Returns to ASSIGNED

## 19.3 Defect Classification

### 19.3.1 Severity Levels (Impact)

| **Severity** | **Definition** | **Examples** | **Response SLA** |
|--------------|----------------|--------------|------------------|
| **Critical** | System crash, data loss, security breach, complete feature failure | Authentication bypass, database corruption, system crash | 4 hours |
| **High** | Major feature broken, significant performance degradation, workaround difficult | PR review fails, graph not rendering, API timeout | 24 hours |
| **Medium** | Minor feature issue, workaround available, cosmetic with functional impact | UI glitch affecting usability, slow query | 3 days |
| **Low** | Cosmetic issue, minor inconvenience, no functional impact | Typo, alignment issue, color inconsistency | 1 week |

### 19.3.2 Priority Levels (Urgency)

| **Priority** | **Definition** | **Criteria** |
|--------------|----------------|--------------|
| **P0** | Immediate fix required | Critical severity + production impact |
| **P1** | Fix in current sprint | High severity OR critical severity in test |
| **P2** | Fix in next sprint | Medium severity OR low impact |
| **P3** | Fix when possible | Low severity, cosmetic only |

## 19.4 Defect Reporting Template

**GitHub Issue Template:**
```markdown
## Defect Summary
[Brief one-line description]

## Severity
- [ ] Critical
- [ ] High
- [ ] Medium
- [ ] Low

## Priority
- [ ] P0 - Immediate
- [ ] P1 - Current Sprint
- [ ] P2 - Next Sprint
- [ ] P3 - Backlog

## Environment
- **Environment:** [Development/Integration/Staging/Production]
- **OS:** [Windows 11/macOS Sonoma/Ubuntu 24.04]
- **Browser:** [Chrome 120/Firefox 121/Safari 17]
- **Build Version:** [e.g., v1.2.3-beta]

## Steps to Reproduce
1. [First step]
2. [Second step]
3. [Third step]

## Expected Behavior
[What should happen]

## Actual Behavior
[What actually happens]

## Test Case ID
[e.g., STC-AUTH-02]

## Screenshots/Logs
[Attach screenshots, error logs, stack traces]

## Additional Context
[Any other relevant information]

## Impact Assessment
- **Users Affected:** [All/Admin only/Specific role]
- **Workaround Available:** [Yes/No - describe if yes]
- **Data Loss Risk:** [Yes/No]
```

## 19.5 Defect Metrics and Tracking

### 19.5.1 Key Defect Metrics

| **Metric** | **Definition** | **Target** | **Frequency** |
|------------|----------------|------------|---------------|
| **Defect Detection Rate** | Defects found per test hour | ≥ 2 defects/hour | Weekly |
| **Defect Density** | Defects per 1000 LOC | ≤ 5 defects/KLOC | Per release |
| **Defect Removal Efficiency** | % defects found before production | ≥ 95% | Per release |
| **Mean Time to Detect (MTTD)** | Average time to find defect | ≤ 24 hours | Monthly |
| **Mean Time to Resolve (MTTR)** | Average time to fix defect | ≤ 48 hours | Monthly |
| **Defect Reopen Rate** | % defects reopened | ≤ 10% | Monthly |
| **Defect Aging** | Days defect remains open | ≤ 7 days avg | Weekly |

### 19.5.2 Defect Trend Analysis

**Weekly Defect Report:**
- New defects opened
- Defects resolved
- Defects verified
- Open defect backlog
- Defect aging analysis
- Top defect categories

**Monthly Defect Analysis:**
- Defect density trends
- Root cause analysis
- Defect prevention recommendations
- Testing effectiveness analysis

## 19.6 Root Cause Analysis (RCA)

### 19.6.1 RCA Process

**For Critical and High-Severity Defects:**
1. **Identify:** What went wrong?
2. **Analyze:** Why did it happen?
3. **Categorize:** Root cause category
4. **Prevent:** How to prevent recurrence?
5. **Document:** RCA report

### 19.6.2 Root Cause Categories

| **Category** | **Description** | **Prevention Strategy** |
|--------------|-----------------|-------------------------|
| **Requirements** | Unclear or missing requirements | Improve requirements review process |
| **Design** | Design flaw or oversight | Enhance design review, add design patterns |
| **Coding** | Implementation error | Code review, pair programming, linting |
| **Testing** | Test case gap | Improve test coverage, add edge cases |
| **Environment** | Configuration or infrastructure issue | Infrastructure as code, automated setup |
| **Integration** | Interface mismatch | Contract testing, API versioning |
| **Data** | Invalid or missing test data | Improve test data management |

# 20. Test Deliverables

## 20.1 Complete Deliverables List

| **Deliverable** | **Description** | **Owner** | **Due Date** | **Format** |
|-----------------|-----------------|-----------|--------------|------------|
| **Test Plan** | This document | Test Lead | Mar 11, 2026 | Markdown |
| **Test Cases** | Detailed test case specifications | QA Engineer | Mar 25, 2026 | Excel/Markdown |
| **Test Scripts** | Automated test code | Testers | Apr 22, 2026 | Python/JS |
| **Test Data** | Test data sets and factories | QA Engineer | Mar 18, 2026 | SQL/JSON |
| **Test Environment Guide** | Environment setup documentation | DevOps | Mar 15, 2026 | Markdown |
| **Unit Test Report** | Unit test execution results | Backend Tester | Mar 25, 2026 | HTML/PDF |
| **Integration Test Report** | Integration test results | All Testers | Apr 8, 2026 | HTML/PDF |
| **System Test Report** | System test execution results | QA Engineer | Apr 22, 2026 | HTML/PDF |
| **Security Test Report** | Security assessment results | Security Tester | Apr 29, 2026 | PDF |
| **Performance Test Report** | Load/stress test results | Performance Tester | May 6, 2026 | HTML/PDF |
| **UAT Report** | User acceptance test results | Test Lead | May 13, 2026 | PDF |
| **Defect Reports** | All defect tracking records | QA Engineer | Ongoing | GitHub Issues |
| **Coverage Reports** | Code coverage analysis | Testers | Ongoing | HTML |
| **Final Test Report** | Comprehensive test summary | Test Lead | May 20, 2026 | PDF |
| **Test Metrics Dashboard** | Real-time test metrics | Test Lead | Ongoing | Web Dashboard |
| **Lessons Learned** | Post-project analysis | Test Lead | May 20, 2026 | Markdown |

## 20.2 Test Report Standards

### 20.2.1 Daily Test Report Template

**Subject:** Daily Test Report - [Date]

**Test Execution Summary:**
- Tests Planned: [number]
- Tests Executed: [number]
- Tests Passed: [number]
- Tests Failed: [number]
- Tests Blocked: [number]
- Pass Rate: [percentage]

**New Defects:**
- Critical: [number]
- High: [number]
- Medium: [number]
- Low: [number]

**Defects Resolved:**
- [List of defect IDs]

**Blockers:**
- [List of blocking issues]

**Risks:**
- [New or updated risks]

**Next Steps:**
- [Planned activities for next day]

### 20.2.2 Weekly Test Report Template

**Subject:** Weekly Test Report - Week [number], [Date Range]

**Executive Summary:**
- Overall test progress: [percentage]
- Test execution status
- Key achievements
- Major issues and risks

**Test Execution Metrics:**
- Total test cases: [number]
- Executed: [number] ([percentage])
- Passed: [number] ([percentage])
- Failed: [number] ([percentage])
- Blocked: [number] ([percentage])

**Defect Summary:**
- Total defects: [number]
- Open defects by severity
- Defect resolution rate
- Defect aging analysis

**Coverage Metrics:**
- Code coverage: [percentage]
- Requirements coverage: [percentage]
- Risk coverage: [percentage]

**Schedule Status:**
- On track / Behind / Ahead
- Variance from plan: [days]
- Mitigation actions if behind

**Risks and Issues:**
- [List of active risks]
- [Mitigation strategies]

**Next Week Plan:**
- [Planned test activities]
- [Resource allocation]

### 20.2.3 Final Test Report Template

**1. Executive Summary**
- Project overview
- Test objectives
- Overall test results
- Go/No-go recommendation

**2. Test Scope and Coverage**
- Features tested
- Requirements coverage
- Test types executed
- Coverage metrics

**3. Test Execution Summary**
- Total test cases executed
- Pass/fail statistics
- Test execution timeline
- Deviations from plan

**4. Defect Summary**
- Total defects found
- Defects by severity
- Defects by category
- Defect resolution status
- Outstanding defects

**5. Quality Assessment**
- Code quality metrics
- Performance benchmarks
- Security assessment
- Usability evaluation

**6. Test Environment**
- Environment configuration
- Tools used
- Issues encountered

**7. Risks and Issues**
- Risks identified
- Mitigation effectiveness
- Outstanding risks

**8. Lessons Learned**
- What went well
- What could be improved
- Recommendations for future

**9. Conclusion and Recommendation**
- Overall quality assessment
- Production readiness
- Go/No-go decision

**10. Appendices**
- Detailed test results
- Coverage reports
- Defect reports
- Test metrics

# 21. Test Data Security and Compliance

## 21.1 Test Data Security Requirements

### 21.1.1 Data Classification

| **Data Type** | **Classification** | **Security Requirements** |
|---------------|-------------------|---------------------------|
| User credentials | Confidential | Encrypted at rest, hashed passwords, no production data |
| Personal information | Confidential | Anonymized, synthetic data only |
| Project code | Internal | Access controlled, no public repositories |
| API keys | Secret | Encrypted, rotated regularly, separate test keys |
| Audit logs | Internal | Access controlled, immutable |
| Test results | Internal | Access controlled, sanitized before sharing |

### 21.1.2 Data Protection Measures

**Encryption:**
- All test data encrypted at rest (AES-256)
- All data in transit encrypted (TLS 1.3)
- Database encryption enabled
- Backup encryption enabled

**Access Control:**
- Role-based access to test environments
- VPN required for staging/production access
- Multi-factor authentication for sensitive systems
- Audit logging of all data access

**Data Masking:**
- Production data never used in testing
- Synthetic data generation for all tests
- PII anonymization in test data
- Credit card numbers masked

## 21.2 Compliance Requirements

### 21.2.1 GDPR Compliance (if applicable)

**Data Minimization:**
- Only necessary data collected
- Test data retention policy: 90 days
- Automated data deletion after retention period

**Right to Erasure:**
- Test data deletion procedures documented
- Automated cleanup scripts available

**Data Protection by Design:**
- Privacy considerations in test design
- Data protection impact assessment completed

### 21.2.2 Academic Integrity

**Code of Conduct:**
- No plagiarism in test code
- Proper attribution for third-party tools
- Ethical testing practices

**Data Ethics:**
- No real user data in testing
- Respect for privacy in test scenarios
- Transparent testing practices

## 21.3 Test Data Lifecycle Management

### 21.3.1 Data Creation
- Automated generation using Faker/Factory Boy
- Seed scripts for consistent data
- Version controlled test data schemas

### 21.3.2 Data Usage
- Isolated per test environment
- Transaction rollback for unit tests
- Automated reset between test runs

### 21.3.3 Data Retention
- Development: 30 days
- Integration: 60 days
- Staging: 90 days
- Production test data: Not allowed

### 21.3.4 Data Disposal
- Automated cleanup scripts
- Secure deletion (overwrite)
- Audit trail of deletions
- Backup purging after retention period

## 21.4 Test Result Confidentiality

**Internal Distribution:**
- Test reports shared only with project team
- Access controlled documentation repository
- Watermarked sensitive reports

**External Sharing:**
- Sanitize all data before sharing
- Remove sensitive information
- Obtain approval before external distribution

**Academic Submission:**
- Anonymize any real data
- Remove API keys and credentials
- Sanitize logs and screenshots

# 22. References and Standards Compliance

## 22.1 International Standards

| **Standard** | **Title** | **Version** | **Compliance Areas** |
|--------------|-----------|-------------|----------------------|
| **IEEE 829-2008** | Software Test Documentation | 2008 | Test plan structure, test records, test reports |
| **ISO/IEC 29119** | Software and Systems Testing | 2013-2021 | Test processes, documentation, techniques |
| **ISO/IEC 25010** | Systems and Software Quality Models | 2011 | Quality characteristics, NFR testing |
| **IEEE 1012** | Software Verification and Validation | 2016 | V&V processes, test planning |
| **ISO 9001** | Quality Management Systems | 2015 | Quality assurance, continuous improvement |
| **OWASP Testing Guide** | Web Application Security Testing | v4.2 | Security testing methodology |
| **ISTQB** | Software Testing Certification | 2023 | Testing best practices, terminology |

## 22.2 Tool Documentation References

- **pytest Documentation:** https://docs.pytest.org/
- **Hypothesis Documentation:** https://hypothesis.readthedocs.io/
- **Playwright Documentation:** https://playwright.dev/
- **Locust Documentation:** https://docs.locust.io/
- **OWASP ZAP User Guide:** https://www.zaproxy.org/docs/
- **GitHub Actions Documentation:** https://docs.github.com/actions

## 22.3 Project-Specific References

- **Project SRS:** ProjectName-SRS_ver-xx.md
- **Project SDD:** ProjectName-SDD_ver-xx.md
- **Project Plan:** ProjectName-Project_plan_ver-xx.md
- **Change Request Template:** ProjectName-CR_ver-xx.md
- **Traceability Record:** ProjectName-Trecability_record_ver-xx.md

---

**Document End**

**Prepared by:** BaiXuan Zhang  
**Reviewed by:** Dr. Siraprapa  
**Approved by:** ___________________  
**Date:** February 20, 2026

**Version Control:**
- v1.0 (2026-02-07): Initial draft
- v2.1 (2026-02-19): Complete revision with comprehensive IEEE 829 and ISO/IEC 29119 compliance
- v3.0 (2026-02-20): Final version with all missing sections added per international standards gap analysis
