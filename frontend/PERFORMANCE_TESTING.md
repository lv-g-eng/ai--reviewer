# Performance Testing Guide

This document describes the performance testing strategy and implementation for the AI-Based Reviewer frontend application.

**Requirements:** 5.9, 10.1, 10.8, 10.9

## Overview

Performance testing ensures that the application meets the documented performance requirements:
- Initial bundle size < 500KB (Requirement 10.8)
- Page load time < 500ms for P95 (Requirement 10.1)
- Lazy loading for heavy components (Requirement 10.9)

## Test Suites

### 1. Bundle Size Tests

Location: `src/__tests__/performance/bundle-size.test.ts`

Tests bundle size optimization and code splitting:

#### Test Cases

1. **Initial Bundle Size**
   - Verifies initial bundle is < 500KB
   - Checks vendor, UI, forms, and common chunks
   - Requirement: 10.8

2. **Lazy-Loaded Visualization Chunks**
   - Verifies visualization libraries are in separate chunks
   - Checks d3, react-force-graph-2d, reactflow are lazy-loaded
   - Requirement: 10.9

3. **Code Splitting**
   - Verifies multiple chunks are created for different routes
   - Checks at least 5 unique chunks exist
   - Requirement: 10.8

4. **Total Bundle Size**
   - Verifies total bundle is < 2MB
   - Reasonable limit for full-featured application

5. **CSS Bundle Size**
   - Verifies CSS is < 200KB
   - Checks Tailwind CSS optimization

6. **No Duplicate Dependencies**
   - Verifies React is not duplicated across chunks
   - Checks code splitting efficiency

#### Running Bundle Size Tests

```bash
# Build the application first
npm run build

# Run bundle size tests
npm test -- bundle-size.test.ts

# View detailed output
npm test -- bundle-size.test.ts --verbose
```

#### Expected Output

```
📦 Initial bundle size: 320.45 KB
📊 Breakdown:
   - vendor.js: 180.23 KB
   - ui.js: 85.12 KB
   - forms.js: 35.67 KB
   - common.js: 19.43 KB

📊 Visualization chunks found: 3
   - visualization.js: 530.21 KB
   - dependency-graph.js: 210.45 KB
   - architecture-graph.js: 165.32 KB

📦 Unique chunks created: 8
   Chunks: vendor, ui, forms, common, visualization, main, webpack, runtime

📦 Total bundle size: 1456.78 KB

🎨 Total CSS size: 145.23 KB
   - main.css: 145.23 KB

⚛️  React found in 2 chunks

✓ initial bundle size should be below 500KB
✓ visualization chunks should be lazy-loaded
✓ code splitting should create separate chunks for different routes
✓ total bundle size should be reasonable
✓ CSS bundle size should be reasonable
✓ no duplicate dependencies in chunks
```

### 2. Page Load Performance Tests

Location: `src/__tests__/performance/page-load.test.tsx`

Tests page rendering performance:

#### Test Cases

1. **Home Page Render Time**
   - Verifies home page renders < 500ms
   - Requirement: 10.1

2. **Login Page Render Time**
   - Verifies login page renders < 500ms
   - Requirement: 10.1

3. **Projects List Page Render Time**
   - Verifies projects page renders < 1000ms
   - Tests with 10 projects

4. **Lazy-Loaded Components**
   - Verifies lazy components don't block initial render
   - Initial render should be < 300ms

5. **Large List Virtualization**
   - Tests rendering 1000 items with virtualization
   - Should render < 1000ms

6. **Form Validation Performance**
   - Tests form with validation renders < 500ms
   - No performance degradation from validation

7. **Navigation Performance**
   - Tests page navigation is < 300ms
   - Client-side routing performance

8. **Image Loading**
   - Verifies lazy-loaded images don't block render
   - Should render < 500ms

9. **Error Boundaries**
   - Tests error boundaries don't impact performance
   - Should render < 500ms

10. **Theme Switching**
    - Tests theme switching is performant
    - Should render < 500ms

#### Running Page Load Tests

```bash
# Run page load tests
npm test -- page-load.test.tsx

# Run with coverage
npm test -- page-load.test.tsx --coverage

# Watch mode for development
npm test -- page-load.test.tsx --watch
```

#### Expected Output

```
🏠 Home page render time: 245.32ms
✓ home page should render within 500ms

🔐 Login page render time: 312.45ms
✓ login page should render within 500ms

📁 Projects page render time: 678.91ms
✓ projects list page should render within 1000ms

⚡ Page with lazy component render time: 156.23ms
✓ lazy-loaded components should not block initial render

📜 Large list render time: 823.45ms
✓ component with large list should use virtualization

📝 Form render time: 289.67ms
✓ form validation should not cause performance issues

🧭 Navigation render time: 178.34ms
✓ navigation between pages should be fast

🖼️  Page with images render time: 234.56ms
✓ image loading should not block page render

🛡️  Page with error boundary render time: 267.89ms
✓ error boundaries should not impact performance

🎨 Themed page render time: 298.12ms
✓ theme switching should be performant
```

## Performance Monitoring

### Browser DevTools

Use Chrome DevTools Performance tab:

1. Open DevTools (F12)
2. Go to Performance tab
3. Click Record
4. Navigate through the application
5. Stop recording
6. Analyze:
   - Loading time
   - Scripting time
   - Rendering time
   - Painting time

