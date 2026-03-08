# CDN and Caching Strategy

This document describes the CDN distribution and caching strategies implemented for optimal static asset delivery and performance.

## Overview

The application implements a comprehensive caching strategy with long-term cache headers for static assets and CDN distribution support. This ensures fast asset delivery globally while maintaining cache freshness through content-based hashing.

## Cache Strategy (需求 11.3, 11.5)

### Static Asset Caching

All static assets are configured with aggressive caching policies to maximize performance:

#### Cache Headers Configuration

```javascript
// next.config.mjs
async headers() {
  return [
    {
      source: '/static/:path*',
      headers: [
        {
          key: 'Cache-Control',
          value: 'public, max-age=31536000, immutable',
        },
      ],
    },
    {
      source: '/_next/static/:path*',
      headers: [
        {
          key: 'Cache-Control',
          value: 'public, max-age=31536000, immutable',
        },
      ],
    },
    {
      source: '/_next/image/:path*',
      headers: [
        {
          key: 'Cache-Control',
          value: 'public, max-age=31536000, immutable',
        },
      ],
    },
  ];
}
```

#### Cache Policy Details

- **Duration**: 1 year (31536000 seconds)
- **Visibility**: `public` - can be cached by browsers and CDNs
- **Immutability**: `immutable` - content never changes for this URL
- **Cache Invalidation**: Automatic via content-hash filenames

### Content-Based Hashing

All static assets include content hashes in their filenames:

```
Example filenames:
- main.a1b2c3d4.js
- styles.e5f6g7h8.css
- chunk-vendors.i9j0k1l2.js
```

**Benefits:**
- Enables safe long-term caching
- Automatic cache invalidation when content changes
- No manual cache busting required
- Prevents serving stale assets

### Asset Types and Caching

| Asset Type | Cache Duration | Cache-Control | Notes |
|------------|---------------|---------------|-------|
| JavaScript bundles | 1 year | public, immutable | Content-hashed filenames |
| CSS files | 1 year | public, immutable | Content-hashed filenames |
| Images (optimized) | 1 year | public, immutable | WebP/AVIF with fallback |
| Fonts | 1 year | public, immutable | Preloaded for performance |
| HTML pages | No cache | no-cache | Always fresh from server |
| API responses | Varies | See API caching | Handled by CacheService |

## CDN Configuration (需求 11.3)

### CDN Setup

The application is designed to work seamlessly with any CDN provider (CloudFront, Cloudflare, Fastly, etc.).

#### Environment Configuration

Configure your CDN URL in environment variables:

```bash
# .env.production
NEXT_PUBLIC_CDN_URL=https://cdn.yourdomain.com
```

#### CDN Integration Points

1. **Static Assets**: All `/_next/static/*` assets should be served from CDN
2. **Images**: All `/_next/image/*` optimized images should be served from CDN
3. **Public Files**: All `/static/*` public assets should be served from CDN

### Recommended CDN Configuration

#### CloudFront (AWS)

```yaml
# CloudFront Distribution Settings
Origins:
  - DomainName: your-app.vercel.app
    OriginPath: ""
    CustomHeaders:
      - HeaderName: x-forwarded-host
        HeaderValue: your-domain.com

Behaviors:
  # Static assets - aggressive caching
  - PathPattern: /_next/static/*
    CachePolicyId: 658327ea-f89d-4fab-a63d-7e88639e58f6  # CachingOptimized
    Compress: true
    ViewerProtocolPolicy: redirect-to-https
    
  # Images - aggressive caching
  - PathPattern: /_next/image/*
    CachePolicyId: 658327ea-f89d-4fab-a63d-7e88639e58f6  # CachingOptimized
    Compress: true
    ViewerProtocolPolicy: redirect-to-https
    
  # HTML pages - no caching
  - PathPattern: /*
    CachePolicyId: 4135ea2d-6df8-44a3-9df3-4b5a84be39ad  # CachingDisabled
    Compress: true
    ViewerProtocolPolicy: redirect-to-https
```

#### Cloudflare

