/**
 * RBAC Usage Examples
 * Demonstrates how to use RBAC components and hooks
 */
'use client';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { RBACGuard } from '@/components/auth/RBACGuard';
import { PermissionCheck } from '@/components/auth/PermissionCheck';
import { useRole } from '@/hooks/useRole';
import { usePermission } from '@/hooks/usePermission';
import { Role, Permission } from '@/types/rbac';
import { Shield, Edit, Trash2, Eye, Settings } from 'lucide-react';

/**
 * Example 1: Page-level protection with RBACGuard
 */
export function AdminOnlyPage() {
  return (
    <RBACGuard requiredRole={Role.ADMIN}>
      <div className="p-6">
        <h1 className="text-2xl font-bold">Admin Dashboard</h1>
        <p>This content is only visible to administrators.</p>
      </div>
    </RBACGuard>
  );
}

/**
 * Example 2: Permission-based page protection
 */
export function SettingsPage() {
  return (
    <RBACGuard requiredPermission={Permission.MODIFY_CONFIG}>
      <div className="p-6">
        <h1 className="text-2xl font-bold">System Settings</h1>
        <p>Only users with MODIFY_CONFIG permission can see this.</p>
      </div>
    </RBACGuard>
  );
}

/**
 * Example 3: Conditional UI rendering with PermissionCheck
 */
export function ProjectCard({ projectId }: { projectId: string }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Project Name</CardTitle>
        <CardDescription>Project description goes here</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="flex gap-2">
          {/* View button - visible to all users with VIEW_PROJECTS */}
          <PermissionCheck permission={Permission.VIEW_PROJECTS}>
            <Button variant="outline" size="sm">
              <Eye className="h-4 w-4 mr-2" />
              View
            </Button>
          </PermissionCheck>

          {/* Edit button - only for users with MODIFY_PROJECT */}
          <PermissionCheck permission={Permission.MODIFY_PROJECT}>
            <Button variant="outline" size="sm">
              <Edit className="h-4 w-4 mr-2" />
              Edit
            </Button>
          </PermissionCheck>

          {/* Delete button - only for users with DELETE_PROJECT */}
          <PermissionCheck permission={Permission.DELETE_PROJECT}>
            <Button variant="destructive" size="sm">
              <Trash2 className="h-4 w-4 mr-2" />
              Delete
            </Button>
          </PermissionCheck>
        </div>
      </CardContent>
    </Card>
  );
}

/**
 * Example 4: Using hooks for complex logic
 */
