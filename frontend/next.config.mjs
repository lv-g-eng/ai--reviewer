/** @type {import('next').NextConfig} */
const nextConfig = {
    reactStrictMode: true,
    trailingSlash: true,
    output: 'standalone',
    compress: true,
    generateEtags: true,

    // Compiler optimizations
    compiler: {
        removeConsole: process.env.NODE_ENV === 'production',
        reactRemoveProperties: process.env.NODE_ENV === 'production',
    },

    images: {
        remotePatterns: [
            {
                protocol: 'http',
                hostname: 'localhost',
                port: '3000',
            },
            {
                protocol: 'http',
                hostname: 'localhost',
                port: '8000',
            },
        ],
        formats: ['image/avif', 'image/webp'],
    },

    serverExternalPackages: ['sharp'],
    turbopack: {},

    experimental: {
        optimizePackageImports: [
            '@radix-ui/react-icons',
            'lucide-react',
            'd3',
            'recharts',
            'react-force-graph-2d',
            'reactflow',
            '@radix-ui/react-avatar',
            '@radix-ui/react-checkbox',
            '@radix-ui/react-dialog',
            '@radix-ui/react-dropdown-menu',
            '@radix-ui/react-label',
            '@radix-ui/react-progress',
            '@radix-ui/react-radio-group',
            '@radix-ui/react-scroll-area',
            '@radix-ui/react-select',
            '@radix-ui/react-separator',
            '@radix-ui/react-slot',
            '@radix-ui/react-switch',
            '@radix-ui/react-tabs',
            '@radix-ui/react-toast'
        ],
        esmExternals: true,
    },

    // Code splitting configuration
    modularizeImports: {
        'lucide-react': {
            transform: 'lucide-react/dist/esm/icons/{{kebabCase member}}',
        },
        'd3': {
            transform: 'd3-{{member}}',
        },
    },

    // Webpack configuration
    webpack: (config, { isServer, dev }) => {
        if (!isServer) {
            config.resolve.fallback = {
                ...config.resolve.fallback,
                fs: false,
                net: false,
                tls: false,
            };
        }

        // Tree shaking optimization
        config.optimization.usedExports = true;
        config.optimization.sideEffects = false;

        // Enhanced code splitting
        if (!dev && !isServer) {
            config.optimization.splitChunks = {
                chunks: 'all',
                cacheGroups: {
                    // Vendor chunk for core dependencies
                    vendor: {
                        test: /[\\/]node_modules[\\/](react|react-dom|next)[\\/]/,
                        name: 'vendor',
                        priority: 10,
                        reuseExistingChunk: true,
                    },
                    // UI library chunk
                    ui: {
                        test: /[\\/]node_modules[\\/](@radix-ui|lucide-react|class-variance-authority|clsx|tailwind-merge)[\\/]/,
                        name: 'ui',
                        priority: 9,
                        reuseExistingChunk: true,
                    },
                    // Visualization libraries chunk
                    visualization: {
                        test: /[\\/]node_modules[\\/](d3|react-force-graph-2d|reactflow|recharts)[\\/]/,
                        name: 'visualization',
                        priority: 8,
                        reuseExistingChunk: true,
                    },
                    // Forms and validation chunk
                    forms: {
                        test: /[\\/]node_modules[\\/](react-hook-form|@hookform|zod)[\\/]/,
                        name: 'forms',
                        priority: 7,
                        reuseExistingChunk: true,
                    },
                    // Common chunk for shared code
                    common: {
                        minChunks: 2,
                        priority: 5,
                        reuseExistingChunk: true,
                        name: 'common',
                    },
                },
                maxInitialRequests: 25,
                maxAsyncRequests: 25,
                minSize: 20000,
            };
        }

        return config;
    },
};

export default nextConfig;
