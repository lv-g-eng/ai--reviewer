# Implementation Plan: Enterprise RBAC Authentication System

## Overview

This implementation plan breaks down the enterprise RBAC authentication system into discrete coding tasks. The system will be built in Python with a focus on security, testability, and maintainability. We'll use FastAPI for the API layer, PyJWT for token management, bcrypt for password hashing, and Hypothesis for property-based testing.

The implementation follows a bottom-up approach: data models → core services → middleware → API endpoints → frontend components → integration.

## Tasks

- [x] 1. Set up project structure and dependencies
  - Create Python project with virtual environment
  - Install dependencies: FastAPI, PyJWT, bcrypt, SQLAlchemy, Hypothesis, pytest
  - Set up project directory structure: `/models`, `/services`, `/middleware`, `/api`, `/tests`
  - Create configuration file for JWT secret, token expiration, database connection
  - _Requirements: All_

- [x] 2. Implement data models and database schema
  - [x] 2.1 Create User, Role, and Permission models
    - Define User model with id, username, password_hash, role, created_at, updated_at, last_login, is_active
    - Define Role enum (ADMIN, PROGRAMMER, VISITOR)
    - Define Permission enum with all 11 permission types
    - Create role-permission mapping dictionary
    - _Requirements: 2.1, 9.1, 9.2, 9.3, 9.4_
  
  - [x] 2.2 Create Project and ProjectAccess models
    - Define Project model with id, name, description, owner_id, created_at, updated_at
    - Define ProjectAccess model with project_id, user_id, granted_at, granted_by
    - Add relationship between User and Project (one-to-many)
    - _Requirements: 2.3, 4.1, 4.5_
  
  - [x] 2.3 Create Session and AuditLog models
    - Define Session model with id, user_id, token, issued_at, expires_at, is_valid, device_info, ip_address
    - Define AuditLog model with id, timestamp, user_id, username, action, resource_type, resource_id, ip_address, user_agent, success, error_message
    - _Requirements: 10.1, 7.1_
  
  - [x] 2.4 Set up database migrations and initialization
    - Create database initialization script
    - Add script to create default admin user
    - _Requirements: 8.4_

- [x] 3. Implement Authentication Service
  - [x] 3.1 Implement password hashing and verification
    - Create hash_password function using bcrypt
    - Create verify_password function
    - _Requirements: 1.5_
  
  - [x] 3.2 Write property test for password hashing
    - **Property 5: Passwords are never stored in plaintext**
    - **Validates: Requirements 1.5**
  
  - [x] 3.3 Implement JWT token generation and validation
    - Create generate_token function that creates JWT with userId, username, role, iat, exp
    - Create validate_token function that verifies JWT signature and expiration
    - Create refresh_token function for token renewal
    - _Requirements: 1.1, 1.4, 10.5_
  
  - [x] 3.4 Write property tests for token operations
    - **Property 1: Valid credentials generate valid JWT tokens**
    - **Validates: Requirements 1.1**
    - **Property 4: Expired tokens require re-authentication**
    - **Validates: Requirements 1.4, 10.2**
    - **Property 36: Active usage refreshes tokens**
    - **Validates: Requirements 10.5**
  
  - [x] 3.5 Implement login and logout functions
    - Create login function that validates credentials and returns JWT
    - Create logout function that invalidates session
    - Handle invalid credentials with generic error messages
    - _Requirements: 1.1, 1.2, 1.3, 6.2_
  
  - [x] 3.6 Write property tests for authentication
    - **Property 2: Invalid credentials are rejected**
    - **Validates: Requirements 1.2, 6.2**
    - **Property 3: Logout invalidates sessions**
    - **Validates: Requirements 1.3**

