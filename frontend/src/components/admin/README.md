# Admin Components

This directory contains administrative components for managing the application.

## FeatureFlagsManager

The `FeatureFlagsManager` component provides a comprehensive interface for managing feature flags.

### Features

- **Display all feature flags**: Shows all available feature flags with their current status
- **Enable/Disable features**: Toggle feature flags on/off with a single click
- **Rollout percentage control**: Set percentage-based rollout for gradual feature deployment
- **Audit logs**: View history of all feature flag changes
- **Export/Import configuration**: Backup and restore feature flag configurations
- **Reset to defaults**: Restore all feature flags to their default state

### Usage

```tsx
import { FeatureFlagsManager } from '@/components/admin/FeatureFlagsManager';

export default function AdminPage() {
  return (
    <div>
      <h1>Admin Panel</h1>
      <FeatureFlagsManager />
    </div>
  );
}
```

### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `className` | `string` | `''` | Additional CSS classes to apply to the component |

### Access Control

The feature flags manager should be protected with RBAC guards to ensure only administrators can access it:

```tsx
import { RBACGuard } from '@/components/auth/RBACGuard';
import { Role } from '@/types/rbac';

<RBACGuard requiredRole={Role.ADMIN}>
  <FeatureFlagsManager />
</RBACGuard>
```

### Page Route

The feature flags manager is available at:
- `/admin/feature-flags` - Dedicated page for feature flag management

### Requirements

This component satisfies requirement 10.3:
- THE Frontend SHALL provide management interface to view and control feature flag status

### Related Components

- `featureFlagsService` - Service for managing feature flags (see `frontend/src/lib/feature-flags.ts`)
- `RBACGuard` - Component for role-based access control
