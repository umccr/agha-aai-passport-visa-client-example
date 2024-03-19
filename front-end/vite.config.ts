import react from "@vitejs/plugin-react";
import { build, defineConfig, UserConfig } from "vite";

// https://vitejs.dev/config/
export default defineConfig((env) => {
  const defaultConfig: UserConfig = {
    build: {
      outDir: "build",
    },
    server: {
      // whilst we won't tend to do dev work via 'vite serve' - if we do then it mind
      // as well run on the same port
      port: 3000,
    },
    plugins: [react()],
  };

  if (env.mode === "development") {
    defaultConfig.build.minify = false;
  }

  return defaultConfig;
});
