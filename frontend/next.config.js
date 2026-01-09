/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: 'export',  // Add this line for static export
  images: {
    unoptimized: true,  // Required for static export
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'https://ai-feedback-backend.onrender.com',
  },
}

module.exports = nextConfig