### Lighthouse

Run Lighthouse audits:

```bash
# Install Lighthouse CLI
npm install -g lighthouse

# Run audit
lighthouse http://localhost:3000 --view

# Run with specific categories
lighthouse http://localhost:3000 --only-categories=performance --view
```

Target Lighthouse scores:
- Performance: > 90
- Accessibility: > 95
- Best Practices: > 90
- SEO: > 90

### Web Vitals

Monitor Core Web Vitals:

1. **Largest Contentful Paint (LCP)**: < 2.5s
2. **First Input Delay (FID)**: < 100ms
3. **Cumulative Layout Shift (CLS)**: < 0.1

Implement Web Vitals monitoring:

```tsx
import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals';

function sendToAnalytics(metric: any) {
  console.log(metric);
  // Send to analytics service
}

getCLS(sendToAnalytics);
getFID(sendToAnalytics);
getFCP(sendToAnalytics);
getLCP(sendToAnalytics);
getTTFB(sendToAnalytics);
```

## Performance Budgets

Set performance budgets in CI/CD:

```json
{
  "budgets": [
    {
      "resourceSizes": [
        {
          "resourceType": "script",
          "budget": 500
        },
        {
          "resourceType": "style",
          "budget": 200
        },
        {
          "resourceType": "image",
          "budget": 300
        },
        {
          "resourceType": "total",
          "budget": 2000
        }
      ]
    }
  ]
}
```

## Continuous Performance Testing

### CI/CD Integration

Add to GitHub Actions workflow:

```yaml
- name: Build application
  run: npm run build

- name: Run performance tests
  run: npm test -- --testPathPattern=performance

- name: Check bundle size
  run: |
    BUNDLE_SIZE=$(du -sb dist/static | cut -f1)
    MAX_SIZE=$((500 * 1024))
    if [ $BUNDLE_SIZE -gt $MAX_SIZE ]; then
      echo "Bundle size $BUNDLE_SIZE exceeds limit $MAX_SIZE"
      exit 1
    fi

- name: Run Lighthouse CI
  run: |
    npm install -g @lhci/cli
    lhci autorun
```

### Performance Regression Detection

Monitor performance over time:

1. **Baseline Metrics**
   - Record initial performance metrics
   - Store in version control

2. **Regression Thresholds**
   - Alert if bundle size increases > 10%
   - Alert if render time increases > 20%
   - Alert if Lighthouse score drops > 5 points

3. **Automated Alerts**
   - Slack notifications for regressions
   - Block PR merge if performance degrades

## Optimization Techniques

### 1. Code Splitting

Implemented in `next.config.mjs`:

```javascript
splitChunks: {
  cacheGroups: {
    vendor: { /* React, Next.js */ },
    ui: { /* Radix UI, Lucide */ },
    visualization: { /* d3, force-graph */ },
    forms: { /* react-hook-form, zod */ },
    common: { /* shared code */ },
  }
}
```

### 2. Lazy Loading

Use dynamic imports:

```tsx
import dynamic from 'next/dynamic';

const HeavyComponent = dynamic(() => import('./HeavyComponent'), {
  loading: () => <LoadingSpinner />,
  ssr: false,
});
```

### 3. Image Optimization

Use Next.js Image component:

```tsx
import Image from 'next/image';

<Image
  src="/image.jpg"
  alt="Description"
  width={800}
  height={600}
  loading="lazy"
  placeholder="blur"
/>
```

### 4. Tree Shaking

Configure in `next.config.mjs`:

```javascript
webpack: (config) => {
  config.optimization.usedExports = true;
  config.optimization.sideEffects = false;
  return config;
}
```

### 5. Compression

Enable in production:

```javascript
compress: true,
generateEtags: true,
```

## Troubleshooting

### Bundle Size Too Large

1. Analyze bundle with webpack-bundle-analyzer:
   ```bash
   npm install --save-dev @next/bundle-analyzer
   ```

2. Check for:
   - Duplicate dependencies
   - Unused imports
   - Large libraries that can be replaced

### Slow Page Load

1. Check Network tab in DevTools
2. Look for:
   - Blocking resources
   - Large assets
   - Slow API calls
   - Missing caching headers

### Memory Leaks

1. Use Chrome DevTools Memory profiler
2. Check for:
   - Detached DOM nodes
   - Event listeners not cleaned up
   - Timers not cleared
   - WebSocket connections not closed

## Best Practices

1. **Measure First**
   - Always measure before optimizing
   - Use real user data when possible

2. **Optimize Critical Path**
   - Focus on above-the-fold content
   - Defer non-critical resources

3. **Use Production Builds**
   - Always test with production builds
   - Development builds are slower

4. **Monitor Continuously**
   - Set up performance monitoring
   - Track metrics over time

5. **Set Budgets**
   - Define performance budgets
   - Enforce in CI/CD

## Resources

- [Next.js Performance](https://nextjs.org/docs/advanced-features/measuring-performance)
- [Web.dev Performance](https://web.dev/performance/)
- [Chrome DevTools Performance](https://developer.chrome.com/docs/devtools/performance/)
- [Lighthouse](https://developers.google.com/web/tools/lighthouse)
- [Web Vitals](https://web.dev/vitals/)
