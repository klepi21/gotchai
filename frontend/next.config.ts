import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  transpilePackages: ['@react-pdf/renderer'],
  experimental: {
    esmExternals: 'loose',
  },
  // Silence Turbopack warning for custom webpack config

  webpack: (config) => {
    config.resolve.alias.canvas = false;
    config.resolve.alias.encoding = false;
    return config;
  },
};

export default nextConfig;
