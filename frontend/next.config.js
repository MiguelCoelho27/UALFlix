/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "export",

  // Changed done, so the streaming service is technically the one streaming and not catalog
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: "http://nginx/api/:path*", // Proxy to the NGINX service
      },
      {
        source: "/static_videos/:path*",
        destination: "http://nginx/static_videos/:path*", // Also proxy static video paths
      },
    ];
  },
};

module.exports = nextConfig;
