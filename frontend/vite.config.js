import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: "dist", // ✅ ensures Vercel serves the correct folder
  },
  server: {
    port: 5173,
  },
});