export function DynamicContent() {
  const { hasRole, currentRole, loading } = useRole();
  const { hasPermission } = usePermission();

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>Your Role: {currentRole}</CardTitle>
        </CardHeader>
        <CardContent>
          {hasRole(Role.ADMIN) && (
            <div className="p-4 bg-red-50 rounded">
              <Shield className="h-5 w-5 text-red-600 mb-2" />
              <p className="font-semibold">Administrator Access</p>
              <p className="text-sm text-gray-600">You have full system access.</p>
            </div>
          )}

          {hasRole(Role.PROGRAMMER) && (
            <div className="p-4 bg-blue-50 rounded">
              <Edit className="h-5 w-5 text-blue-600 mb-2" />
              <p className="font-semibold">Programmer Access</p>
              <p className="text-sm text-gray-600">You can create and manage projects.</p>
            </div>
          )}

          {hasRole(Role.VISITOR) && (
            <div className="p-4 bg-gray-50 rounded">
              <Eye className="h-5 w-5 text-gray-600 mb-2" />
              <p className="font-semibold">Visitor Access</p>
              <p className="text-sm text-gray-600">You have read-only access.</p>
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Available Actions</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          {hasPermission(Permission.CREATE_PROJECT) && (
            <Button className="w-full">Create New Project</Button>
          )}
          
          {hasPermission(Permission.MODIFY_CONFIG) && (
            <Button variant="outline" className="w-full">
              <Settings className="h-4 w-4 mr-2" />
              System Settings
            </Button>
          )}
          
          {!hasPermission(Permission.CREATE_PROJECT) && (
            <p className="text-sm text-gray-500">
              You don't have permission to create projects.
            </p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

/**
 * Example 5: Role-based navigation menu
 */
export function NavigationMenu() {
  const { hasRole } = useRole();
  const { hasPermission } = usePermission();

  return (
    <nav className="space-y-2">
      {/* Always visible */}
      <Button variant="ghost" className="w-full justify-start">
        Dashboard
      </Button>

      {/* Visible to users with VIEW_PROJECTS permission */}
      <PermissionCheck permission={Permission.VIEW_PROJECTS}>
        <Button variant="ghost" className="w-full justify-start">
          Projects
        </Button>
      </PermissionCheck>

      {/* Visible to users with VIEW_REVIEWS permission */}
      <PermissionCheck permission={Permission.VIEW_REVIEWS}>
        <Button variant="ghost" className="w-full justify-start">
          Reviews
        </Button>
      </PermissionCheck>

      {/* Admin-only menu items */}
      <PermissionCheck role={Role.ADMIN}>
        <div className="border-t pt-2 mt-2">
          <p className="text-xs font-semibold text-gray-500 px-3 mb-2">ADMIN</p>
          <Button variant="ghost" className="w-full justify-start">
            User Management
          </Button>
          <Button variant="ghost" className="w-full justify-start">
            Audit Logs
          </Button>
        </div>
      </PermissionCheck>

      {/* Settings - only for users with MODIFY_CONFIG */}
      <PermissionCheck permission={Permission.MODIFY_CONFIG}>
        <Button variant="ghost" className="w-full justify-start">
          <Settings className="h-4 w-4 mr-2" />
          Settings
        </Button>
      </PermissionCheck>
    </nav>
  );
}

/**
 * Example 6: Fallback content
 */
export function RestrictedSection() {
  return (
    <PermissionCheck
      permission={Permission.DELETE_PROJECT}
      fallback={
        <Card className="border-yellow-200 bg-yellow-50">
          <CardContent className="pt-6">
            <p className="text-sm text-yellow-800">
              You don't have permission to delete projects. Contact your administrator for access.
            </p>
          </CardContent>
        </Card>
      }
    >
      <Card className="border-red-200">
        <CardHeader>
          <CardTitle className="text-red-600">Danger Zone</CardTitle>
          <CardDescription>
            Irreversible actions that require elevated permissions
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Button variant="destructive">
            <Trash2 className="h-4 w-4 mr-2" />
            Delete Project
          </Button>
        </CardContent>
      </Card>
    </PermissionCheck>
  );
}

/**
 * Example 7: Multiple permission checks
 */
export function UserManagementTable() {
  return (
    <div className="space-y-4">
      {/* Create user button */}
      <PermissionCheck permission={Permission.CREATE_USER}>
        <Button>
          <Plus className="h-4 w-4 mr-2" />
          Add User
        </Button>
      </PermissionCheck>

      {/* User table */}
      <table className="w-full">
        <thead>
          <tr>
            <th>Name</th>
            <th>Email</th>
            <th>Role</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>John Doe</td>
            <td>john@example.com</td>
            <td>Programmer</td>
            <td className="flex gap-2">
              {/* Edit button - only for users with MODIFY_USER */}
              <PermissionCheck permission={Permission.MODIFY_USER}>
                <Button variant="ghost" size="sm">
                  <Edit className="h-4 w-4" />
                </Button>
              </PermissionCheck>

              {/* Delete button - only for users with DELETE_USER */}
              <PermissionCheck permission={Permission.DELETE_USER}>
                <Button variant="ghost" size="sm">
                  <Trash2 className="h-4 w-4" />
                </Button>
              </PermissionCheck>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  );
}

function Plus(props: any) {
  return <svg {...props} />;
}
