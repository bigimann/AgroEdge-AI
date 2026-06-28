import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Produces a self-contained .next/standalone build with only the
  // production deps actually needed at runtime — keeps the Docker image
  // small. No effect on `next dev`.
  output: "standalone",
};

export default nextConfig;
