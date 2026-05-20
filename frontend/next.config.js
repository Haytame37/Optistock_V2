/** @type {import('next').NextConfig} */
const nextConfig = {
  images: { domains: ["avatars.githubusercontent.com", "github.com"] },
  output: "standalone",
}

module.exports = nextConfig
