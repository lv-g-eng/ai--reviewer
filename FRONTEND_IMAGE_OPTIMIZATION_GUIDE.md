# Frontend Image Optimization Guide

This guide provides comprehensive strategies for optimizing images in the AI Code Review Platform frontend.

## Optimization Strategies

### 1. Use Next.js Image Optimization

Next.js provides built-in image optimization features that work automatically.

#### Automatic Features

- **Automatic Image Resizing** - Next.js automatically creates optimized versions of images at different sizes
- **WebP Format Conversion** - Converts PNG/JPEG to WebP format for better compression
- **Lazy Loading** - Images load only when they enter the viewport
- **Blur Placeholders** - Automatic blur-up placeholder images

#### Configuration

```javascript
// next.config.js
module.exports = {
  images: {
    formats: ['image/avif', 'image/webp'],
    deviceSizes: [640, 750, 768, 1024, 1200, 1920, 3840],
    imageSizes: [16, 32, 48],
    minimumCacheTTL: 60, // Cache for 60 seconds
  },
};
```

### 2. Optimize Image Formats

#### Use Modern Formats

- **WebP** - Best for photos and images with smooth gradients
- **AVIF** - Best for logos and graphics with transparency
- **SVG** - Best for icons and simple graphics
- **PNG-8** - Good for photos requiring transparency

#### Avoid

- Unnecessary large JPEG/PNG files
- Animated GIFs for static UI elements
- Large BMP files

### 3. Image Size Targets

#### Maximum File Sizes

| Image Type     | Maximum Size |
| -------------- | ------------ |
| Hero Images    | 500 KB       |
| Product Images | 300 KB       |
| Profile Photos | 200 KB       |
| Icons          | 50 KB        |
| Thumbnails     | 50 KB        |

### 4. Image Loading Optimization

#### Lazy Loading

```typescript
import Image from 'next/image';
import { useState } from 'react';

interface OptimizedImageProps {
  src: string;
  alt: string;
  width?: number;
  height?: number;
  priority?: boolean;
  placeholder?: string;
}

export function OptimizedImage({
  src,
  alt,
  width,
  height,
  priority = false,
  placeholder = '/images/placeholder.jpg',
}: OptimizedImageProps) {
  const [isLoaded, setIsLoaded] = useState(false);
  const [isInView, setIsInView] = useState(false);
  const imageRef = useRef<HTMLDivElement>(null);

  // Intersection Observer for lazy loading
  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry], [observerEntry]) => {
        if (entry.isIntersecting) {
          setIsInView(true);
          observer.unobserve(entry.target);
        }
      },
      { threshold: 0.1 }
    );

    if (imageRef.current) {
      observer.observe(imageRef.current);
    }

    return () => {
      observer.disconnect();
    };
  }, [imageRef]);

  const handleLoad = () => {
    setIsLoaded(true);
  };

  return (
    <div
      <img
        ref={imageRef}
        src={isInView ? src : placeholder}
        alt={alt}
        width={width}
        height={height}
        loading="lazy"
        decoding="async"
        onLoad={handleLoad}
        onError={() => setIsInView(true)} // Fallback on error
        className={`transition-opacity duration-300 ${isLoaded ? 'opacity-100' : 'opacity-0'}`}
      />
    </div>
  );
}
```

#### Progressive Loading

```typescript
import Image from 'next/image';

export function ProgressiveImage({
  src,
  alt,
  blur = 20,
}: {
  src: string;
  alt: string;
  blur?: number;
}) {
  return (
    <div style={{ position: 'relative', overflow: 'hidden' }}>
      <Image
        src={src}
        alt={alt}
        placeholder="blur"
        blurDataURL={blur}
        className="transition-opacity duration-300"
      />
    </div>
  );
}
```

### 5. Responsive Images

```typescript
import Image from 'next/image';

interface ResponsiveImageProps {
  src: string;
  alt: string;
  className?: string;
}

export function ResponsiveImage({
  src,
  alt,
  className = '',
}: ResponsiveImageProps) {
  return (
    <picture className={className}>
      {/* Mobile */}
      <source
        media="(max-width: 640px)"
        srcSet={`${src}?w=640 1x, ${src}?w=1200 2x`}
        sizes="640w"
      />
      {/* Tablet */}
      <source
        media="(min-width: 641px) and (max-width: 1024px)"
        srcSet={`${src}?w=750 1x, ${src}?w=1500 2x`}
        sizes="750w"
      />
      {/* Desktop */}
      <source
        media="(min-width: 1025px)"
        srcSet={`${src}?w=1024 1x, ${src}?w=1920 2x`}
        sizes="1024w"
      />
      {/* Fallback */}
      <Image
        src={src}
        alt={alt}
        className="w-full h-auto object-cover"
      />
    </picture>
  );
}
```

### 6. CDN Configuration

#### Using Vercel Image Optimization

Configure Vercel to automatically optimize images:

```javascript
// next.config.js
module.exports = {
  images: {
    domains: ['cdn.yourdomain.com'],
    unoptimized: false,
  },
};
```

#### Using AWS CloudFront Image Optimization

Configure CloudFront to automatically optimize and cache images:

1. Upload original images to S3
2. Configure CloudFront to use Image Optimizer
3. Set up cache policies for images

### 7. Image Processing Workflow

#### Before Deployment

1. **Convert to WebP format** - Best compression ratio
2. **Create multiple sizes** - For responsive images
3. Optimize file size\*\* - Use tools like Squoosh
4. Test image quality\*\* - Maintain visual fidelity

#### Tools

- **Squoosh** - Command-line WebP converter
- **Sharp** - Node.js image processing library
- **ImageMagick** - Advanced image processing

### 8. Best Practices

#### File Naming

