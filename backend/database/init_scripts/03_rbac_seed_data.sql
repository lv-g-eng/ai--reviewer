-- ================================================
-- RBAC Seed Data - Default Users for 5 Roles
-- ================================================
-- IMPORTANT: These are placeholder password hashes for development only.
-- In production, create users through secure registration or API only.
-- The hash below is a placeholder and will not work for login.

INSERT INTO rbac_users (id, username, password_hash, role, created_at, updated_at, is_active)
VALUES (
    'admin-0000-0000-0000-000000000001',
    'admin',
    '$2b$12$PLACEHOLDERHASHREQUIRESREPLACEMENT',
    'ADMIN',
    NOW(),
    NOW(),
    false
)
ON CONFLICT (id) DO NOTHING;

-- Create test users for all 5 roles (all disabled for security)
INSERT INTO rbac_users (id, username, password_hash, role, created_at, updated_at, is_active)
VALUES 
    (
        'mngr-0000-0000-0000-000000000002',
        'manager',
        '$2b$12$PLACEHOLDERHASHREQUIRESREPLACEMENT',
        'MANAGER',
        NOW(),
        NOW(),
        false
    ),
    (
        'revw-0000-0000-0000-000000000003',
        'reviewer',
        '$2b$12$PLACEHOLDERHASHREQUIRESREPLACEMENT',
        'REVIEWER',
        NOW(),
        NOW(),
        false
    ),
    (
        'prog-0000-0000-0000-000000000004',
        'programmer',
        '$2b$12$PLACEHOLDERHASHREQUIRESREPLACEMENT',
        'PROGRAMMER',
        NOW(),
        NOW(),
        false
    ),
    (
        'visit-0000-0000-0000-000000000005',
        'visitor',
        '$2b$12$PLACEHOLDERHASHREQUIRESREPLACEMENT',
        'VISITOR',
        NOW(),
        NOW(),
        false
    )
ON CONFLICT (id) DO NOTHING;