- [x] 4. Implement RBAC Service
  - [x] 4.1 Implement permission checking functions
    - Create has_permission function that checks if user's role includes permission
    - Create get_role_permissions function that returns all permissions for a role
    - _Requirements: 9.5_
  
  - [x] 4.2 Write property test for permission checking
    - **Property 32: Authorization checks verify role permissions**
    - **Validates: Requirements 9.5**
  
  - [x] 4.3 Implement project access control functions
    - Create can_access_project function that checks ownership or access grants
    - Create grant_project_access function for admins/owners
    - Create revoke_project_access function
    - Handle admin bypass logic
    - _Requirements: 4.2, 4.4, 4.5_
  
  - [x] 4.4 Write property tests for project access control
    - **Property 16: Project access requires ownership or grant**
    - **Validates: Requirements 4.2**
    - **Property 17: Admins bypass project isolation**
    - **Validates: Requirements 4.4**
    - **Property 18: Access grants enable project access**
    - **Validates: Requirements 4.5**
  
  - [x] 4.5 Implement role assignment and validation
    - Create assign_role function that updates user role
    - Create validate_role function that ensures role is valid
    - Implement immediate permission update for active sessions
    - _Requirements: 2.1, 8.2_
  
  - [x] 4.6 Write property tests for role management
    - **Property 6: Users have exactly one role**
    - **Validates: Requirements 2.1**
    - **Property 29: Role updates apply immediately**
    - **Validates: Requirements 8.2**

- [ ] 5. Checkpoint - Ensure core services work
  - Run all tests for authentication and RBAC services
  - Verify password hashing, token generation, and permission checking
  - Ask the user if questions arise

- [-] 6. Implement Authorization Middleware
  - [x] 6.1 Create token authentication middleware
    - Implement authenticate_token middleware that extracts and validates JWT from Authorization header
    - Set request.user with token payload on success
    - Return 401 for invalid/missing tokens
    - _Requirements: 3.2, 3.5_
  
  - [x] 6.2 Write property test for token authentication
    - **Property 15: Invalid tokens return 401**
    - **Validates: Requirements 3.5**
  
  - [x] 6.3 Create role-based authorization middleware
    - Implement check_role middleware that accepts required role
    - Return 403 if user role doesn't match required role
    - Allow request to proceed if role matches
    - _Requirements: 3.3, 3.4_
  
  - [x] 6.4 Write property tests for role authorization
    - **Property 13: Matching roles grant access**
    - **Validates: Requirements 3.3**
    - **Property 14: Non-matching roles return 403**
    - **Validates: Requirements 3.4**
  
  - [x] 6.5 Create permission-based authorization middleware
    - Implement check_permission middleware that accepts required permission
    - Use RBAC service to verify user has permission
    - Return 403 if permission check fails
    - _Requirements: 2.2, 2.5, 2.6_
  
  - [x] 6.6 Write property tests for permission authorization
    - **Property 7: Admin users have all permissions**
    - **Validates: Requirements 2.2**
    - **Property 10: Visitors cannot modify resources**
    - **Validates: Requirements 2.5**
  
  - [ ] 6.7 Create project access middleware
    - Implement check_project_access middleware that validates project access
    - Extract project_id from request params
    - Use RBAC service to check ownership or access grants
    - _Requirements: 2.4, 4.3_
  
  - [ ] 6.8 Write property test for project access middleware
    - **Property 9: Unauthorized project access is denied**
    - **Validates: Requirements 2.4, 4.3**

- [ ] 7. Implement Audit Service
  - [ ] 7.1 Create audit logging functions
    - Implement log_action function that creates AuditLog entries
    - Extract IP address and user agent from request context
    - Ensure immediate persistence to database
    - Prevent modification/deletion of audit logs
    - _Requirements: 7.1, 7.3, 7.4_
  
  - [ ] 7.2 Write property tests for audit logging
    - **Property 24: Audit logs contain required fields**
    - **Validates: Requirements 7.1**
    - **Property 25: Audit logs persist immediately**
    - **Validates: Requirements 7.3**
    - **Property 26: Users cannot modify audit logs**
    - **Validates: Requirements 7.4**
  
  - [ ] 7.3 Implement audit log query functions
    - Create query_logs function with filters for userId, action, date range
    - Implement pagination support
    - _Requirements: 7.5_
  
  - [ ] 7.4 Write property test for audit log queries
    - **Property 27: Audit log queries filter correctly**
    - **Validates: Requirements 7.5**
  
  - [ ] 7.5 Add audit logging to sensitive operations
    - Integrate log_action calls for: login, logout, project access, user CRUD, role changes, config modifications
    - Use decorator pattern for automatic logging
    - _Requirements: 7.2_

