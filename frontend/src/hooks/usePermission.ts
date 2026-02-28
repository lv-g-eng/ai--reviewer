/**
 * usePermission Hook
 * Checks if user has specific permissions based on their role
 */
'use client';

import { useAuth } from '@/contexts/AuthContext';
import { Permission, Role } from '@/types/rbac';
import { useMemo } from 'react';

// Role-Permission mapping
const ROLE_PERMISSIONS: Record<Role, Permission[]> = {
  [Role.ADMIN]: [
    Permission.VIEW_PROJECTS,
    Permission.CREATE_PROJECT,
    Permission.MODIFY_PROJECT,
    Permission.DELETE_PROJECT,
    Permission.VIEW_USERS,
    Permission.CREATE_USER,
    Permission.MODIFY_USER,
    Permission.DELETE_USER,
    Permission.VIEW_REVIEWS,
    Permission.CREATE_REVIEW,
    Permission.MODIFY_REVIEW,
    Permission.MODIFY_CONFIG,
  ],
  [Role.DEVELOPER]: [
    Permission.VIEW_PROJECTS,
    Permission.CREATE_PROJECT,
    Permission.MODIFY_PROJECT,
    Permission.VIEW_REVIEWS,
    Permission.CREATE_REVIEW,
    Permission.MODIFY_REVIEW,
  ],
  [Role.REVIEWER]: [
    Permission.VIEW_PROJECTS,
    Permission.VIEW_REVIEWS,
    Permission.CREATE_REVIEW,
    Permission.MODIFY_REVIEW,
  ],
  [Role.COMPLIANCE_OFFICER]: [
    Permission.VIEW_PROJECTS,
    Permission.VIEW_REVIEWS,
    Permission.MODIFY_CONFIG,
  ],
  [Role.MANAGER]: [
    Permission.VIEW_PROJECTS,
    Permission.VIEW_USERS,
    Permission.VIEW_REVIEWS,
  ],
};

interface UsePermissionReturn {
  hasPermission: (permission: Permission) => boolean;
  loading: boolean;
}

export function usePermission(): UsePermissionReturn {
  const { user, loading } = useAuth();

  const userPermissions = useMemo(() => {
    if (!user?.role) return [];
    const role = user.role as Role;
    return ROLE_PERMISSIONS[role] || [];
  }, [user]);

  const hasPermission = (permission: Permission): boolean => {
    return userPermissions.includes(permission);
  };

  return {
    hasPermission,
    loading,
  };
}