```yaml
# Cloudflare Page Rules
Rules:
  # Static assets - cache everything
  - URL: */_next/static/*
    Settings:
      Cache Level: Cache Everything
      Edge Cache TTL: 1 year
      Browser Cache TTL: 1 year
      
  # Images - cache everything
  - URL: */_next/image/*
    Settings:
      Cache Level: Cache Everything
      Edge Cache TTL: 1 year
      Browser Cache TTL: 1 year
      Polish: Lossless
      
  # HTML pages - bypass cache
  - URL: *.html
    Settings:
      Cache Level: Bypass
```

#### Vercel (Built-in CDN)

Vercel automatically configures optimal CDN settings for Next.js applications:

- Static assets are automatically served from global edge network
- Content-hashed files are cached indefinitely
- Images are optimized and cached at the edge
- No additional configuration required

### CDN Best Practices

1. **Enable Compression**: Ensure gzip/brotli compression is enabled at CDN level
2. **HTTP/2 or HTTP/3**: Use modern protocols for multiplexing
3. **Geographic Distribution**: Configure edge locations near your users
4. **Cache Purging**: Set up cache purging for emergency updates
5. **SSL/TLS**: Always use HTTPS for all assets
6. **Monitoring**: Track CDN hit rates and performance metrics

## Critical CSS Inlining (需求 11.5)

### Overview

Critical CSS inlining improves First Contentful Paint (FCP) by embedding above-the-fold styles directly in the HTML, eliminating render-blocking CSS requests.

### Implementation

#### 1. Next.js Built-in Optimization

Next.js automatically optimizes CSS loading:

```javascript
// next.config.mjs
const nextConfig = {
  // Automatic CSS optimization
  optimizeFonts: true,
  optimizeCss: true,
};
```

#### 2. Custom Document with Critical CSS

Create or update `pages/_document.tsx` to inline critical styles:

```typescript
import Document, { Html, Head, Main, NextScript, DocumentContext } from 'next/document';

class MyDocument extends Document {
  static async getInitialProps(ctx: DocumentContext) {
    const initialProps = await Document.getInitialProps(ctx);
    return initialProps;
  }

  render() {
    return (
      <Html lang="en">
        <Head>
          {/* Critical CSS for above-the-fold content */}
          <style
            dangerouslySetInnerHTML={{
              __html: `
                /* Critical styles for initial render */
                body {
                  margin: 0;
                  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
                    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
                    sans-serif;
                  -webkit-font-smoothing: antialiased;
                  -moz-osx-font-smoothing: grayscale;
                }
                
                /* Loading state styles */
                .loading-skeleton {
                  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
                  background-size: 200% 100%;
                  animation: loading 1.5s ease-in-out infinite;
                }
                
                @keyframes loading {
                  0% { background-position: 200% 0; }
                  100% { background-position: -200% 0; }
                }
                
                /* Critical layout styles */
                .container {
                  max-width: 1280px;
                  margin: 0 auto;
                  padding: 0 1rem;
                }
              `,
            }}
          />
          
          {/* Preload critical fonts */}
          <link
            rel="preload"
            href="/fonts/inter-var.woff2"
            as="font"
            type="font/woff2"
            crossOrigin="anonymous"
          />
        </Head>
        <body>
          <Main />
          <NextScript />
        </body>
      </Html>
    );
  }
}

export default MyDocument;
```

#### 3. Automatic CSS Code Splitting

Next.js automatically splits CSS by page:

- Each page loads only its required CSS
- Shared styles are extracted to common chunks
- CSS is loaded asynchronously after critical render

#### 4. Font Optimization

Optimize font loading to prevent layout shift:

```typescript
// app/layout.tsx or pages/_app.tsx
import { Inter } from 'next/font/google';

const inter = Inter({
  subsets: ['latin'],
  display: 'swap', // Use font-display: swap for better performance
  preload: true,
  variable: '--font-inter',
});

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={inter.variable}>
      <body>{children}</body>
    </html>
  );
}
```

### Critical CSS Extraction Tools

For advanced critical CSS extraction, consider these tools:

#### Option 1: Critical (Automated)

```bash
npm install --save-dev critical
```