- [ ] 8. Implement API endpoints
  - [ ] 8.1 Create authentication endpoints
    - POST /auth/login - accepts username/password, returns JWT
    - POST /auth/logout - invalidates session
    - POST /auth/refresh - refreshes JWT token
    - Apply audit logging to all endpoints
    - _Requirements: 1.1, 1.2, 1.3, 10.5_
  
  - [ ] 8.2 Create user management endpoints
    - POST /users - create user (admin only)
    - GET /users - list users (admin only)
    - GET /users/{id} - get user details
    - PUT /users/{id}/role - update user role (admin only)
    - DELETE /users/{id} - delete user (admin only)
    - Apply check_role(ADMIN) middleware
    - Prevent deletion of last admin
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_
  
  - [ ] 8.3 Write property tests for user management
    - **Property 28: User creation requires all fields**
    - **Validates: Requirements 8.1**
    - **Property 30: User deletion invalidates sessions**
    - **Validates: Requirements 8.3**
    - **Property 31: User list contains required fields**
    - **Validates: Requirements 8.5**
  
  - [ ] 8.4 Create project management endpoints
    - POST /projects - create project (programmer/admin)
    - GET /projects - list accessible projects
    - GET /projects/{id} - get project details
    - PUT /projects/{id} - update project (owner/admin)
    - DELETE /projects/{id} - delete project (owner/admin)
    - POST /projects/{id}/access - grant access (owner/admin)
    - DELETE /projects/{id}/access/{userId} - revoke access (owner/admin)
    - Apply check_project_access middleware
    - _Requirements: 2.3, 2.4, 4.1, 4.2, 4.5_
  
  - [ ] 8.5 Write property tests for project management
    - **Property 8: Project creation sets ownership**
    - **Validates: Requirements 2.3, 4.1**
    - **Property 11: Visitors have read-only access to assigned projects**
    - **Validates: Requirements 2.6**
  
  - [ ] 8.6 Create audit log endpoints
    - GET /audit/logs - query audit logs (admin only)
    - GET /audit/logs/user/{userId} - get user's audit logs (admin only)
    - Apply check_role(ADMIN) middleware
    - _Requirements: 7.5_

- [ ] 9. Implement session management
  - [ ] 9.1 Create session lifecycle functions
    - Implement create_session function on login
    - Implement invalidate_session function on logout
    - Implement invalidate_all_user_sessions for password changes
    - Support concurrent sessions per user
    - _Requirements: 10.1, 10.3, 10.4_
  
  - [ ] 9.2 Write property tests for session management
    - **Property 33: Login creates session with expiration**
    - **Validates: Requirements 10.1**
    - **Property 34: Concurrent sessions are supported**
    - **Validates: Requirements 10.3**
    - **Property 35: Password change invalidates all sessions**
    - **Validates: Requirements 10.4**

- [ ] 10. Checkpoint - Ensure backend is complete
  - Run all backend tests (unit and property tests)
  - Test API endpoints with curl or Postman
  - Verify audit logging is working
  - Ask the user if questions arise

