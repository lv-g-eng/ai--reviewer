# LoadingState and OfflineIndicator Components

## Overview

This document describes the LoadingState and OfflineIndicator components, which provide unified loading states and offline status indicators for the application.

## LoadingState Component

### Purpose

The LoadingState component provides a consistent way to display loading states across the application with multiple visual styles.

### Features

- **Multiple Variants**: Spinner, dots, and skeleton screen
- **Customizable Sizes**: Small, medium, and large
- **Optional Text**: Display loading messages
- **Fullscreen Mode**: Cover entire viewport
- **Accessibility**: Proper ARIA attributes for screen readers

### Usage

```tsx
import { LoadingState } from '@/components/LoadingState';

// Basic spinner
<LoadingState />

// With text
<LoadingState text="Loading data..." />

// Dots variant
<LoadingState variant="dots" size="large" />

// Skeleton screen
<LoadingState variant="skeleton" skeletonLines={5} />

// Fullscreen loading
<LoadingState fullscreen text="Please wait..." />

// Custom color
<LoadingState color="#ff6b6b" />
```

### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `variant` | `'spinner' \| 'dots' \| 'skeleton'` | `'spinner'` | Loading animation style |
| `size` | `'small' \| 'medium' \| 'large'` | `'medium'` | Size of the loading indicator |
| `text` | `string` | `undefined` | Optional loading message |
| `fullscreen` | `boolean` | `false` | Cover entire viewport |
| `className` | `string` | `''` | Custom CSS class |
| `color` | `string` | `'#0066cc'` | Color of the loading indicator |
| `skeletonLines` | `number` | `3` | Number of skeleton lines (skeleton variant only) |

### Variants

#### Spinner
A rotating circular spinner, ideal for general loading states.

```tsx
<LoadingState variant="spinner" size="medium" />
```

#### Dots
Three animated dots, suitable for inline loading indicators.

```tsx
<LoadingState variant="dots" size="small" />
```

#### Skeleton
Placeholder content that mimics the structure of the loading content.

```tsx
<LoadingState variant="skeleton" skeletonLines={4} />
```

### Accessibility

The component includes proper ARIA attributes:
- `role="status"`: Indicates a status update
- `aria-live="polite"`: Announces changes to screen readers
- `aria-busy="true"`: Indicates loading state

## OfflineIndicator Component

### Purpose

The OfflineIndicator component monitors network connectivity and displays a banner when the user goes offline, with automatic detection of connection restoration.

### Features

- **Automatic Detection**: Monitors `navigator.onLine` and network events
- **Offline Banner**: Shows when connection is lost
- **Online Notification**: Briefly displays when connection is restored
- **Retry Button**: Allows users to retry or reload
- **Customizable Position**: Top or bottom of viewport
- **Auto-hide**: Online message automatically disappears after a duration

### Usage

```tsx
import { OfflineIndicator } from '@/components/OfflineIndicator';

// Basic usage
<OfflineIndicator />

// Custom messages
<OfflineIndicator 
  offlineMessage="No internet connection"
  onlineMessage="Back online!"
/>

// Bottom position
<OfflineIndicator position="bottom" />

// Custom callbacks
<OfflineIndicator 
  onOffline={() => console.log('Went offline')}
  onOnline={() => console.log('Back online')}
  onRetry={() => window.location.reload()}
/>

// Without retry button
<OfflineIndicator showRetryButton={false} />

// Custom online message duration
<OfflineIndicator onlineMessageDuration={5000} />
```

### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `position` | `'top' \| 'bottom'` | `'top'` | Position of the indicator |
| `offlineMessage` | `string` | `'You are currently offline...'` | Message shown when offline |
| `onlineMessage` | `string` | `'Connection restored'` | Message shown when back online |
| `onlineMessageDuration` | `number` | `3000` | Duration to show online message (ms), 0 = don't hide |
| `className` | `string` | `''` | Custom CSS class |
| `onOffline` | `() => void` | `undefined` | Callback when going offline |
| `onOnline` | `() => void` | `undefined` | Callback when going online |
| `showRetryButton` | `boolean` | `true` | Show retry button when offline |
| `onRetry` | `() => void` | `undefined` | Custom retry handler (default: reload page) |

### Behavior

1. **Initial State**: Component is hidden when online
2. **Going Offline**: Banner appears with offline message and retry button
3. **Going Online**: Banner changes to show online message with checkmark
4. **Auto-hide**: Online message disappears after `onlineMessageDuration` milliseconds
5. **Retry**: Clicking retry button calls `onRetry` or reloads the page

### Accessibility

The component includes proper ARIA attributes:
- `role="alert"`: Indicates important message
- `aria-live="assertive"`: Immediately announces changes to screen readers

