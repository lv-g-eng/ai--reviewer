/**
 * Feature Flags Admin Page
 * 
 * Admin page for managing feature flags.
 * Accessible only to users with admin role.
 * 
 * Requirements: 10.3
 */

'use client';

import MainLayout from '@/components/layout/main-layout';
import { RBACGuard } from '@/components/auth/RBACGuard';
import { Role } from '@/types/rbac';
import { FeatureFlagsManager } from '@/components/admin/FeatureFlagsManager';
import { Flag } from 'lucide-react';

export default function FeatureFlagsPage() {
  return (
    <RBACGuard requiredRole={Role.ADMIN}>
      <MainLayout>
        <div className="space-y-6">
          {/* Page Header */}
          <div>
            <h1 className="text-3xl font-bold flex items-center gap-3">
              <Flag className="h-8 w-8" />
              Feature Flags
            </h1>
            <p className="text-muted-foreground mt-1">
              Manage feature flags for progressive migration and A/B testing
            </p>
          </div>

          {/* Feature Flags Manager Component */}
          <FeatureFlagsManager />
        </div>
      </MainLayout>
    </RBACGuard>
  );
}
