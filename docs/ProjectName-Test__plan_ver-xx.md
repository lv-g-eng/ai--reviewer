**\[AI-Based Reviewer on Project Code and Architecture\] - Software Test
Plan Template**

**Document Name:** \[e.g., EV_Better TestPlan_v3.1\] **Owner:** \[Names
of responsible members\] **Version:** \[e.g., v3.1\] **Date:**
\[Submission Date\]

1\. Introduction

**1.1 Purpose**

This document establishes a comprehensive testing plan for the AI-Based
Reviewer platform, including unit testing, integration testing, and
system testing strategies to discover and address potential defects
before deployment.

**1.2 Scope**

This test plan covers white-box and black-box testing activities used to
verify all user requirements (URS) and system requirements (SRS).
Testing includes functional requirements, non-functional requirements
(performance, security, usability), and integration with external
systems (GitHub API, LLM APIs).

**1.3 Acronyms and Definitions**

-   **UTC:** Unit Test Case.

-   **ITC:** Integration Test Case.

-   **STC:** System Test Case.

-   **TD:** Test Data.

-   **API:** Application Programming Interface

-   **AST:** Abstract Syntax Tree

-   **LLM:** Large Language Model

**2. Test Plan and Procedures**

**2.1 Test Objectives**

• Detect and fix all critical and high-severity bugs before production
release

• Verify coverage of all functional requirements (100% of URS)

• Validate non-functional requirements (performance, security,
scalability)

• Ensure integration with external services (GitHub, LLM APIs) functions
correctly

• Achieve minimum 80% code coverage for critical components

**2.2 Scope of Testing**

**Unit Testing:**

• AST Parser functions

• Graph Analysis algorithms

• Authentication middleware

• Data validation functions

**Integration Testing:**

• GitHub API integration

• LLM API integration

• Database operations (PostgreSQL, Neo4j)

• Redis queue operations

**System Testing:**

• End-to-end user workflows (registration, repository addition, PR
review)

• Architecture visualization and analysis

• Metrics dashboard functionality

• Configuration management

**2.3 Test Duration**

  ----------------------- ----------------------- -----------------------
  **Test Phase**          **Duration**            **Timeline**

  **Unit Testing**        **2 weeks**             **Week 1-2 of Feb
                                                  2026**

  **Integration Testing** **1 week**              **Week 3 of Feb 2026**

  **System Testing**      **2 weeks**             **Week 4 of Feb - Week
                                                  1 of Mar 2026**
  ----------------------- ----------------------- -----------------------

**2.4 Test Responsibility**

  ----------------------------------- -----------------------------------
  **Role**                            **Responsibility**

  **Test Lead**                       **Overall test strategy,
                                      coordination, and reporting**

  **Backend Developer**               **Unit tests for API services, AST
                                      parser, graph analysis**

  **Frontend Developer**              **UI component tests, integration
                                      tests for frontend**

  **QA Engineer**                     **System testing, test record
                                      documentation**
  ----------------------------------- -----------------------------------

**2.5 Test Strategy**

**White-box Testing:**

• Unit tests using pytest framework for Python backend

• Code coverage analysis with pytest-cov

• Mocking external dependencies (GitHub API, LLM APIs)

**Black-box Testing:**

• System testing based on use cases

• Boundary value analysis for input validation

• Equivalence partitioning for test data

**Automated Testing:**

• CI/CD integration with GitHub Actions

• Automated regression testing on each commit

• Performance testing with Locust for load simulation

**2.6 Test Environment**

**Hardware:**

• MacBook Pro M2, 16GB RAM (local development)

• AWS EC2 t3.medium instances (staging environment)

**Software:**

• Operating System: macOS Sonoma 14.0, Ubuntu 24.04 LTS

• Browsers: Chrome 120+, Firefox 121+, Safari 17+

• Python 3.11+, Node.js 20+

• PostgreSQL 15, Neo4j 5.x, Redis 7.x

• Docker 24.x for containerization

**3. Unit Test Plan**

\[Detail the testing of individual components or controllers.\]

-   **UTC ID:** \[e.g., UTC-01\].

-   **Description:** \[What is being checked\].

-   **Prerequisite:** \[Requirements before testing\].

-   **Test Cases Table:**

**4. System Testing**

**STC-01: User Registration**

**Description:** Verify a guest can successfully register to the system

**Prerequisite:** Browser is not logged in, on registration page

**Test Script:**

1\. Navigate to registration page

2\. Enter valid username (e.g., \'testuser123\')

3\. Enter valid email (e.g., \'test@example.com\')

4\. Enter valid password meeting complexity requirements

5\. Click \'Register\' button

6\. Verify success message is displayed

7\. Verify redirect to login page

**Expected Result:** User account created, confirmation email sent,
redirected to login

**STC-02: Add GitHub Repository**

**Description:** Verify user can add a GitHub repository for monitoring

**Prerequisite:** User is logged in, on project management page

**Test Script:**

1\. Click \'Add Repository\' button

2\. Enter valid GitHub repository URL

3\. Select target branch (optional)

4\. Click \'Connect Repository\' button

5\. Verify webhook configuration success message

6\. Verify repository appears in project list

7\. Verify initial analysis is queued

**Expected Result:** Repository added, webhook configured, initial
analysis starts

**STC-03: Automated PR Review**

**Description:** Verify system performs automated code review on pull
request

**Prerequisite:** Repository connected with active webhook

**Test Script:**

1\. Create pull request on GitHub with code changes

2\. Wait for webhook trigger (max 10 seconds)

3\. Verify analysis task appears in queue

4\. Wait for analysis completion (8-50 seconds)

5\. Verify review comments posted on GitHub PR

6\. Verify issues categorized by severity

7\. Verify dependency graph updated in Neo4j

**Expected Result:** AI review feedback posted, issues identified, graph
updated

**STC-04: Architecture Visualization**

**Description:** Verify user can view interactive architecture graph

**Prerequisite:** Repository analyzed at least once

**Test Script:**

1\. Navigate to Architecture tab

2\. Select project from dropdown

3\. Verify dependency graph renders

4\. Click on a node to view details

5\. Apply filter (e.g., view by service)

6\. Verify circular dependencies highlighted in red

7\. Export graph as PNG

**Expected Result:** Graph displays correctly, filters work, export
succeeds

**STC-05: Code Quality Metrics**

**Description:** Verify manager can view comprehensive metrics dashboard

**Prerequisite:** Manager role, historical analysis data exists

**Test Script:**

1\. Navigate to Metrics dashboard

2\. Select date range filter

3\. Verify trend charts display correctly

4\. Verify defect density metrics shown

5\. Click on specific metric for drill-down

6\. Export report as PDF

**Expected Result:** Dashboard loads, charts accurate, export succeeds

**\[Feature Name\]**

-   **STC ID:** \[e.g., STC-01\].

-   **Description:** \[e.g., Testing if a Guest can register\].

-   **Prerequisite:** \[e.g., Browser not logged in\].

-   **Test Script (Steps):**
