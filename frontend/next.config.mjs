/** @type {import('next').NextConfig} */
const nextConfig = {
    reactStrictMode: true,
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
    trailingSlash: true,
    experimental: {
        optimizePackageImports: ['@radix-ui/react-icons'],
    },
    // Keep webpack config for compatibility
    webpack: (config, { isServer }) => {
        if (!isServer) {
            config.resolve.fallback = {
                ...config.resolve.fallback,
                fs: false,
                net: false,
                tls: false,
            };
        }
        return config;
    },
};

export default nextConfig;