- [ ] 11. Implement frontend route guard
  - [ ] 11.1 Create route guard component
    - Implement RouteGuard class that checks user permissions
    - Add can_activate method that validates route access
    - Add get_redirect_path method for unauthorized users
    - Check token validity on each navigation
    - _Requirements: 5.1, 5.2, 5.4, 5.5_
  
  - [ ] 11.2 Write property tests for route guard
    - **Property 19: Non-Admins cannot access admin routes**
    - **Validates: Requirements 5.1**
    - **Property 20: Users without config permissions cannot access settings**
    - **Validates: Requirements 5.2**
    - **Property 22: Expired sessions redirect to login**
    - **Validates: Requirements 5.4**
  
  - [ ] 11.3 Apply route guards to protected routes
    - Protect /admin/* routes with ADMIN role check
    - Protect /settings/* routes with MODIFY_CONFIG permission check
    - Redirect to /unauthorized for failed checks
    - Redirect to /login for expired sessions
    - _Requirements: 5.1, 5.2, 5.4_

- [ ] 12. Implement permission-based UI components
  - [ ] 12.1 Create permission HOC/decorator
    - Implement with_permission decorator for components
    - Implement CanAccess component for conditional rendering
    - Check user permissions from auth context
    - _Requirements: 5.3_
  
  - [ ] 12.2 Write property test for conditional rendering
    - **Property 21: UI elements hidden without permissions**
    - **Validates: Requirements 5.3**
  
  - [ ] 12.3 Apply permission checks to UI elements
    - Hide Delete buttons without DELETE_* permissions
    - Hide Configure buttons without MODIFY_CONFIG permission
    - Hide user management UI for non-admins
    - _Requirements: 5.3_

- [ ] 13. Implement login UI
  - [ ] 13.1 Create login page component
    - Create form with username and password fields
    - Add submit button with loading state
    - Display error messages without revealing username/password validity
    - Transmit credentials over HTTPS (configuration)
    - _Requirements: 6.1, 6.2, 6.3, 6.4_
  
  - [ ] 13.2 Implement authenticated user redirect
    - Check for valid token on login page load
    - Redirect authenticated users to dashboard
    - _Requirements: 6.5_
  
  - [ ] 13.3 Write property test for authenticated redirect
    - **Property 23: Authenticated users redirected from login**
    - **Validates: Requirements 6.5**

- [ ] 14. Integration and wiring
  - [ ] 14.1 Wire authentication flow
    - Connect login UI to /auth/login endpoint
    - Store JWT token in secure storage (httpOnly cookie or localStorage)
    - Add token to Authorization header for all API requests
    - Handle token refresh before expiration
    - _Requirements: 1.1, 1.3, 10.5_
  
  - [ ] 14.2 Wire authorization checks
    - Ensure all protected endpoints use appropriate middleware
    - Verify frontend route guards are applied to all protected routes
    - Test role-based access across all user types
    - _Requirements: 3.2, 3.3, 3.4, 5.1, 5.2_
  
  - [ ] 14.3 Wire audit logging
    - Verify all sensitive operations trigger audit logs
    - Test audit log query endpoints
    - Ensure logs cannot be modified
    - _Requirements: 7.1, 7.2, 7.3, 7.4_
  
  - [ ] 14.4 Write integration tests
    - Test complete authentication flow: login → access resource → logout
    - Test role-based scenarios: Admin vs Programmer vs Visitor
    - Test project isolation with multiple programmers
    - Test session lifecycle: login → refresh → expiration
    - _Requirements: All_

- [ ] 15. Final checkpoint - Complete system validation
  - Run all tests (unit, property, integration)
  - Verify all 36 correctness properties pass
  - Test security scenarios (token tampering, unauthorized access)
  - Verify audit logs for all sensitive operations
  - Ask the user if questions arise

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Property tests use Hypothesis library with minimum 100 iterations
- All passwords must be hashed with bcrypt (never stored in plaintext)
- JWT tokens should have reasonable expiration (e.g., 1 hour) with refresh capability
- Audit logs should be write-only (no updates or deletes allowed)
- The last Admin user cannot be deleted to prevent system lockout
- All API endpoints should return consistent error response format
- Frontend should handle token expiration gracefully with automatic redirect to login
