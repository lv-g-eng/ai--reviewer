# CDN Deployment Quick Start Guide

This guide provides step-by-step instructions for deploying the application with CDN support.

## Prerequisites

- Production build completed (`npm run build`)
- Hosting platform account (Vercel, AWS, Cloudflare, etc.)
- Domain name configured (optional but recommended)

## Deployment Options

### Option 1: Vercel (Recommended - Zero Configuration)

Vercel provides built-in CDN with optimal Next.js configuration.

#### Steps:

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Deploy**
   ```bash
   cd frontend
   vercel
   ```

3. **Configure Environment Variables**
   - Go to Vercel Dashboard → Project Settings → Environment Variables
   - Add production environment variables from `.env.production.example`

4. **Verify Deployment**
   ```bash
   # Check cache headers
   curl -I https://your-app.vercel.app/_next/static/chunks/main.js
   
   # Expected: Cache-Control: public, max-age=31536000, immutable
   ```

**Benefits:**
- Automatic CDN configuration
- Global edge network
- Automatic HTTPS
- Zero configuration required

---

### Option 2: AWS CloudFront + S3

Deploy static assets to S3 and serve through CloudFront CDN.

#### Steps:

1. **Build the Application**
   ```bash
   npm run build
   ```

2. **Create S3 Bucket**
   ```bash
   aws s3 mb s3://your-app-static-assets
   ```

3. **Upload Static Assets**
   ```bash
   # Upload Next.js static files
   aws s3 sync .next/static s3://your-app-static-assets/_next/static \
     --cache-control "public, max-age=31536000, immutable"
   
   # Upload public files
   aws s3 sync public s3://your-app-static-assets/static \
     --cache-control "public, max-age=31536000, immutable"
   ```

4. **Create CloudFront Distribution**
   ```bash
   aws cloudfront create-distribution \
     --origin-domain-name your-app-static-assets.s3.amazonaws.com \
     --default-root-object index.html
   ```

5. **Configure CloudFront Behaviors**
   - Path: `/_next/static/*` → Cache Policy: CachingOptimized
   - Path: `/static/*` → Cache Policy: CachingOptimized
   - Path: `/*` → Cache Policy: CachingDisabled (for HTML)

6. **Update Environment Variables**
   ```bash
   # .env.production
   NEXT_PUBLIC_CDN_URL=https://d1234567890.cloudfront.net
   ```

7. **Deploy Application Server**
   - Deploy Next.js server to EC2, ECS, or Lambda
   - Configure to serve HTML and API routes
   - Static assets will be served from CloudFront

**CloudFormation Template Example:**

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Resources:
  StaticAssetsBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: your-app-static-assets
      PublicAccessBlockConfiguration:
        BlockPublicAcls: false
        BlockPublicPolicy: false
        IgnorePublicAcls: false
        RestrictPublicBuckets: false

  CloudFrontDistribution:
    Type: AWS::CloudFront::Distribution
    Properties:
      DistributionConfig:
        Enabled: true
        Origins:
          - Id: S3Origin
            DomainName: !GetAtt StaticAssetsBucket.DomainName
            S3OriginConfig:
              OriginAccessIdentity: ''
        DefaultCacheBehavior:
          TargetOriginId: S3Origin
          ViewerProtocolPolicy: redirect-to-https
          CachePolicyId: 658327ea-f89d-4fab-a63d-7e88639e58f6
          Compress: true
