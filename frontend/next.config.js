/** @type {import('next').NextConfig} */
const nextConfig = {
    reactStrictMode: true,
    images: {
        minimumCacheTTL: 60,  
    },
    output: 'export',
    assetPrefix: '/aic2024/'
};

module.exports = nextConfig