```javascript
// scripts/extract-critical-css.js
const critical = require('critical');

critical.generate({
  inline: true,
  base: 'out/',
  src: 'index.html',
  target: {
    html: 'index-critical.html',
    css: 'critical.css',
  },
  width: 1300,
  height: 900,
  dimensions: [
    { width: 375, height: 667 },   // Mobile
    { width: 768, height: 1024 },  // Tablet
    { width: 1920, height: 1080 }, // Desktop
  ],
});
```

#### Option 2: Critters (Next.js Plugin)

```bash
npm install --save-dev critters
```

```javascript
// next.config.mjs
import Critters from 'critters-webpack-plugin';

const nextConfig = {
  webpack: (config, { isServer }) => {
    if (!isServer) {
      config.plugins.push(
        new Critters({
          preload: 'swap',
          pruneSource: true,
        })
      );
    }
    return config;
  },
};
```

### Performance Impact

Critical CSS inlining provides:

- **Faster FCP**: Eliminates render-blocking CSS for above-the-fold content
- **Better LCP**: Improves Largest Contentful Paint by rendering content faster
- **Reduced CLS**: Prevents layout shifts from late-loading styles
- **Improved Lighthouse Score**: Typically adds 5-15 points to performance score

### Verification

To verify critical CSS is working:

1. **Chrome DevTools**:
   - Open Network tab
   - Disable cache
   - Reload page
   - Check that initial HTML includes `<style>` tags
   - Verify CSS files load asynchronously

2. **Lighthouse Audit**:
   - Run Lighthouse performance audit
   - Check "Eliminate render-blocking resources" metric
   - Verify FCP and LCP improvements

3. **WebPageTest**:
   - Run test with "First View" and "Repeat View"
   - Compare render timelines
   - Verify faster initial render

## Caching Verification

### Browser Cache Verification

1. Open Chrome DevTools → Network tab
2. Load the page
3. Check response headers for static assets:
   ```
   Cache-Control: public, max-age=31536000, immutable
   ```
4. Reload page - assets should load from disk cache

### CDN Cache Verification

1. Check response headers for CDN-specific headers:
   ```
   X-Cache: HIT from cloudfront
   CF-Cache-Status: HIT
   ```
2. Verify assets are served from CDN domain
3. Check CDN dashboard for cache hit rates

### Performance Testing

```bash
# Test cache headers
curl -I https://yourdomain.com/_next/static/chunks/main.js

# Expected output:
# Cache-Control: public, max-age=31536000, immutable
# Content-Encoding: gzip
# Content-Type: application/javascript
```

## Monitoring and Metrics

### Key Metrics to Track

1. **Cache Hit Rate**: Target >95% for static assets
2. **CDN Bandwidth**: Monitor data transfer costs
3. **Time to First Byte (TTFB)**: Target <200ms from CDN
4. **First Contentful Paint (FCP)**: Target <1.8s
5. **Largest Contentful Paint (LCP)**: Target <2.5s

### Monitoring Tools

- **Vercel Analytics**: Built-in performance monitoring
- **Google Analytics**: Core Web Vitals tracking
- **Sentry**: Performance monitoring and error tracking
- **CDN Dashboard**: Provider-specific metrics

## Troubleshooting

### Assets Not Caching

1. Verify cache headers are present in response
2. Check CDN configuration for cache rules
3. Ensure content-hash filenames are being generated
4. Clear CDN cache and test again

### Stale Assets Being Served

1. Verify content-hash filenames are changing with updates
2. Check if CDN is respecting cache headers
3. Purge CDN cache if necessary
4. Verify build process is generating new hashes

### Critical CSS Not Inlining

1. Check `_document.tsx` is properly configured
2. Verify styles are in `<Head>` component
3. Check build output for inline styles
4. Test with production build (not development)

## Related Documentation

- [Build Optimization](./BUILD_OPTIMIZATION.md) - Build system configuration
- [Resource Compression](./RESOURCE_COMPRESSION.md) - Asset compression strategies
- [Config Service](./src/services/CONFIG_README.md) - Environment configuration

## References

- [Next.js Caching](https://nextjs.org/docs/app/building-your-application/caching)
- [Web.dev: Cache Headers](https://web.dev/http-cache/)
- [Web.dev: Critical CSS](https://web.dev/extract-critical-css/)
- [MDN: Cache-Control](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Cache-Control)
