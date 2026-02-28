/**
 * RouteGuard Component
 * Protects routes by checking authentication and authorization
 * 
 * Requirements:
 * - 3.4: Redirect unauthenticated users to login page
 * - 3.5: Display 403 Forbidden for unauthorized access
 */
'use client';

import { useEffect } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { Loader2 } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { Role, Permission } from '@/types/rbac';

interface RouteGuardProps {
  children: React.ReactNode;
  requiredRole?: Role;
  requiredPermission?: Permission;
  redirectTo?: string;
}

/**
 * RouteGuard protects routes based on authentication and authorization
 * 
 * @param children - Content to render if authorized
 * @param requiredRole - Optional role requirement
 * @param requiredPermission - Optional permission requirement
 * @param redirectTo - Optional custom redirect path for unauthenticated users (defaults to /login)
 */
export function RouteGuard({
  children,
  requiredRole,
  requiredPermission,
  redirectTo = '/login',
}: RouteGuardProps) {
  const router = useRouter();
  const pathname = usePathname();
  const { user, loading, isAuthenticated, permissions } = useAuth();

  useEffect(() => {
    // Wait for auth state to load
    if (loading) return;

    // Requirement 3.4: Redirect unauthenticated users to login
    if (!isAuthenticated) {
      // Store the intended destination for redirect after login
      const returnUrl = pathname !== redirectTo ? pathname : '/dashboard';
      router.push(`${redirectTo}?returnUrl=${encodeURIComponent(returnUrl)}`);
      return;
    }

    // Requirement 3.5: Check role requirement
    if (requiredRole && user?.role !== requiredRole) {
      router.push('/unauthorized');
      return;
    }

    // Requirement 3.5: Check permission requirement
    if (requiredPermission && !permissions.includes(requiredPermission)) {
      router.push('/unauthorized');
      return;
    }
  }, [
    loading,
    isAuthenticated,
    user,
    requiredRole,
    requiredPermission,
    router,
    pathname,
    redirectTo,
    permissions,
  ]);

  // Show loading state while checking authentication
  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center" role="status" aria-live="polite">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin text-primary-600 mx-auto" aria-hidden="true" />
          <span className="sr-only">Loading authentication status...</span>
        </div>
      </div>
    );
  }

  // Don't render content if not authenticated
  if (!isAuthenticated) {
    return null;
  }

  // Don't render content if role requirement not met
  if (requiredRole && user?.role !== requiredRole) {
    return null;
  }

  // Don't render content if permission requirement not met
  if (requiredPermission && !permissions.includes(requiredPermission)) {
    return null;
  }

  // User is authenticated and authorized
  return <>{children}</>;
}
