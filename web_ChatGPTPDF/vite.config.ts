import path from "path";
import type { ConfigEnv, PluginOption } from "vite";
import { defineConfig, loadEnv } from "vite";
import vue from "@vitejs/plugin-vue";
import { VitePWA } from "vite-plugin-pwa";
import CompressionPlugin from 'vite-plugin-compression';

function setupPlugins(env: ImportMetaEnv): PluginOption[] {
  return [
    vue(),
    env.VITE_GLOB_APP_PWA === "true" &&
      VitePWA({
        injectRegister: "auto",
        manifest: {
          name: "chatGPT",
          short_name: "chatGPT",
          icons: [
            { src: "pwa-192x192.png", sizes: "192x192", type: "image/png" },
            { src: "pwa-512x512.png", sizes: "512x512", type: "image/png" },
          ],
        },
      }),
  ];
}

// interface ConfigEnv {
//   [key: string]: string;
// }

export default defineConfig((env: ConfigEnv) => {
  const viteEnv = (loadEnv(
    env.mode,
    process.cwd()
  ) as unknown) as ImportMetaEnv;

  return {
    resolve: {
      alias: {
        "@": path.resolve(process.cwd(), "src"),
      },
    },
    plugins: [
      setupPlugins(viteEnv),
      CompressionPlugin({
        algorithm: "gzip",
        ext: ".gz",
      }),
    ],
    server: {
      host: "0.0.0.0",
      port: 1002,
      open: false,
      proxy: {
        "/api": {
          target: viteEnv.VITE_APP_API_BASE_URL,
          changeOrigin: true, // 允许跨域
          rewrite: (path) => path.replace("/api/", "/"),
        },
      },
    },
    build: {
      // rollupOptions: {
      // 	plugins: [
      // 		// 在生產環境下使用 terser 壓縮代碼
      // 		viteEnv.VITE_NODE_ENV === 'production' && terser(),
      // 	],
      // },
      reportCompressedSize: true,
      sourcemap: false,
      commonjsOptions: {
        ignoreTryCatch: false,
      },
    },
  };
});
