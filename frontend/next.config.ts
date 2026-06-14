import type { NextConfig } from "next";

// NOTE: next.config.js is the authoritative config (module.exports with NEXT_PUBLIC_API_URL passthrough).
// This file exists for TypeScript type checking only. Next.js will use .js over .ts automatically.
const nextConfig: NextConfig = {
  output: 'standalone',
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },
};

export default nextConfig;
