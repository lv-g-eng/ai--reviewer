# Feature Flags A/B Testing Guide

This document explains how to use the A/B testing capabilities of the Feature Flags Service.

## Overview

The Feature Flags Service now supports A/B testing with the following capabilities:

1. **User ID-based hash grouping**: Ensures the same user always gets the same variant
2. **Rollout percentage logic**: Control what percentage of users see a feature
3. **A/B testing metrics collection**: Track impressions, interactions, and conversions

## Requirements

- Requirements: 10.5, 10.7
- Design: Section on A/B Testing and Feature Flags

## Basic Usage

### 1. Setting Up an A/B Test

```typescript
import { featureFlagsService } from '@/lib/feature-flags';

// Create a feature flag with A/B test variants
featureFlagsService.setFlag('new-dashboard-design', true);
featureFlagsService.setRolloutPercentage('new-dashboard-design', 50); // 50% of users
featureFlagsService.setABTestVariants('new-dashboard-design', ['control', 'variant-a']);
```

### 2. Getting a User's Variant

```typescript
// In your component
const userId = getCurrentUserId(); // Get from auth context
const variant = featureFlagsService.getABTestVariant('new-dashboard-design', userId);

if (variant === 'control') {
  // Show original dashboard
  return <OriginalDashboard />;
} else if (variant === 'variant-a') {
  // Show new dashboard design
  return <NewDashboard />;
} else {
  // User not in rollout
  return <OriginalDashboard />;
}
```

### 3. Tracking Metrics

```typescript
// Track when user sees the feature (automatically tracked by getABTestVariant)
const variant = featureFlagsService.getABTestVariant('new-dashboard-design', userId);

// Track when user interacts with the feature
function handleDashboardClick() {
  featureFlagsService.trackABTestMetric(
    'new-dashboard-design',
    userId,
    variant!,
    'interaction',
    { action: 'clicked-widget' }
  );
}

// Track when user converts (e.g., completes desired action)
function handleGoalComplete() {
  featureFlagsService.trackABTestMetric(
    'new-dashboard-design',
    userId,
    variant!,
    'conversion',
    { goal: 'completed-onboarding' }
  );
}
```

### 4. Viewing A/B Test Results

```typescript
// Get statistics for an A/B test
const stats = featureFlagsService.getABTestStats('new-dashboard-design');

console.log('Total users:', stats.totalUsers);
console.log('Control group:', stats.variantStats.control);
console.log('Variant A group:', stats.variantStats['variant-a']);

// Example output:
// {
//   flagKey: 'new-dashboard-design',
//   totalUsers: 1000,
//   variantStats: {
//     control: {
//       userCount: 500,
//       impressions: 1500,
//       interactions: 300,
//       conversions: 50
//     },
//     'variant-a': {
//       userCount: 500,
//       impressions: 1600,
//       interactions: 400,
//       conversions: 80
//     }
//   }
// }
```

## Advanced Usage

### Multiple Variants

You can test more than two variants:

```typescript
featureFlagsService.setABTestVariants('pricing-page', [
  'control',
  'variant-a',
  'variant-b',
  'variant-c'
]);

// Users will be evenly distributed across all variants
const variant = featureFlagsService.getABTestVariant('pricing-page', userId);
```

### Gradual Rollout

Start with a small percentage and gradually increase:

```typescript
// Week 1: 10% of users
featureFlagsService.setRolloutPercentage('new-feature', 10);

// Week 2: 25% of users
featureFlagsService.setRolloutPercentage('new-feature', 25);

// Week 3: 50% of users
featureFlagsService.setRolloutPercentage('new-feature', 50);

// Week 4: 100% of users
featureFlagsService.setRolloutPercentage('new-feature', 100);
```

### Custom Metadata

Track additional information with metrics:

```typescript
featureFlagsService.trackABTestMetric(
  'new-feature',
  userId,
  variant,
  'interaction',
  {
    component: 'dashboard',
    action: 'button-click',
    timestamp: Date.now(),
    sessionId: getSessionId(),
    userAgent: navigator.userAgent
  }
);
```

## Key Features

### Consistent Hashing

The service uses a deterministic hash function to ensure:
- The same user always gets the same variant
- Users are evenly distributed across variants
- Changing the rollout percentage doesn't reassign existing users

```typescript
// User 'user-123' will always get the same variant
const variant1 = featureFlagsService.getABTestVariant('feature', 'user-123');
const variant2 = featureFlagsService.getABTestVariant('feature', 'user-123');
// variant1 === variant2 (always true)
```

### Automatic Impression Tracking

When you call `getABTestVariant()`, an impression is automatically tracked:

```typescript
// This automatically tracks an impression
const variant = featureFlagsService.getABTestVariant('feature', userId);

// No need to manually track impression
```

### Local Storage Persistence

