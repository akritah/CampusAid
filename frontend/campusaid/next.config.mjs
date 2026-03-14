/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    return [
      {
        source: '/complaints',
        destination: 'http://localhost:8000/complaints'
      },
      {
        source: '/complaints/voice',
        destination: 'http://localhost:8000/complaints/voice'
      },
      {
        source: '/complaints/:id',
        destination: 'http://localhost:8000/complaints/:id'
      },
      {
        source: '/admin/stats',
        destination: 'http://localhost:8000/admin/stats'
      }
    ];
  }
};

export default nextConfig;
