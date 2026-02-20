/**
 * PermissionCheck Component
 * Conditional rendering based on permissions and roles
 */
'use client';

import { useRole } from '@/hooks/useRole';
import { usePermission } from '@/hooks/usePermission';
import { Role, Permission } from '@/types/rbac';

interface PermissionCheckProps {
  children: React.ReactNode;
  permission?: Permission;
  role?: Role;
  fallback?: React.ReactNode;
}

export function PermissionCheck({
  children,
  permission,
  role,
  fallback = null,
}: PermissionCheckProps) {
  const { hasRole, loading: roleLoading } = useRole();
  const { hasPermission, loading: permissionLoading } = usePermission();

  const loading = roleLoading || permissionLoading;

  // Don't render anything while loading
  if (loading) {
    return <>{fallback}</>;
  }

  // Check role requirement
  if (role && !hasRole(role)) {
    return <>{fallback}</>;
  }

  // Check permission requirement
  if (permission && !hasPermission(permission)) {
    return <>{fallback}</>;
  }

  return <>{children}</>;
}
