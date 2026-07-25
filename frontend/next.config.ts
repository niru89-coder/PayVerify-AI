import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Produces a minimal, self-contained .next/standalone build for Docker.
  output: "standalone",
};

export default nextConfig;
