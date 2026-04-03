import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  images: {
    remotePatterns: [
      { protocol: "https", hostname: "mpesije.jne.gob.pe" },
      { protocol: "https", hostname: "votoinformado.jne.gob.pe" },
    ],
  },
};

export default nextConfig;
