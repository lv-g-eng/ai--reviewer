/**
 * useRole Hook
 * Checks user role and provides role-based utilities
 */
'use client';

import { useAuth } from '@/contexts/AuthContext';
import { Role } from '@/types/rbac';
import { useMemo } from 'react';

interface UseRoleReturn {
  hasRole: (requiredRole: Role) => boolean;
  currentRole: Role | null;
  loading: boolean;
}

export function useRole(): UseRoleReturn {
  const { user, loading } = useAuth();

  const currentRole = useMemo(() => {
    if (!user?.role) return null;
    return user.role as Role;
  }, [user]);

  const hasRole = (requiredRole: Role): boolean => {
    if (!currentRole) return false;
    return currentRole === requiredRole;
  };

  return {
    hasRole,
    currentRole,
    loading,
  };
}
