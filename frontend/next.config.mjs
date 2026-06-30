/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  env: {
    AGENT_URL: process.env.AGENT_URL || "http://localhost:7000",
  },
};

export default nextConfig;
