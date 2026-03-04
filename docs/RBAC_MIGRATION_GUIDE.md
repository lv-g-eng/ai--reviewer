# RBAC Migration Guide: 3 Roles → 5 Roles

This guide helps you migrate from the previous 3-role system to the new 5-role system.

## Overview of Changes

### Previous System (3 Roles)
- ADMIN
- PROGRAMMER
- VISITOR

### New System (5 Roles)
- ADMIN (unchanged)
- MANAGER (new)
- REVIEWER (new)
- PROGRAMMER (unchanged)
- VISITOR (unchanged)

## Database Migration

### Step 1: Update Database Schema

The role column in the `rbac_users` table already supports string values, so no schema changes are required. The new roles (MANAGER, REVIEWER) can be inserted directly.

### Step 2: Run Seed Data Script

Execute the updated seed data script to create default users for the new roles:

```bash
# From the project root
psql -U your_username -d your_database -f backend/database/init_scripts/03_rbac_seed_data.sql
```

This will create:
- `manager` user with MANAGER role
- `reviewer` user with REVIEWER role

### Step 3: Verify New Users

```sql
SELECT id, username, role, is_active 
FROM rbac_users 
WHERE role IN ('MANAGER', 'REVIEWER');
```

Expected output:
```
id                                   | username | role     | is_active
-------------------------------------|----------|----------|----------
mngr-0000-0000-0000-000000000002    | manager  | MANAGER  | true
revw-0000-0000-0000-000000000003    | reviewer | REVIEWER | true
```

## Backend Code Updates

### Updated Files
1. `enterprise_rbac_auth/models/enums.py` - Role enum and permission mappings
2. `backend/app/auth/services/rbac_service.py` - No changes needed (uses enum)
3. `backend/database/init_scripts/03_rbac_seed_data.sql` - New seed data
4. `backend/tests/test_rbac_properties.py` - Updated test strategies

### No Changes Required
The RBAC service automatically uses the updated `ROLE_PERMISSIONS` mapping, so existing permission checks will work with the new roles without code changes.

## Frontend Code Updates

### Updated Files
1. `frontend/src/types/rbac.ts` - Role and Permission enums
2. `frontend/src/hooks/usePermission.ts` - Permission mappings
3. `shared/types/index.ts` - Shared type definitions

### UI Components
Update any UI components that display or filter by role:

```typescript
// Before
const roles = ['ADMIN', 'PROGRAMMER', 'VISITOR'];

// After
const roles = ['ADMIN', 'MANAGER', 'REVIEWER', 'PROGRAMMER', 'VISITOR'];
```

### Role Selection Dropdowns
Update role selection components:

```typescript
// Example: RoleSelector.tsx
const roleOptions = [
  { value: Role.ADMIN, label: 'Admin - Full System Control' },
  { value: Role.MANAGER, label: 'Manager - Project Oversight & ROI' },
  { value: Role.REVIEWER, label: 'Reviewer - Read/Write Analysis' },
  { value: Role.PROGRAMMER, label: 'Programmer - CRUD Own Branch' },
  { value: Role.VISITOR, label: 'Visitor - Read-Only' },
];
```

## Testing

### Run Backend Tests

```bash
# Run RBAC property tests
pytest backend/tests/test_rbac_properties.py -v

# Run all auth tests
pytest backend/tests/ -k "rbac or auth" -v
```

### Run Frontend Tests

```bash
cd frontend
npm test -- --testPathPattern="rbac|permission"
```

### Manual Testing Checklist

- [ ] Login with each of the 5 roles
- [ ] Verify ADMIN can access all features
- [ ] Verify MANAGER can create/delete projects
- [ ] Verify REVIEWER can update projects but not create/delete
- [ ] Verify PROGRAMMER can create projects
- [ ] Verify VISITOR has read-only access
- [ ] Test permission checks in UI (buttons, menus should show/hide correctly)
- [ ] Test API endpoints with different roles

## Assigning New Roles to Existing Users

### Via SQL

```sql
-- Assign MANAGER role to a user
UPDATE rbac_users 
SET role = 'MANAGER', updated_at = NOW() 
WHERE username = 'john.doe';

-- Assign REVIEWER role to a user
UPDATE rbac_users 
SET role = 'REVIEWER', updated_at = NOW() 
WHERE username = 'jane.smith';
```

### Via API (Admin Only)

```bash
# Assign MANAGER role
curl -X PUT http://localhost:8000/api/users/{user_id}/role \
  -H "Authorization: Bearer {admin_token}" \
  -H "Content-Type: application/json" \
  -d '{"role": "MANAGER"}'

# Assign REVIEWER role
curl -X PUT http://localhost:8000/api/users/{user_id}/role \
  -H "Authorization: Bearer {admin_token}" \
  -H "Content-Type: application/json" \
  -d '{"role": "REVIEWER"}'
```

## Rollback Plan

If you need to rollback to the 3-role system:

### 1. Reassign Users with New Roles

```sql
-- Convert MANAGER users to PROGRAMMER
UPDATE rbac_users 
SET role = 'PROGRAMMER', updated_at = NOW() 
WHERE role = 'MANAGER';

-- Convert REVIEWER users to PROGRAMMER
UPDATE rbac_users 
SET role = 'PROGRAMMER', updated_at = NOW() 
WHERE role = 'REVIEWER';
```

### 2. Restore Previous Code

```bash
git revert <commit_hash>
```

### 3. Restart Services

```bash
docker-compose restart backend frontend
```

## Common Issues and Solutions

### Issue: "Invalid role" error when logging in

**Solution:** Clear browser cache and local storage, then login again.

```javascript
// In browser console
localStorage.clear();
sessionStorage.clear();
location.reload();
```

### Issue: Permission denied for new roles

**Solution:** Verify the role is correctly set in the database and the user has logged in after the role change.

```sql
-- Check user's current role
SELECT id, username, role, updated_at 
FROM rbac_users 
WHERE username = 'problematic_user';
```

### Issue: Frontend shows old role options

**Solution:** Clear build cache and rebuild:

```bash
cd frontend
rm -rf .next node_modules/.cache
npm run build
npm run dev
```

## Best Practices

1. **Role Assignment Strategy**
   - Use MANAGER for project leads and stakeholders who need oversight
   - Use REVIEWER for QA engineers and code reviewers
   - Keep PROGRAMMER for developers
   - Use VISITOR for external stakeholders

2. **Permission Auditing**
   - Regularly review user roles and permissions
   - Log role changes for audit trails
   - Implement periodic access reviews

3. **Testing**
   - Test with each role before deploying to production
   - Use the default test accounts for integration testing
   - Verify permission boundaries are enforced

## Support

For questions or issues:
- Check the main documentation: `docs/RBAC_ROLES.md`
- Review test cases: `backend/tests/test_rbac_properties.py`
- Contact the development team

## Changelog

### Version 2.0.0 (Current)
- Added MANAGER role with project oversight capabilities
- Added REVIEWER role with read/write analysis permissions
- Updated permission matrix
- Enhanced role hierarchy
- Added comprehensive documentation

### Version 1.0.0 (Previous)
- Initial 3-role system (ADMIN, PROGRAMMER, VISITOR)
