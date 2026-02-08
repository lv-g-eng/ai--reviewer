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

        return config;
    },
};

export default nextConfig;
