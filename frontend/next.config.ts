import type { NextConfig } from "next";

const nextConfig: NextConfig = {
    /* config options here */
    reactCompiler: true,

    typescript: {
        ignoreBuildErrors: true,
    },

    // Enable standalone output for Docker deployment
    output: "standalone",
    // webpack: (config) => {
    //     config.watchOptions = {
    //         poll: 1000, // check for changes every 1 second
    //         aggregateTimeout: 300,
    //     };
    //     return config;
    // },
};

export default nextConfig;