```
/images/
  /hero/
    /products/
    /team/
  /icons/

/assets/
  /images/hero-home.jpg
  /images/product-widget.png
```

#### Compression Quality

- **Target**: JPEG quality 80-85
- **Target**: WebP quality 80-90
- **Avoid**: Visible compression artifacts

#### Metadata

Include image dimensions in the filename:

```
/home-banner-1920x600.webp
/product-widget-400x300.webp
/user-profile-200x200.jpg
```

### 9. Performance Monitoring

#### Monitor Image Load Times

```typescript
import { useReportWebVitals } from 'next/web-vitals';

export function reportImageVitals(metricName: string, value: number) {
  // Report image load performance to analytics
  console.log(`[Image Performance] ${metricName}: ${value}ms`);
}

// Use with next/image
import Image from 'next/image';

export function TrackedImage({ src, alt }: { src: string; alt: string }) {
  const handleLoad = () => {
    const perfEntry = performance.getEntriesByName('image')[0];

    if (perfEntry) {
      reportImageVitals('First Contentful Paint', perfEntry.startTime);
      reportImageVitals('Largest Contentful Paint', perfEntry.startTime);
      reportImageVitals('Time to First Byte', perfEntry.startTime);
    }
  };

  return <Image src={src} alt={alt} onLoad={handleLoad} />;
}
```

#### Core Web Vitals

- **LCP (Largest Contentful Paint)**: < 2.5s
- **LIP (Largest Inpaint)**: < 2.5s
- **CLS (Cumulative Layout Shift)**: < 0.1s
- **FID (First Input Delay)**: < 100ms

### 10. Common Issues and Solutions

#### Issue: Slow Image Loading

**Symptoms**:

- Images take long time to load
- Layout shifts while loading
- Poor LCP scores

**Solutions**:

- Implement lazy loading
- Use progressive loading
- Optimize image file sizes
- Enable CDN caching
- Use blur-up placeholders

#### Issue: High Memory Usage

**Symptoms**:

- Memory usage increases when loading images
- Browser tab crashes

**Solutions**:

- Use lazy loading
- Implement virtual scrolling for image lists
- Limit concurrent image loads
- Use responsive images (smaller images on mobile)

#### Issue: Poor Quality After Optimization

**Symptoms**:

- Images appear pixelated
- Colors look washed out
- Text is not readable

**Solutions**:

- Increase quality setting (80-85%)
- Use appropriate format (WebP for photos, AVIF for graphics)
- Test visual quality before deploying
- Avoid over-compression

### 11. Implementation Examples

#### Product Image Card

```typescript
import Image from 'next/image';

interface ProductImageProps {
  product: Product;
  priority?: boolean;
}

export function ProductImage({ product, priority = false }: ProductImageProps) {
  const imageSrc = product.imageUrl;
  const imageAlt = product.name;

  return (
    <Image
      src={imageSrc}
      alt={imageAlt}
      width={400}
      height={300}
      quality={85}
      placeholder={`data:image/svg+xml;charset=utf-8,%3Csvg+xml;base64,${getPlaceholderSVG(400, 300)}`}
      loading="lazy"
      className="object-cover rounded-lg hover:shadow-lg transition-all"
    />
  );
}

function getPlaceholderSVG(width: number, height: number): string {
  const svg = `<svg width="${width}" height="${height}" viewBox="0 0 ${width} ${height}" fill="#f0f0f0" xmlns="http://www.w3.org/2000/svg">
    <rect width="100%" height="100%" fill="%23f0f0" rx="8" ry="8"/>
    <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" fill="%239696">
      Loading...
    </text>
  </svg>`;

  return `data:image/svg+xml;charset=utf-8,${encodeURIComponent(svg)}`;
}
```

#### User Profile Picture

```typescript
import Image from 'next/image';

interface UserProfileImageProps {
  userId: string;
  imageUrl?: string;
  size?: number;
}

export function UserProfileImage({ userId, imageUrl, size = 120 }: UserProfileImageProps) {
  const imageSrc = imageUrl || `/api/users/${userId}/avatar`;
  const imageAlt = `User ${userId} avatar`;

  return (
    <Image
      src={imageSrc}
      alt={imageAlt}
      width={size}
      height={size}
      quality={90}
      placeholder={`data:image/svg+xml;charset=utf-8,%3Csvg+xml;base64,${getCircleSVG(size)}`}
      loading="lazy"
      className="rounded-full object-cover"
      onError={() => console.error(`Failed to load avatar for user ${userId}`)}
    />
  );
}

function getCircleSVG(size: number): string {
  const svg = `<svg width="${size}" height="${size}" viewBox="0 0 ${size} ${size}" fill="%23f0f0" xmlns="http://www.w3.org/2000/svg">
    <circle cx="50%" cy="50%" r="50%" fill="%23f0f0"/>
  </svg>`;

  return `data:image/svg+xml;charset=utf-8,${encodeURIComponent(svg)}`;
}
```

### 12. Testing Checklist

Before deploying image optimizations:

- [ ] Test on mobile devices (iOS Safari, Chrome)
- [ ] Test on desktop browsers (Chrome, Firefox, Edge)
- [ ] Check image quality visually
- [ ] Verify file size targets met
- [ ] Test lazy loading functionality
- [ ] Monitor Core Web Vitals
- [ ] Verify responsive behavior
- [ ] Test fallback placeholders

### 13. Maintenance

#### Regular Tasks

**Daily**:

- Monitor image load times
- Check Core Web Vitals
- Review slow image reports

**Weekly**:

- Analyze image CDN performance
- Optimize frequently requested images
- Review image quality

**Monthly**:

- Audit image usage
- Update optimization strategies
- Train team on best practices

---

**Last Updated**: 2026-03-09
**Version**: 1.0
**Maintainer**: Frontend Team
