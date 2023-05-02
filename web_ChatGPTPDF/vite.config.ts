import path from "path";
import type { ConfigEnv, PluginOption } from "vite";
import { defineConfig, loadEnv } from "vite";
import vue from "@vitejs/plugin-vue";
import { VitePWA } from "vite-plugin-pwa";
import CompressionPlugin from "vite-plugin-compression";
import visualizer from "rollup-plugin-visualizer";
import externalGlobals from "rollup-plugin-external-globals";

let globals = externalGlobals({
  vue: "Vue",
  "vue-demi": "VueDemi",
  axios: "axios",
  "vue-i18n": "VueI18n",
  "vue-router": "VueRouter",
  //"naive-ui": "naive-ui",
  lodash: "_",
  //pinia: "pinia",
  html2canvas: "html2canvas",
  katex: "katex",
  "pdfjs-dist": "pdfjsLib",
  "highlight.js": "highlight.js",
  //"markdown-it": "markdown-it",
  "crypto-js": "crypto-js",
});

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

// function setupPlugins(env: ImportMetaEnv): PluginOption[] {
//   return [
//     vue(),
//     env.VITE_GLOB_APP_PWA === "true" &&
//       VitePWA({
//         injectRegister: "auto",
//         manifest: {
//           name: "chatGPT",
//           short_name: "chatGPT",
//           icons: [
//             { src: "pwa-192x192.png", sizes: "192x192", type: "image/png" },
//             { src: "pwa-512x512.png", sizes: "512x512", type: "image/png" },
//           ],
//         },
//       }),
//   ];
// }

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
      visualizer() as PluginOption,
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
          target: viteEnv.VITE_API_BASE_URL,
          changeOrigin: true, // 允许跨域
          //rewrite: (path) => path.replace("/api/", "/"),
        },
      },
    },
    build: {
      rollupOptions: {
        // 忽略打包
        external: [
          "vue",
          "vue-demi",
          "axios",
          "vue-i18n",
          //"pinia",
          "vue-router",
          //"naive-ui",
          "lodash",
          "html2canvas",
          "katex",
          "pdfjs-dist",
          "highlight.js",
					"crypto-js",
					//"markdown-it"
        ],
        plugins: [globals as PluginOption],
      },

      reportCompressedSize: true,
      sourcemap: false,
      commonjsOptions: {
        ignoreTryCatch: false,
      },
    },
  };
});