All metrics and variant assignments are stored in localStorage:
- Metrics are kept for the last 1000 events
- Variant assignments are cached to ensure consistency
- Data persists across page reloads

### Backend Integration

Metrics are automatically sent to the backend (if available):

```typescript
// Metrics are sent to: POST /api/v1/metrics/ab-test
// Audit logs are sent to: POST /api/v1/audit/feature-flags
```

## Best Practices

### 1. Define Clear Success Metrics

Before starting an A/B test, define what success looks like:

```typescript
// Good: Clear conversion goal
featureFlagsService.trackABTestMetric(
  'checkout-flow',
  userId,
  variant,
  'conversion',
  { goal: 'purchase-completed', revenue: 99.99 }
);
```

### 2. Run Tests Long Enough

Ensure you have enough data before making decisions:

```typescript
const stats = featureFlagsService.getABTestStats('feature');

// Wait until you have at least 100 users per variant
if (stats.variantStats.control.userCount < 100) {
  console.log('Not enough data yet');
}
```

### 3. Track Multiple Event Types

Track the full user journey:

```typescript
// Impression (automatic)
const variant = featureFlagsService.getABTestVariant('feature', userId);

// Interaction
featureFlagsService.trackABTestMetric('feature', userId, variant, 'interaction');

// Conversion
featureFlagsService.trackABTestMetric('feature', userId, variant, 'conversion');
```

### 4. Clean Up After Tests

Once a test is complete, clean up the data:

```typescript
// Clear metrics for a completed test
featureFlagsService.clearABTestMetrics();

// Set winner to 100% rollout
featureFlagsService.setRolloutPercentage('feature', 100);
featureFlagsService.setABTestVariants('feature', []); // Remove variants
```

## Example: Complete A/B Test

Here's a complete example of running an A/B test:

```typescript
import { featureFlagsService } from '@/lib/feature-flags';
import { useAuth } from '@/hooks/useAuth';

function DashboardPage() {
  const { user } = useAuth();
  const userId = user?.id;
  
  // Get variant for this user
  const variant = featureFlagsService.getABTestVariant(
    'new-dashboard-layout',
    userId
  );
  
  // Track interaction when user clicks a button
  const handleButtonClick = () => {
    if (variant) {
      featureFlagsService.trackABTestMetric(
        'new-dashboard-layout',
        userId,
        variant,
        'interaction',
        { action: 'clicked-cta-button' }
      );
    }
    
    // Handle button click logic
    navigateToNextPage();
  };
  
  // Track conversion when user completes goal
  const handleGoalComplete = () => {
    if (variant) {
      featureFlagsService.trackABTestMetric(
        'new-dashboard-layout',
        userId,
        variant,
        'conversion',
        { goal: 'completed-setup' }
      );
    }
  };
  
  // Render appropriate variant
  if (variant === 'variant-a') {
    return <NewDashboardLayout onButtonClick={handleButtonClick} />;
  } else {
    return <OriginalDashboardLayout onButtonClick={handleButtonClick} />;
  }
}
```

## API Reference

### `getABTestVariant(flagKey: string, userId: string): string | null`

Gets the A/B test variant for a specific user. Returns null if the user is not in the rollout or the flag doesn't have variants.

### `trackABTestMetric(flagKey, userId, variant, eventType, metadata?)`

Tracks an A/B test metric event.

- `eventType`: 'impression' | 'interaction' | 'conversion'
- `metadata`: Optional additional data about the event

### `getABTestStats(flagKey: string): ABTestStats | null`

Gets statistics for an A/B test including user counts and event counts per variant.

### `setABTestVariants(flagKey: string, variants: string[])`

Sets the variants for an A/B test. Variants should be an array of strings like `['control', 'variant-a']`.

### `clearABTestMetrics()`

Clears all A/B test metrics and variant assignments. Useful for testing or resetting data.

## Troubleshooting

### Users Not Getting Variants

Check that:
1. The flag is enabled: `featureFlagsService.setFlag('flag-key', true)`
2. Rollout percentage is > 0: `featureFlagsService.setRolloutPercentage('flag-key', 50)`
3. Variants are set: `featureFlagsService.setABTestVariants('flag-key', ['control', 'variant-a'])`

### Metrics Not Being Tracked

Check that:
1. You're calling `trackABTestMetric` with the correct parameters
2. The variant is not null
3. localStorage is available and not full

### Inconsistent Variant Assignment

The service uses consistent hashing, so the same user should always get the same variant. If you're seeing inconsistencies:
1. Check that the userId is consistent across calls
2. Verify that variant assignments are being cached properly
3. Check browser console for errors

## Related Documentation

- [Feature Flags Service](./feature-flags.ts)
- [Feature Flags Manager Component](../components/admin/FeatureFlagsManager.tsx)
- [Production Environment Migration Spec](.kiro/specs/production-environment-migration/)
