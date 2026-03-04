-- ================================================
-- RBAC Seed Data - Default Users for 5 Roles
-- ================================================
-- Password: Admin123!
-- This creates default users for all 5 role types

INSERT INTO rbac_users (id, username, password_hash, role, created_at, updated_at, is_active)
VALUES (
    'admin-0000-0000-0000-000000000001',
    'admin',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqRJSm9T8u',
    'ADMIN',
    NOW(),
    NOW(),
    true
)
ON CONFLICT (id) DO NOTHING;

-- Create test users for all 5 roles
INSERT INTO rbac_users (id, username, password_hash, role, created_at, updated_at, is_active)
VALUES 
    (
        'mngr-0000-0000-0000-000000000002',
        'manager',
        '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqRJSm9T8u',
        'MANAGER',
        NOW(),
        NOW(),
        true
    ),
    (
        'revw-0000-0000-0000-000000000003',
        'reviewer',
        '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqRJSm9T8u',
        'REVIEWER',
        NOW(),
        NOW(),
        true
    ),
    (
        'prog-0000-0000-0000-000000000004',
        'programmer',
        '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqRJSm9T8u',
        'PROGRAMMER',
        NOW(),
        NOW(),
        true
    ),
    (
        'visit-0000-0000-0000-000000000005',
        'visitor',
        '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqRJSm9T8u',
        'VISITOR',
        NOW(),
        NOW(),
        true
    )
ON CONFLICT (id) DO NOTHING;

-- Note: All users have the same password: Admin123!
-- Change these passwords after first login in production!
-- 
-- Role Hierarchy:
-- ADMIN: Full system control
-- MANAGER: Project oversight & ROI
-- REVIEWER: Read/Write analysis
-- PROGRAMMER: CRUD own branch
-- VISITOR: Read-only grants