### Integration with PWA

The OfflineIndicator works seamlessly with Progressive Web App (PWA) features:

```tsx
import { OfflineIndicator } from '@/components/OfflineIndicator';
import { useServiceWorker } from '@/hooks/useServiceWorker';

function App() {
  const { isOffline, syncPendingData } = useServiceWorker();
  
  return (
    <>
      <OfflineIndicator 
        onOnline={syncPendingData}
        offlineMessage="You're offline. Changes will sync when reconnected."
      />
      {/* Rest of app */}
    </>
  );
}
```

## Best Practices

### LoadingState

1. **Choose the Right Variant**:
   - Use `spinner` for general loading states
   - Use `dots` for inline or compact spaces
   - Use `skeleton` when you know the content structure

2. **Provide Context**:
   - Always include descriptive text for longer operations
   - Keep text concise and action-oriented

3. **Size Appropriately**:
   - Use `small` for inline elements
   - Use `medium` for cards and sections
   - Use `large` for full-page loading

4. **Fullscreen Sparingly**:
   - Only use fullscreen for critical operations
   - Ensure users can't interact with content behind it

### OfflineIndicator

1. **Global Placement**:
   - Place once at the app root level
   - Don't nest multiple indicators

2. **Provide Feedback**:
   - Use callbacks to handle offline/online transitions
   - Queue operations when offline, sync when online

3. **Custom Retry Logic**:
   - Implement smart retry for failed operations
   - Don't just reload the page if you can recover gracefully

4. **User Communication**:
   - Clearly explain what features are unavailable offline
   - Inform users about pending changes that will sync

## Testing

Both components include comprehensive unit tests:

```bash
# Run LoadingState tests
npm test -- --testPathPatterns=LoadingState.test

# Run OfflineIndicator tests
npm test -- --testPathPatterns=OfflineIndicator.test
```

### Test Coverage

- **LoadingState**: 22 tests covering all variants, sizes, and edge cases
- **OfflineIndicator**: 24 tests covering online/offline transitions, callbacks, and UI states

## Requirements Validation

These components satisfy the following requirements:

- **Requirement 12.3**: "WHEN 用户离线时，THE Frontend_Application SHALL 从缓存加载页面并显示离线提示"
  - OfflineIndicator detects offline state and displays appropriate message
  - LoadingState provides consistent loading UI for cached content

## Examples

### Loading Data with Offline Support

```tsx
function DataView() {
  const { data, isLoading, error } = useQuery('data', fetchData);
  const isOnline = useOnlineStatus();
  
  if (isLoading) {
    return <LoadingState text="Loading data..." />;
  }
  
  if (error && !isOnline) {
    return (
      <div>
        <p>Showing cached data (offline)</p>
        <DataDisplay data={data} />
      </div>
    );
  }
  
  return <DataDisplay data={data} />;
}

function App() {
  return (
    <>
      <OfflineIndicator />
      <DataView />
    </>
  );
}
```

### Skeleton Loading for Lists

```tsx
function ProjectList() {
  const { projects, isLoading } = useProjects();
  
  if (isLoading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3, 4, 5].map(i => (
          <LoadingState 
            key={i}
            variant="skeleton" 
            skeletonLines={3}
          />
        ))}
      </div>
    );
  }
  
  return (
    <div>
      {projects.map(project => (
        <ProjectCard key={project.id} project={project} />
      ))}
    </div>
  );
}
```

### Fullscreen Loading for Critical Operations

```tsx
function DeploymentView() {
  const [isDeploying, setIsDeploying] = useState(false);
  
  const handleDeploy = async () => {
    setIsDeploying(true);
    try {
      await deployApplication();
    } finally {
      setIsDeploying(false);
    }
  };
  
  return (
    <>
      {isDeploying && (
        <LoadingState 
          fullscreen
          text="Deploying application... Please do not close this window."
          size="large"
        />
      )}
      <button onClick={handleDeploy}>Deploy</button>
    </>
  );
}
```

## Browser Support

Both components work in all modern browsers:
- Chrome/Edge 90+
- Firefox 88+
- Safari 14+

The OfflineIndicator uses the `navigator.onLine` API and `online`/`offline` events, which are widely supported.

## Performance Considerations

- **LoadingState**: Lightweight animations using CSS, minimal re-renders
- **OfflineIndicator**: Only renders when offline or showing online message, automatic cleanup of event listeners

## Future Enhancements

Potential improvements for future versions:

1. **LoadingState**:
   - Progress bar variant with percentage
   - Custom animation support
   - Themed variants (success, warning, error)

2. **OfflineIndicator**:
   - Network quality indicator (slow connection warning)
   - Pending operations counter
   - Manual dismiss option
   - Toast notification variant
