import { defineConfig } from "vite";

export default defineConfig({
  build: {
    outDir: "app/static/dist",
    emptyOutDir: true,
    rollupOptions: {
      input: {
        // viewer: "app/src/js/viewer.js",
        viewCss: "app/src/css/viewer.css",
      },
      output: {
        entryFileNames: "[name].js",
        chunkFileNames: "[name].js",
        assetFileNames: "[name].[ext]",
      },
    },
  },
});
