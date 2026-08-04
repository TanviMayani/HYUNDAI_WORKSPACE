import { defineConfig } from "vite";
import commonjs from "vite-plugin-commonjs";
import react from '@vitejs/plugin-react'
//import react from "@vitejs/plugin-react-swc";
import svgr from "vite-plugin-svgr";

// https://vitejs.dev/config/
export default defineConfig({
  server: {
    // proxy: {
    //   "/v1/idp": "https://devidpapi.binarysemantics.com/v1/idp",
    // } ,
    watch: {
      usePolling: true,
    },
    host: true,
    strictPort: true,
    port: 7007,
  },
  preview: {
    host: '0.0.0.0',
    port: 7007,
  },
  plugins: [
    react(),
    svgr(),
  ],
  define: {
    global: {},
},
  // resolve: {
  //   alias: {
  //     "@": fileURLToPath(new URL("./src", import.meta.url)),
  //   },
  // },
});
