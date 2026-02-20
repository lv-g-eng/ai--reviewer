/**
 * RBACGuard Component
 * Route protection based on roles and permissions
 */
'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Loader2 } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { useRole } from '@/hooks/useRole';
import { usePermission } from '@/hooks/usePermission';
import { Role, Permission } from '@/types/rbac';

interface RBACGuardProps {
  children: React.ReactNode;
  requiredRole?: Role;
  requiredPermission?: Permission;
  fallback?: React.ReactNode;
}

export function RBACGuard({
  children,
  requiredRole,
  requiredPermission,
  fallback,
}: RBACGuardProps) {
  const router = useRouter();
  const { user, session, loading: authLoading } = useAuth();
  const { hasRole, loading: roleLoading } = useRole();
  const { hasPermission, loading: permissionLoading } = usePermission();

  const loading = authLoading || roleLoading || permissionLoading;

  useEffect(() => {
    // Check if session is expired
    if (!loading && !session) {
      router.push('/login');
      return;
    }

    // Check role requirement
    if (!loading && requiredRole && !hasRole(requiredRole)) {
      router.push('/unauthorized');
      return;
    }

    // Check permission requirement
    if (!loading && requiredPermission && !hasPermission(requiredPermission)) {
      router.push('/unauthorized');
      return;
    }
  }, [
    loading,
    session,
    user,
    requiredRole,
    requiredPermission,
    hasRole,
    hasPermission,
    router,
  ]);

  // Show loading state
  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary-600" />
      </div>
    );
  }

  // Check if session is expired
  if (!session) {
    return fallback || null;
  }

  // Check role requirement
  if (requiredRole && !hasRole(requiredRole)) {
    return fallback || null;
  }

  // Check permission requirement
  if (requiredPermission && !hasPermission(requiredPermission)) {
    return fallback || null;
  }

  return <>{children}</>;
}