```

---

### Option 3: Cloudflare Pages

Deploy to Cloudflare Pages with automatic CDN.

#### Steps:

1. **Connect Repository**
   - Go to Cloudflare Dashboard → Pages
   - Connect your Git repository

2. **Configure Build Settings**
   ```
   Build command: npm run build
   Build output directory: .next
   Root directory: frontend
   ```

3. **Set Environment Variables**
   - Add all variables from `.env.production.example`

4. **Configure Page Rules** (Optional)
   - Rule 1: `*/_next/static/*` → Cache Everything, Edge TTL: 1 year
   - Rule 2: `*/static/*` → Cache Everything, Edge TTL: 1 year

5. **Deploy**
   - Push to main branch
   - Cloudflare automatically builds and deploys

**Benefits:**
- Free tier available
- Global CDN included
- Automatic HTTPS
- DDoS protection

---

### Option 4: Netlify

Deploy to Netlify with built-in CDN.

#### Steps:

1. **Install Netlify CLI**
   ```bash
   npm install -g netlify-cli
   ```

2. **Build and Deploy**
   ```bash
   cd frontend
   npm run build
   netlify deploy --prod
   ```

3. **Configure Headers** (netlify.toml)
   ```toml
   [[headers]]
     for = "/_next/static/*"
     [headers.values]
       Cache-Control = "public, max-age=31536000, immutable"
   
   [[headers]]
     for = "/static/*"
     [headers.values]
       Cache-Control = "public, max-age=31536000, immutable"
   ```

4. **Set Environment Variables**
   - Go to Site Settings → Environment Variables
   - Add production variables

---

## Post-Deployment Verification

### 1. Verify Cache Headers

```bash
# Check static assets
curl -I https://your-domain.com/_next/static/chunks/main.js

# Expected headers:
# Cache-Control: public, max-age=31536000, immutable
# Content-Encoding: gzip or br
# X-Cache: HIT (from CDN)
```

### 2. Test CDN Hit Rate

```bash
# First request (MISS)
curl -I https://your-domain.com/_next/static/chunks/main.js | grep -i cache

# Second request (HIT)
curl -I https://your-domain.com/_next/static/chunks/main.js | grep -i cache
```

### 3. Verify Critical CSS

```bash
# Check HTML source
curl https://your-domain.com | grep -A 20 "<style"

# Should see inline critical CSS in <head>
```

### 4. Run Lighthouse Audit

```bash
# Install Lighthouse CLI
npm install -g lighthouse

# Run audit
lighthouse https://your-domain.com --view

# Check for:
# - Performance score >= 90
# - "Eliminate render-blocking resources" passed
# - "Serve static assets with efficient cache policy" passed
```

### 5. Test from Multiple Locations

Use tools to test CDN performance globally:
- [WebPageTest](https://www.webpagetest.org/)
- [GTmetrix](https://gtmetrix.com/)
- [Pingdom](https://tools.pingdom.com/)

---

## Performance Monitoring

### Set Up Monitoring

1. **Vercel Analytics** (if using Vercel)
   - Automatically enabled
   - View in Vercel Dashboard

2. **Google Analytics 4**
   ```typescript
   // Add to layout.tsx
   import Script from 'next/script';
   
   <Script
     src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"
     strategy="afterInteractive"
   />
   ```

3. **Sentry Performance Monitoring**
   ```typescript
   // Already configured in ErrorMonitor service
   // Tracks Core Web Vitals automatically
   ```

### Key Metrics to Monitor

- **Cache Hit Rate**: Target >95%
- **TTFB**: Target <200ms
- **FCP**: Target <1.8s
- **LCP**: Target <2.5s
- **CLS**: Target <0.1
- **CDN Bandwidth**: Monitor costs

---

## Troubleshooting

### Issue: Assets Not Caching

**Solution:**
1. Verify cache headers in response
2. Check CDN configuration
3. Clear CDN cache
4. Verify content-hash filenames

### Issue: Stale Assets After Deployment

**Solution:**
1. Verify new content hashes generated
2. Purge CDN cache
3. Check build process

### Issue: Slow Initial Load

**Solution:**
1. Verify critical CSS is inlined
2. Check font loading strategy
3. Run Lighthouse audit
4. Optimize images

### Issue: High CDN Costs

**Solution:**
1. Verify cache hit rate is high
2. Check for cache misses
3. Optimize asset sizes
4. Consider compression settings

---

## CDN Configuration Checklist

- [ ] Production build completed
- [ ] Cache headers configured (1 year, immutable)
- [ ] Content-hash filenames enabled
- [ ] Critical CSS inlined
- [ ] Fonts optimized (display: swap)
- [ ] Images optimized (WebP/AVIF)
- [ ] Compression enabled (gzip/brotli)
- [ ] CDN distribution created
- [ ] Environment variables configured
- [ ] HTTPS enabled
- [ ] Cache headers verified in production
- [ ] Lighthouse audit passed (score >= 90)
- [ ] Monitoring configured

---

## Additional Resources

- [Next.js Deployment Documentation](https://nextjs.org/docs/deployment)
- [Vercel Documentation](https://vercel.com/docs)
- [AWS CloudFront Documentation](https://docs.aws.amazon.com/cloudfront/)
- [Cloudflare Pages Documentation](https://developers.cloudflare.com/pages/)
- [Web.dev: Fast Load Times](https://web.dev/fast/)

---

## Support

For issues or questions:
1. Check [CDN_AND_CACHING.md](./CDN_AND_CACHING.md) for detailed configuration
2. Run `npm run cdn:verify` to verify local configuration
3. Review deployment platform documentation
4. Check application logs for errors
