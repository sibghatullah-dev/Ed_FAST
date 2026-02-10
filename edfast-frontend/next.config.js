/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  images: {
    domains: ['localhost', 'x7mq0j1w-5000.asse.devtunnels.ms'],
  },
  env: {
    API_URL: process.env.API_URL || 'http://localhost:5000/api/v1',
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000/api/v1',
  },
  // Disable SWR validation in production (helps with dev tunnels)
  swrConfig: {
    dedupingInterval: 0,
  },
}

module.exports = nextConfig




