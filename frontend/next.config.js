/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: 'export',  // Add this line for static export
  images: {
    unoptimized: true,  // Required for static export
  },
  env: {
    // For static export, this must be set in Render environment variables
    // Set NEXT_PUBLIC_API_URL in Render dashboard to your backend URL
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'https://ai-feedback-system-backend-yashika.onrender.com',
  },
}

module.exports = nextConfig
